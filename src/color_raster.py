import numpy as np
import matplotlib.pyplot as plt
import rasterio
import matplotlib.colors as colors
import matplotlib.patches as patches

def raster_color_png(ndvi_array):

    # Define the custom colormap
    colors_list = ['#808080', '#d7191c', '#ffa500', '#ffff99', '#1fed18', '#006400'] # grey, red, orange, light yellow, green, dark green
    cmap_name = 'custom_ndvi_colormap'
    cmap = colors.ListedColormap(colors_list, name=cmap_name)
    bounds = [-1, 0, 0.1, 0.25, 0.4, 0.6, 1] # set the color boundaries
    norm = colors.BoundaryNorm(bounds, cmap.N) # set the normalization to use the boundaries

    
    # Plot the NDVI data with the custom colormap
    fig, ax = plt.subplots(figsize=(3,3))
    im = ax.imshow(ndvi_array, cmap=cmap, norm=norm)
    plt.show()
    ax.set_axis_off()

    plt.savefig('/tmp/tmp.png', dpi=200, bbox_inches='tight', pad_inches = 0 ,transparent=True)
