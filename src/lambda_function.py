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

def resample_data(input_data, target_resolution):
    orig_ds = rasterio.open(input_data)
    orig_data = orig_ds.read(1)
    orig_profile = orig_ds.profile.copy()

    # Calculate the scaling factor for resampling
    scale_factor = orig_ds.res[0] / target_resolution

    # Calculate the new shape of the resampled data
    new_height = int(orig_data.shape[0] / scale_factor)
    new_width = int(orig_data.shape[1] / scale_factor)

    # Create an empty array for the resampled data
    resampled_data = np.empty((new_height, new_width), dtype=np.float32)

    # Perform resampling using rasterio's built-in resampling function
    rasterio.warp.reproject(
        source=orig_data,
        destination=resampled_data,
        src_transform=orig_profile["transform"],
        src_crs=orig_profile["crs"],
        dst_transform=orig_profile["transform"] * scale_factor,
        dst_crs=orig_profile["crs"],
        resampling=rasterio.enums.Resampling.bilinear
    )

    return resampled_data

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

        print("inside NDVI index check logic")
        ds = rasterio.open(object_path)
        data = ds.read(1)
        data = data.astype(np.float32)
        data = np.interp(data, (np.nanmin(data), np.nanmax(data)), (0, 1))
        '''
        # Calculate the target resolution for resampling
        target_resolution = 10  # in meters

        # Resample the data
        orig_data = resample_data(object_path, target_resolution)
        print(f"Data: {orig_data}")
        orig_data = orig_data.astype(np.float32)
        orig_data = np.interp(orig_data, (np.nanmin(orig_data), np.nanmax(orig_data)), (0, 1))

        print(f"orig_data : {orig_data}")
        data = orig_data
        print(f"data : {data}")
        '''

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
