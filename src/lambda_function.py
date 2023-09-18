'''
import json
import os
import boto3
import zipfile
import rasterio
from datetime import date
import numpy as np
from datetime import datetime , timedelta
import base64
from color_raster import raster_color_png
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from rasterio.enums import Resampling

# Define the S3 bucket and file name
bucket_name = "sentinel-2-cogs-rnil"
s3 = boto3.client('s3')

def get_cloud_image():
    with open('clouds.png', 'rb') as f:
        png_data = f.read()
    encoded_image = base64.b64encode(png_data).decode('utf-8')
    return {
        "isBase64Encoded": True,
        "statusCode": 200,
        "headers": {
            "Content-Type": "image/gif",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Origin": "*",
        },
        "body": encoded_image,
    }



def lambda_handler(event, context):

    print(type(event))
    print(event)

    
    try:
        farmID = event["queryStringParameters"]["farmID"]
        farmName = event["queryStringParameters"]["farmName"]
        index = event["queryStringParameters"]["index"].upper()
        zoom = event["queryStringParameters"]["zoom"]
        date = event["queryStringParameters"]["date"]
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        
    except ValueError:
        return {
            "statusCode": 400,
            "body": json.dumps("Please provide/check query string parameters")
        }

    start_date = date_obj - timedelta(days=6)
    end_date = date_obj + timedelta(days=1)
    indexToFind = f"{index}.tif"

    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=f"{farmID}_{farmName}")['Contents']

    matching_objects = [obj for obj in objects if obj['Key'].endswith(indexToFind)  and start_date <= datetime.strptime(obj['Key'].split('/')[1].split('_')[0], '%Y-%m-%d').date() <= end_date]

    if not matching_objects:
        return get_cloud_image()

    object_key = matching_objects[-1]['Key']
    object_path = f"/tmp/{farmID}.tif"

    try:
        s3.download_file(bucket_name, object_key, object_path)
    except:
        print("error Downloading")

    if index == "NDMI":
        colors_list = ['#bbd2f0', '#79aaf8', '#4086e3', '#1e60b1', '#0c468f', '#06408c']
        bounds = [-1, -0.2, 0, 0.2, 0.4, 0.6, 1]

        with rasterio.open(object_path) as src:

            original_data = src.read(1)
            # Calculate the new dimensions for resampling
            new_height = original_data.shape[0] * 4
            new_width = original_data.shape[1] * 4

            # Resample the raster to 10-meter resolution
            resampled_data = src.read(
                out_shape=(src.count, new_height, new_width),
                resampling=Resampling.bilinear
            )
        data = resampled_data[0]
        
        #data = np.interp(data, (np.nanmin(data), np.nanmax(data)), (0, 1))
        
        
        

    elif index == "NDVI":
        
        ds = rasterio.open(object_path)
        data = ds.read(1)
        
        # NEW CODE ADDED HERE
        # with rasterio.open(object_path) as src:

        #     original_data = src.read(1)
        #     new_pixel_size = 20 # 50cm
    
    
        #     scaling_factor = src.transform.a / new_pixel_size
            
        #     print(f"Scaling factor : {scaling_factor}")
            
        #     new_height = original_data.shape[0] * int(scaling_factor)
        #     new_width = original_data.shape[1] * int(scaling_factor)

        #     # Resample the raster to 10-meter resolution
        #     resampled_data = src.read(
        #         out_shape=(src.count, new_height, new_width),
        #         resampling=Resampling.bilinear
        #     )
        # data = resampled_data[0]
        

        colors_list = ['#808080', '#94f08d', '#4df267', '#108c07', '#0c6d05', '#074003']
        bounds = [-1, 0.009, 0.1, 0.25, 0.4, 0.6, 1]

   

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
'''
import json
import boto3
import base64
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from io import BytesIO
from PIL import Image
from datetime import datetime, timedelta

# Initialize S3 client and bucket_name outside the lambda handler
s3 = boto3.client('s3')
bucket_name = 'gis-colourized-png-data'

def lambda_handler(event, context):
    print(type(event))
    print(event)

    try:
        query_params = event["queryStringParameters"]
        farmID = query_params["farmID"]
        farmName = query_params["farmName"]
        index = query_params["index"].upper()
        zoom = query_params["zoom"]
        date = query_params["date"]
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except (ValueError, KeyError):
        return {
            "statusCode": 400,
            "body": json.dumps("Please provide/check query string parameters")
        }

    start_date = date_obj - timedelta(days=6)
    end_date = date_obj + timedelta(days=1)
    indexToFind = f"{index}.png"

    try:
        objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=f"{farmID}_{farmName}")['Contents']
        matching_objects = [
            obj for obj in objects 
            if obj['Key'].endswith(indexToFind) and 
            start_date <= datetime.strptime(obj['Key'].split('/')[1].split('_')[0], '%Y-%m-%d').date() <= end_date
        ]

        if not matching_objects:
            return get_cloud_image()

        object_key = matching_objects[-1]['Key']
        s3_response = s3.get_object(Bucket=bucket_name, Key=object_key)
        image_data = s3_response['Body'].read()

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'image/png',
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Origin": "*",
            },
            'body': base64.b64encode(image_data).decode('utf-8'),
            'isBase64Encoded': True
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
