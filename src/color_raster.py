import numpy as np
import matplotlib.pyplot as plt
import rasterio
import matplotlib.colors as colors
import matplotlib.patches as patches

def raster_color_png(ndvi_array,polygon_boundary):

    # Define the custom colormap
    colors_list = ['#808080', '#d7191c', '#ffa500', '#ffff99', '#1fed18', '#006400'] # grey, red, orange, light yellow, green, dark green
    cmap_name = 'custom_ndvi_colormap'
    cmap = colors.ListedColormap(colors_list, name=cmap_name)
    bounds = [-1, 0, 0.1, 0.25, 0.4, 0.6, 1] # set the color boundaries
    norm = colors.BoundaryNorm(bounds, cmap.N) # set the normalization to use the boundaries

    

    # Plot the NDVI data with the custom colormap
    fig, ax = plt.subplots(figsize=(5,5))
    im = ax.imshow(ndvi_array, cmap=cmap, norm=norm)
    ax.set_axis_off()

    
    polygon_boundary.plot(ax=ax,facecolor='none', edgecolor='blue')
    '''
    # Set the plot extent to the polygon boundary
    plt.xlim(polygon_boundary.total_bounds[0], polygon_boundary.total_bounds[2])
    plt.ylim(polygon_boundary.total_bounds[1], polygon_boundary.total_bounds[3])
    '''
    
    # Save the plot as a PNG file
    #plt.savefig('/tmp/plot.png')
    plt.close()

    
    plt.savefig('/tmp/tmp.png', dpi=200, bbox_inches='tight', pad_inches = 0 ,transparent=True)
