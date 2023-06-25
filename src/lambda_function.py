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
    #object_key = "8984_testGIS/2023-06-20_NDVI.tif"
    object_key = "19_dummy_2/2023-05-24_NDMI.tif"
    object_path = "/tmp/tmp.tiff"



    try:
        s3.download_file(bucket_name, object_key, object_path)
    except:
        print("error Downloading")

    if index == "NDMI":
        colors_list = ['#bbd2f0', '#79aaf8', '#4086e3', '#1e60b1', '#0c468f', '#06408c']
        bounds = [-1, -0.2, 0, 0.2, 0.4, 0.6, 1]
        ds = rasterio.open(object_path)
        data = ds.read(1)
        data = data.astype(np.float32)
        data = np.interp(data, (np.nanmin(data), np.nanmax(data)), (0, 1))
        

    elif index == "NDVI":
        
        ds = rasterio.open(object_path)
        data = ds.read(1)
        data = data.astype(np.float32)
        data = np.interp(data, (np.nanmin(data), np.nanmax(data)), (0, 1))

        colors_list = ['#808080', '#94f08d', '#4df267', '#108c07', '#0c6d05', '#074003']
        bounds = [-1, 0, 0.1, 0.25, 0.4, 0.6, 1]


    raster_color_png(data,colors_list,bounds)

    with open('/tmp/tmp.png', 'rb') as f:
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
