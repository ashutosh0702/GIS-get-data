import json
import os
import boto3
import zipfile
import rasterio
from datetime import date
import numpy as np

import base64
from color_raster import raster_color_png
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Define the S3 bucket and file name
bucket_name = "sentinel-2-cogs-rnil"
file_name = "145_testgis/2023-03-09_NDVI.tif"
s3 = boto3.client('s3')

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

    #object_key = "9_Chilli_Bangalore_01/2023-05-18_NDVI.tif"
    object_key = "8984_testGIS/2023-06-20_NDMI.tif"
    object_path = "/tmp/tmp.tiff"
    try:
        s3.download_file(bucket_name, object_key, object_path)
    except:
        print("error Downloading")

    if index == "NDMI":
        orig_ds = rasterio.open(object_path)
        data = orig_ds.read(1)
        data = data.astype(np.float32)
        data = np.interp(data, (np.nanmin(data), np.nanmax(data)), (0, 1))
        resampled_path = "/tmp/NDMI_10m.tif"
        resampled_profile = orig_ds.profile.copy()
        resampled_profile.update(width=orig_ds.width // 10, height=orig_ds.height // 10, transform=orig_ds.transform * orig_ds.transform.scale(10, 10))
        with rasterio.open(resampled_path, 'w', **resampled_profile) as resampled_ds:
            resampled_ds.write(data.astype(rasterio.float32), 1)

        ds = rasterio.open(resampled_path)
        data = ds.read(1)

    elif index == "NDVI":
        print("inside NDVI index check logic")
        ds = rasterio.open(object_path)
        data = ds.read(1)
        data = data.astype(np.float32)
        data = np.interp(data, (np.nanmin(data), np.nanmax(data)), (0, 1))

    print("Printing the tiff array -------------------------")
    print(data)

    raster_color_png(data)

    
    # Read the temporary file as binary data
    with open('/tmp/tmp.png', 'rb') as f:
        png_data = f.read()
    encoded_image = base64.b64encode(png_data).decode('utf-8')

    print(encoded_image)

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
