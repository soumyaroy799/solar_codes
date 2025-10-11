import numpy as np
from sunpy.map import Map, MapSequence
import os, asdf

def save_asdf_map(obj, path=None, filename=None, compress=False):
    """
    Save a SunPy Map or MapSequence to an ASDF file, preserving full metadata.

    Parameters
    ----------
    obj : sunpy.map.GenericMap or sunpy.map.MapSequence
        The SunPy map or map sequence to save.
    path : str, optional
        Directory or full path where the ASDF file will be saved.
        If a directory is provided, a filename will be auto-generated.
    filename : str, optional
        Name of the ASDF file (used if 'path' is a directory or None).
    compress : bool, optional
        If True, compress all array data with zlib (lossless).
    """
    # Determine filename and directory behavior
    if path is None and filename is None:
        raise ValueError("You must specify either 'path' or 'filename'.")

    if path and os.path.isdir(path):
        if filename is None:
            base = "map_sequence.asdf" if isinstance(obj, sunpy.map.MapSequence) else "map.asdf"
        else:
            base = filename
        filepath = os.path.join(path, base)
    elif path and os.path.splitext(path)[1].lower() == ".asdf":
        filepath = path
    elif filename:
        filepath = filename
    else:
        raise ValueError("Invalid combination of 'path' and 'filename'.")

    # Build ASDF tree
    if isinstance(obj, MapSequence):
        tree = {
            "type": "sunpy.map.MapSequence",
            "maps": [{"data": m.data, "meta": dict(m.meta)} for m in obj],
        }
    elif isinstance(obj, GenericMap):
        tree = {
            "type": "sunpy.map.GenericMap",
            "data": obj.data,
            "meta": dict(obj.meta),
        }
    else:
        raise TypeError("Object must be a SunPy Map or MapSequence")

    # Write ASDF file
    with asdf.AsdfFile(tree) as af:
        if compress:
            af.write_to(filepath, all_array_compression="zlib")
        else:
            af.write_to(filepath)


def read_asdf_map(filepath):
    """
    Load a SunPy Map or MapSequence from an ASDF file.

    Parameters
    ----------
    filepath : str
        Path to the ASDF file.

    Returns
    -------
    sunpy.map.GenericMap or sunpy.map.MapSequence
        The loaded SunPy Map or MapSequence with full metadata.
    """
    with asdf.open(filepath) as af:
        tree = af.tree

        if tree["type"] == "sunpy.map.MapSequence":
            maps = [Map(np.array(m["data"]), m["meta"]) for m in tree["maps"]]
            return MapSequence(maps)
        elif tree["type"] == "sunpy.map.GenericMap":
            return Map(np.array(tree["data"]), tree["meta"])
        else:
            raise TypeError(f"Unknown ASDF map type: {tree['type']}")