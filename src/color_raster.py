import numpy as np
import matplotlib.pyplot as plt
import rasterio
import matplotlib.colors as colors
import matplotlib.patches as patches

def raster_color_png(ndvi_array,colors_list,bounds):


    # Define the custom colormap
    cmap_name = 'custom_ndvi_colormap'
    cmap = colors.ListedColormap(colors_list, name=cmap_name)
    norm = colors.BoundaryNorm(bounds, cmap.N)

    
    # Plot the NDVI data with the custom colormap
    fig, ax = plt.subplots(figsize=(3,3))
    im = ax.imshow(ndvi_array, cmap=cmap, norm=norm)
    plt.show()
    ax.set_axis_off()

    plt.savefig('/tmp/tmp.png', dpi=200, bbox_inches='tight', pad_inches = 0 ,transparent=True)
    
    # cmap = plt.cm.get_cmap('RdYlGn') 
    # colored_ndvi = (cmap(ndvi_array) * 255).astype(np.uint8)
    
    # plt.imsave('/tmp/tmp.png', colored_ndvi)