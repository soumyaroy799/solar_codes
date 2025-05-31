from astropy import units as u
from sunpy.map import Map
import numpy as np

def sun_register(smap,res=0.7* u.arcsec / u.pix,missing=None,order=3,method='scipy', clip=True):
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
        scale = (smap.scale[0] / res).round() * res * u.arcsec
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


def sun_register_2(smap, res=0.7 * u.arcsec, missing=0., order=3, method='scipy'):
    """
    Co-registers observations with different plate scales. Uses SunPy Map's rotate function.

    Parameters:
    -----------
    smap : sunpy.map.Map
        Input SunPy map to be co-registered.
    res : astropy.units.Quantity, optional
        Required resolution of the output map in arcsec/pix. Default is 0.7 arcsec/pix.
    missing : float, optional
        Value to replace missing (NaN) pixels. Default is 0.
    order : int, optional
        Interpolation order. Default is 3.
    method : str, optional
        Interpolation method to use ('scipy' or other valid methods). Default is 'scipy'.

    Returns:
    --------
    sunpy.map.Map
        Co-registered SunPy map with the specified resolution.
    """

    # Ensure the resolution is in the correct units
    res = u.Quantity(res, u.arcsec)

    # Compute the desired scale
    current_scale = smap.scale[0]
    if not np.isclose((current_scale / res).decompose().value, 1.0):
        scale = res
    else:
        scale = current_scale

    # Compute the scale factor for resizing
    scale_factor = (current_scale / scale).decompose().value

    # Rotate and rescale the map
    tempmap = smap.rotate(
        recenter=True,
        scale=scale_factor,
        order=order,
        missing=missing,
        method=method,
    )

    # Ensure rotated data matches the original data type
    if tempmap.data.dtype != smap.data.dtype:
        tempmap.data = tempmap.data.astype(smap.data.dtype)

    # Define the submap range based on the new map center
    center_x = tempmap.meta["crpix1"]
    center_y = tempmap.meta["crpix2"]
    side_length = smap.data.shape[0] / 2

    # Submap range in pixels
    bottom_left = u.Quantity([center_x - side_length, center_y - side_length], u.pix)
    top_right = u.Quantity([center_x + side_length - 1, center_y + side_length - 1], u.pix)

    # Extract the submap
    newmap = tempmap.submap(bottom_left, top_right=top_right)

    # Update solar radius in pixels
    newmap.meta["r_sun"] = newmap.meta["rsun_obs"] / newmap.meta["cdelt1"]

    return newmap
