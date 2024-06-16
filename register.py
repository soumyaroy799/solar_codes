from astropy import units as u 
from sunpy.map import Map
import numpy as np

def sun_register(smap,res=0.7,missing=0.,order=3,method='scipy'):
    """
    Co-registers observations with differet plate scale. Uses SunPy Map rotate function. 
    smap: SunPy Mapsequence.
    res: Required resolution of the output maps. Default value: 0.7
    missing: Value to replace the empty array values. Default value: 0
    order: Default order of interpolation. Default order: 3
    method: Interpolation method to use. Default: 'scipy'
    """

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
    return newmap
