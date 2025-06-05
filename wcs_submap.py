import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord
from sunpy.map import Map, MapSequence, GenericMap
from astropy.wcs.utils import skycoord_to_pixel
from matplotlib.path import Path


def _mask_submap_region(map_obj, bottom_left, top_right, width=None, height=None, outside_value=-200):
    # Determine corners
    if top_right is not None:
        br = SkyCoord(top_right.Tx, bottom_left.Ty, frame=bottom_left.frame)
        tl = SkyCoord(bottom_left.Tx, top_right.Ty, frame=bottom_left.frame)
        tr = top_right
    elif width is not None and height is not None:
        tr = bottom_left + SkyCoord(width, height)
        br = bottom_left + SkyCoord(width, 0 * height.unit)
        tl = bottom_left + SkyCoord(0 * width.unit, height)
    else:
        raise ValueError("Provide either top_right or both width and height.")

    corners = SkyCoord([bottom_left, br, tr, tl, bottom_left], frame=bottom_left.frame)
    px_x, px_y = skycoord_to_pixel(corners, map_obj.wcs)
    polygon_xy = np.array([px_x, px_y]).T

    poly = Path(polygon_xy)

    ny, nx = map_obj.data.shape
    x, y = np.meshgrid(np.arange(nx), np.arange(ny))
    points = np.vstack((x.ravel(), y.ravel())).T
    mask = poly.contains_points(points).reshape((ny, nx))

    # Apply mask
    padded_data = np.full_like(map_obj.data, outside_value)
    padded_data[mask] = map_obj.data[mask]

    new_meta = map_obj.meta.copy()
    if map_obj.mask is not None:
        new_mask = np.zeros_like(map_obj.mask)
        new_mask[mask] = map_obj.mask[mask]
        return Map(padded_data, new_meta, mask=new_mask, plot_settings=map_obj.plot_settings)

    return Map(padded_data, new_meta, plot_settings=map_obj.plot_settings)


def apply_mask_to_submap(submap, bottom_left, *, top_right=None, width=None, height=None, outside_value=-200):
    if not isinstance(submap, GenericMap):
        raise TypeError("This function expects a single SunPy Map (e.g. a submap).")
    return _mask_submap_region(submap, bottom_left, top_right, width, height, outside_value)
