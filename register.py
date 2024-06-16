from astropy import units as u 
from sunpy.map import Map
import numpy as np

def sun_register(smap,res=0.6,missing=0.,order=3,method='scipy'):

    if((smap.scale[0] / res).round() != 1.0 * u.arcsec / u.pix):
        scale = (smap.scale[0] / res).round() * res * u.arcsec
    else:
        scale = res * u.arcsec
    
    scale_factor = smap.scale[0] / scale
    tempmap = smap.rotate(recenter=True,scale=scale_factor.value,order=order,missing=missing,method=method,)
    center = np.floor(tempmap.meta["crpix1"])
    range_side = (center + np.array([-1, 1]) * smap.data.shape[0] / 2) * u.pix
    newmap = tempmap.submap(u.Quantity([range_side[0], range_side[0]]),top_right=u.Quantity([range_side[1], range_side[1]]) - 1 * u.pix,)
    newmap.meta["r_sun"] = newmap.meta["rsun_obs"] / newmap.meta["cdelt1"]
    newmap.meta["lvl_num"] = 1.5
    newmap.meta["bitpix"] = -64
    return newmap