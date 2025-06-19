from astropy import units as u
from sunpy.map import Map
import numpy as np

def sun_register(smap,res=0.7* u.arcsec / u.pix, recenter=True, missing=None, order=3, method='scipy', clip=True):
    """
    Co-registers observations with differet plate scale. Uses SunPy Map rotate function.
    smap: SunPy Mapsequence.
    res: Required resolution of the output maps. Default value: 0.7
    missing: Value to replace the empty array values. Default value: 0
    order: Default order of interpolation. Default order: 3
    method: Interpolation method to use. Default: 'scipy'
    """

    [x_shp, y_shp] = smap.data.shape

    if((smap.scale[0] / res).round() != 1.0 * u.arcsec / u.pix):
        if(smap.scale[0]/res>0.5):
            scale = (smap.scale[0] / res).round() * res * u.arcsec
        else:
            scale = (smap.scale[0]/res) * u.arcsec
    else:
        scale = res * u.arcsec

    scale_factor = smap.scale[0] / scale
    missing = smap.min() if missing is None else missing
    tempmap = smap.rotate(recenter=True,scale=scale_factor.value,order=order,missing=missing,method=method,clip=clip)
    center = np.floor(tempmap.meta["crpix1"])


    if(tempmap.data.shape[0]>x_shp):
        print('Here !!')
        range_side = (center + np.array([-1, 1]) * smap.data.shape[0] / 2) * u.pix
        newmap = tempmap.submap(u.Quantity([range_side[0], range_side[0]]),top_right=u.Quantity([range_side[1], range_side[1]]) - 1 * u.pix,)
    else:
        newmap = tempmap
    try:
        newmap.meta["r_sun"] = newmap.meta["rsun_obs"] / newmap.meta["cdelt1"]
        return newmap
    except KeyError:
        pass
        return newmap


