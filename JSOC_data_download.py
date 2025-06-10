from sunpy.net import Fido, attrs as a
from astropy import units as u

# print(a.jsoc.Series) ## Prints all the available attributes 
## the names of the various data series
#
# print(a.Instrument) ## Names of all the instrument available
# 

time = a.Time('2021-10-28T15:30:25','2021-10-28T16:00:25') # Time of observation
wv = a.Wavelength(1600*u.angstrom) # Wavelength of observation
ser = a.jsoc.Series('aia.lev1_uv_24s') # The specific data series to be searched.
## You will find the list in (a.jsoc.Series)
notify_flag = a.jsoc.Notify('soumyaroy@iucaa.in') ## The account used to fetch the data

fdir = '/Users/soumyaroy/Downloads/' ## Path where the data needs to be downloaded

res = Fido.search(time, ser, wv, notify_flag) ## Compiles the list of files

# print(res) ## Prints the details of the files found


########### Download the data ####################


download = Fido.fetch(res,path=fdir,)

## $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ ##


while(len(download.errors)>0):
    download = Fido.fetch(download,path=fdir,)

# CAUTION!!CAUTION!! 
# 
# This step is only useful if there are errors in the download
# e.g. partial files or full error and you want to restart the  
# download immidiately. There is a slight chance that you are 
# stuck in an infinite loop and have to kill the kernel!!
# 
# I should really add a break counter !!

## $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ ##


###################################################