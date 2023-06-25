import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Define the colors and labels
#colors = ['#00FF00', '#006400', '#228B22']
colors = ['#94f08d', '#108c07','#074003']
labels = ['Poor', 'Good', 'Excellent']

# Create a color map from the colors
cmap = mcolors.LinearSegmentedColormap.from_list('mycmap', colors)

# Create a figure and axis
fig, ax = plt.subplots()

# Create a colorbar and set the tick labels
cb = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap), ax=ax, orientation='vertical', ticks=[0, 0.5, 1])
cb.ax.set_yticklabels(labels, color='white')

# Save the colorbar as a PNG file
plt.savefig('ndvi.png', dpi=300, bbox_inches='tight', transparent=True)
