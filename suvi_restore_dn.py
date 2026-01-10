from dataclasses import dataclass
import numpy as np

@dataclass
class SuviIndex:
    wavelnth: int
    filter1: str
    filter2: str
    ccd_tmp1: float
def suvi_index_from_map(suvi_map):
    """
    Construct a SUVI index object from a SunPy Map or FITS header.
    """

    # --- Get header safely ---
    if hasattr(suvi_map, "meta"):
        hdr = suvi_map.meta
    elif hasattr(suvi_map, "header"):
        hdr = suvi_map.header
    else:
        raise TypeError("Input must be SunPy Map or FITS HDU/Header")

    # --- Wavelength ---
    if "WAVELNTH" in hdr:
        wvln = int(hdr["WAVELNTH"])
    elif "WAVELENGTH" in hdr:
        wvln = int(hdr["WAVELENGTH"])
    else:
        raise KeyError("No wavelength keyword found in header")

    # --- Filters ---
    try:
        fw1 = hdr["FILTER1"].strip()
        fw2 = hdr["FILTER2"].strip()
    except KeyError as e:
        raise KeyError(f"Missing filter keyword: {e}")

    # --- CCD temperature ---
    if "CCD_TMP1" in hdr:
        ccd_tmp = float(hdr["CCD_TMP1"])
    else:
        raise KeyError("CCD_TMP1 missing from header")

    return SuviIndex(
        wavelnth=wvln,
        filter1=fw1,
        filter2=fw2,
        ccd_tmp1=ccd_tmp
    )


def suvi_approx_response(wvln, fw1, fw2, ccd_temp):
    """
    Python translation of IDL suvi_approx_response.pro

    Parameters
    ----------
    wvln : int or str
        Wavelength (e.g. 171 or '171 A')
    fw1 : str
        Filter wheel 1 name: 'Open', 'Thin_Al', 'Thin_Zr', 'Thick_Zr', 'Thick_Al'
    fw2 : str
        Filter wheel 2 name: 'Glass', 'Open', 'Thin_Al', 'Thin_Zr', 'Thick_Al'
    ccd_temp : float
        CCD temperature in deg C

    Returns
    -------
    response : ndarray, shape (5,)
        [response, eff_area, quantum_yield, photon_energy, ccd_gain]
    """

    # --- Wavelength handling (IDL var_type logic) ---
    if isinstance(wvln, str):
        wvlns = ['94 A', '131 A', '171 A', '195 A', '284 A', '304 A']
    else:
        wvlns = [94, 131, 171, 195, 284, 304]

    fw1_names = ['Open', 'Thin_Al', 'Thin_Zr', 'Thick_Zr', 'Thick_Al']
    fw2_names = ['Glass', 'Open', 'Thin_Al', 'Thin_Zr', 'Thick_Al']

    # --- Constants ---
    geom_area = 0.001936            # m^2
    solid_angle = 1.46903e-10       # sr

    m1_reflectivity = np.array([0.3249, 0.6615, 0.4833, 0.3615, 0.2415, 0.2264])
    m2_reflectivity = np.array([0.2452, 0.6171, 0.4459, 0.3302, 0.2193, 0.2103])
    ent_trans = np.array([0.3655, 0.3289, 0.5392, 0.5323, 0.3907, 0.3645])

    fw1_trans = np.array([
        [1.0, 5.951421e-03, 3.67894e-01, 2.64501197e-01, 4.31837e-04],
        [1.0, 8.200625e-03, 3.30119966e-01, 2.35383536e-01, 7.26064e-04],
        [1.0, 5.34282080e-01, 1.66932636e-01, 9.02533750e-02, 4.67286276e-01],
        [1.0, 5.29553176e-01, 4.24509360e-02, 1.23050400e-02, 4.71508674e-01],
        [1.0, 3.85627244e-01, 1.58321e-10, 4.64234e-15, 3.18311852e-01],
        [1.0, 3.63653942e-01, 1.9698e-12, 7.21305e-18, 2.97853032e-01],
    ])

    fw2_trans = np.array([
        [0.0, 1.0, 7.034442e-03, 3.66690547e-01, 4.03902e-04],
        [0.0, 1.0, 9.570788e-03, 3.29012990e-01, 6.8255e-04],
        [0.0, 1.0, 5.38863752e-01, 1.65916294e-01, 4.65692969e-01],
        [0.0, 1.0, 5.33485838e-01, 4.19321e-02, 4.70115272e-01],
        [0.0, 1.0, 3.90370926e-01, 1.42733e-10, 3.16758959e-01],
        [0.0, 1.0, 3.68309497e-01, 1.73955e-12, 2.96341297e-01],
    ])

    ccd_qe_list = np.array([0.5255, 0.872, 0.8256, 0.8093, 0.7676, 0.7575])

    phot_elec_conversion = np.array([36.17, 25.89, 19.85, 17.41, 11.95, 11.18])
    phot_energy = np.array([
        2.12e-17, 1.51e-17, 1.16e-17,
        1.02e-17, 6.99e-18, 6.54e-18
    ])

    ccd_gain_temp_array = np.array([
        -88.93333333, -87.91666667, -86.9, -86.02142857, -85.14285714,
        -84.26428571, -83.38571429, -82.50714286, -81.62857143, -80.75,
        -79.87142857, -78.99285714, -78.11428571, -77.23571429, -76.35714286,
        -75.05555556, -74.6, -73.65384615, -72.70769231, -71.76153846,
        -70.81538462, -69.86923077, -68.92307692, -67.97692308, -67.03076923,
        -66.08461538, -65.13846154, -64.19230769, -63.2, -62.3,
        -61.34615385, -60.39230769, -59.43846154, -58.48461538, -57.53076923,
        -56.57692308, -55.62307692, -54.66923077, -53.71538462, -52.76153846,
        -51.388, -50.396, -49.9, -48.86666667, -47.83333333, -46.8,
        -45.76666667, -44.73333333, -43.7, -42.66666667, -41.63333333,
        -40.6, -39.56666667, -38.944, -37.5, -36.53846154,
        -35.57692308, -34.61538462, -33.65384615, -32.69230769, -31.73076923
    ])

    ccd_gain = np.array([
        35.42917853, 35.47891651, 35.52865449, 35.57163649, 35.61461849,
        35.6576005, 35.7005825, 35.7435645, 35.7865465, 35.8295285,
        35.8725105, 35.9154925, 35.95847451, 36.00145651, 36.04443851,
        36.10811555, 36.13040251, 36.17669082, 36.22297913, 36.26926744,
        36.31555575, 36.36184406, 36.40813237, 36.45442068, 36.50070899,
        36.5469973, 36.5932856, 36.63957391, 36.68812019, 36.73215053,
        36.77881517, 36.82547981, 36.87214444, 36.91880908, 36.96547372,
        37.01213835, 37.05880299, 37.10546763, 37.15213226, 37.1987969,
        37.26599398, 37.3145252, 37.33879081, 37.38934417, 37.43989753,
        37.49045088, 37.54100424, 37.5915576, 37.64211095, 37.69266431,
        37.74321767, 37.79377102, 37.84432438, 37.87478685, 37.94543109,
        37.99247206, 38.03951302, 38.08655399, 38.13359495, 38.18063592,
        38.22767688
    ])

    # --- Index lookup (IDL where) ---
    wvln_loc = wvlns.index(wvln)
    fw1_loc = fw1_names.index(fw1)
    fw2_loc = fw2_names.index(fw2)

    # --- Effective area ---
    eff_area = (
        geom_area *
        ent_trans[wvln_loc] *
        fw1_trans[wvln_loc, fw1_loc] *
        fw2_trans[wvln_loc, fw2_loc] *
        m1_reflectivity[wvln_loc] *
        m2_reflectivity[wvln_loc] *
        ccd_qe_list[wvln_loc]
    )

    # --- Gain interpolation ---
    gain = np.interp(ccd_temp, ccd_gain_temp_array, ccd_gain)

    # --- Response construction (exact IDL order) ---
    response = gain                               # e-/DN
    response /= phot_elec_conversion[wvln_loc]    # phot/DN
    response /= eff_area                          # phot/DN/m^2
    response *= phot_energy[wvln_loc]             # J/DN/m^2
    response /= solid_angle                       # J/DN/m^2/sr

    return np.array([
        response,
        eff_area,
        phot_elec_conversion[wvln_loc],
        phot_energy[wvln_loc],
        gain
    ])

def _get_index_value(index, key):
    """
    Safely extract metadata from a SuviIndex or dict.
    """
    if hasattr(index, key):
        return getattr(index, key)

    if isinstance(index, dict) and key in index:
        return index[key]

    raise KeyError(f"{key} not found in index")


def suvi_restore_dn(
    data,
    index,
    approx_camera_noise=1.0,
    return_error=True
):
    """
    Restore SUVI L1b radiance image to Data Numbers (DN).

    Parameters
    ----------
    data : ndarray
        SUVI L1b image in radiance units (W m^-2 sr^-1)
    index : object or dict
        Must contain wavelnth, filter1, filter2, ccd_tmp1
    approx_camera_noise : float, optional
        Camera noise in DN (default = 1 DN, matches IDL)
    return_error : bool, optional
        Whether to return error estimate

    Returns
    -------
    out_dn : ndarray
        Image converted back to DN
    error_estimate : ndarray (optional)
        Approximate DN error per pixel
    response : ndarray
        Response vector from suvi_approx_response
    """

    # --- Pull metadata ---
    wvln = _get_index_value(index, "wavelnth")
    fw1 = _get_index_value(index, "filter1")
    fw2 = _get_index_value(index, "filter2")
    ccd_temp = _get_index_value(index, "ccd_tmp1")

    # --- Instrument response ---

    response = suvi_approx_response(wvln, fw1, fw2, ccd_temp)

    response_factor = response[0]   # J / DN m^-2 sr^-1
    phot_energy = response[3]       # J / photon
    ccd_gain = response[4]          # e- / DN

    # --- Radiance → DN ---
    out_dn = data / response_factor

    if not return_error:
        return out_dn, response

    # --- Error estimate (IDL-faithful) ---
    # data_phot = out_image * response[4] / response[2]
    data_phot = out_dn * ccd_gain / response[2]

    shot_noise = np.sqrt(np.maximum(data_phot, 0.0))

    error_estimate = np.sqrt(
        approx_camera_noise**2 +
        (shot_noise / (ccd_gain / response[2]))**2
    )

    return out_dn, error_estimate, response

