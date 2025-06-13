
from matplotlib.widgets import RectangleSelector
import matplotlib.pyplot as plt
import astropy.units as u
# author_gowria

def select_roi_with_mouse(sunpy_map):
    # Create a figure and explicitly add a WCSAxes subplot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection=sunpy_map) # Create ax first
    ax.set_title("Select ROI (click and drag) then close the window")
    sunpy_map.plot(axes=ax)
    coords = []

    def onselect(eclick, erelease):
        coords.append((eclick.xdata, eclick.ydata, erelease.xdata, erelease.ydata))

    toggle_selector = RectangleSelector(ax, onselect, useblit=True,
                                        button=[1], minspanx=5, minspany=5, spancoords='pixels',
                                        interactive=True)
    plt.show()

    if not coords:
        raise RuntimeError("ROI selection cancelled or failed.")

    x1, y1, x2, y2 = coords[0]

    bottom_left = (min(x1, x2), min(y1, y2)) * u.pixel
    top_right = (max(x1, x2), max(y1, y2)) * u.pixel

    submap = sunpy_map.submap(bottom_left=bottom_left, top_right=top_right)
    return submap

if __name__=="__main__" :
    """
    # Loading the files and sorting an dtaking the first image as reference
    """
    ref_img = sunpy.map.Map(sorted_files[ref_idx])
    logger.info(f"Using reference image: {sorted_files[ref_idx]}")
    ref_submap = select_roi_with_mouse(ref_img)

    """
    Rest of the code
    """
