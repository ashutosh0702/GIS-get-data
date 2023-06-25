import json
import os
import boto3
import zipfile
import rasterio
from datetime import date
import numpy as np
import sys
import base64
from rasterio.io import MemoryFile
from tempfile import TemporaryFile
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Define the S3 bucket and file name
bucket_name = "sentinel-2-cogs-rnil"
file_name = "145_testgis/2023-03-09_NDVI.tif"
s3 = boto3.client('s3')

color_maps = {
    "NDVI": mcolors.ListedColormap(['gray', 'lightgreen', 'mediumseagreen', 'green', 'darkgreen', 'darkgreen']),
    "NDMI": mcolors.ListedColormap(['white', 'lightblue', 'cornflowerblue', 'blue', 'darkblue', 'darkblue'])
}

def get_color(idx, color_maps):
    return color_maps[idx]

def get_cloud_image():
    with open('cloud.png', 'rb') as f:
        png_data = f.read()
    encoded_image = base64.b64encode(png_data).decode('utf-8')
    return {
        "isBase64Encoded": True,
        "statusCode": 200,
        "headers": {
            "Content-Type": "image/png",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Origin": "*",
        },
        "body": encoded_image,
    }

def lambda_handler(event, context):

    print("________LASTEST DEPLOYMENT____________")
    farmID = 8984
    index = "NDMI"

    object_key = "8984_testGIS/2023-06-20_NDMI.tif"
    object_path = f"/tmp/{farmID}.tif"
    s3.download_file(bucket_name, object_key, object_path)

    if index == "NDMI":
        with rasterio.open(object_path) as orig_ds:
            data = orig_ds.read(1, masked=True)
            data = data.astype(np.float32)
            data = np.interp(data, (np.nanmin(data), np.nanmax(data)), (0, 1))
            resampled_path = "/tmp/NDMI_10m.tif"
            resampled_profile = orig_ds.profile.copy()
            resampled_profile.update(width=orig_ds.width // 10, height=orig_ds.height // 10, transform=orig_ds.transform * orig_ds.transform.scale(10, 10))
            with rasterio.open(resampled_path, 'w', **resampled_profile) as resampled_ds:
                resampled_ds.write(data, 1)

            with rasterio.open(resampled_path) as ds:
                data = ds.read(1)

    elif index == "NDVI":
        with rasterio.open(object_path) as ds:
            data = ds.read(1, masked=True)
            data = data.astype(np.float32)
            data = np.interp(data, (np.nanmin(data), np.nanmax(data)), (0, 1))

    colors = get_color(index, color_maps)

    plt.imshow(data, cmap=colors, vmin=0, vmax=1)
    plt.axis('off')

    # Save the plot to a temporary file
    plt.savefig('/tmp/output.png', bbox_inches='tight', pad_inches=0)

    # Read the temporary file as binary data
    with open('/tmp/output.png', 'rb') as f:
        png_data = f.read()
    encoded_image = base64.b64encode(png_data).decode('utf-8')

    # Return the PNG image as binary data
    return {
        "isBase64Encoded": True,
        "statusCode": 200,
        "headers": {
            "Content-Type": "image/png",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Origin": "*",
        },
        "body": encoded_image,
    }
