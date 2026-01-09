from astropy.io import fits
import requests
import os, gzip, re
import glob

def fix_suvi_l1b_header(in_filename):
    # Read the file manually as bytes until we hit a UnicodeDecodeError, i.e.
    # until we reach the data part. Since astropy version 4.2.1, we can't use
    # the .to_string() method anymore because of FITS header consistency checks
    # that cannot be overridden. 
    header = ''
    with open(in_filename, 'rb') as in_file:
        counter = 1
        while True:
            try:
                this_line = in_file.read(counter)
                this_str = this_line.decode("utf-8")
                header += this_str
                counter += 1
            except UnicodeDecodeError:
                break
    in_file.close()
    hdr_list = [header[i:i+80] for i in range(0, len(header), 80)]

    # Remove all the empty entries
    while(" "*80 in hdr_list) : 
        hdr_list.remove(" "*80) 

    # Make a new string list where we put all the information together correctly
    hdr_list_new = []
    for count, item in enumerate(hdr_list):
        if count <= len(hdr_list)-2:
            if hdr_list[count][0:8] != 'CONTINUE' and hdr_list[count+1][0:8] != 'CONTINUE':
                hdr_list_new.append(hdr_list[count])
            else:
                if hdr_list[count][0:8] != 'CONTINUE' and hdr_list[count+1][0:8] == 'CONTINUE':
                    ampersand_pos = hdr_list[count].find('&')
                    if ampersand_pos != -1:
                        new_entry = hdr_list[count][0:ampersand_pos]
                    else:
                        # Raise exception here because there should be an ampersand at the end of a CONTINUE'd keyword
                        raise Exception("There should be an ampersand at the end of a CONTINUE'd keyword.")
                
                    tmp_count = 1
                    while hdr_list[count+tmp_count][0:8] == 'CONTINUE':
                        ampersand_pos = hdr_list[count+tmp_count].find('&')
                        if ampersand_pos != -1:
                            first_sq_pos = hdr_list[count+tmp_count].find("'")
                            if first_sq_pos != -1:
                                new_entry = new_entry+hdr_list[count+tmp_count][first_sq_pos+1:ampersand_pos]
                            else:
                                # Raise exception here because there should be a single quote after CONTINUE
                                raise Exception("There should be two single quotes after CONTINUE. Did not find any.")
                        
                        else:
                            # If there is no ampersand at the end anymore, it means the entry ends here.
                            # Read from the first to the second single quote in this case.
                            first_sq_pos = hdr_list[count+tmp_count].find("'")
                            if first_sq_pos != -1:
                                second_sq_pos = hdr_list[count+tmp_count][first_sq_pos+1:].find("'")
                                if second_sq_pos != -1:
                                    new_entry = new_entry+hdr_list[count+tmp_count][first_sq_pos+1:second_sq_pos+1+first_sq_pos].rstrip()+"'"
                                else:
                                    # Raise exception here because there should be a second single quote after CONTINUE
                                    raise Exception("There should be two single quotes after CONTINUE. Found the first, but not the second.")
                                
                            else:
                                # Raise exception here because there should be a (first) single quote after CONTINUE
                                raise Exception("There should be two single quotes after CONTINUE. Did not find any.")

                        tmp_count += 1
                        
                    hdr_list_new.append(new_entry)
            
                else:
                    continue

        else:
            # Add END at the end of the header
            hdr_list_new.append(hdr_list[count])

    # Now we stitch together the CONTINUE information correctly,
    # with a "\n" at the end that we use as a separator later on
    # when we convert from a string to an astropy header.
    for count, item in enumerate(hdr_list_new):
        if len(item) > 80:
            this_entry = item[0:78]+"&'\n"
            rest       = "CONTINUE  '"+item[78:]
            while len(rest) > 80:
                this_entry = this_entry + rest[0:78] + "&'\n"
                rest       = "CONTINUE  '"+ rest[78:]
            this_entry = this_entry + rest
            hdr_list_new[count] = this_entry
    
    # Now we should have the correct list of strings. Since we can't convert a list to a
    # fits header directly, we have to convert it to a string first, separated by "\n".
    hdr_str_new = '\n'.join([str(item) for item in hdr_list_new]) 

    # And finally we create the new corrected astropy fits header from that string
    hdr_corr = fits.Header.fromstring(hdr_str_new, sep='\n')

    # Return the corrected header
    return hdr_corr