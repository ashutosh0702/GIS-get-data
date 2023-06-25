
import json
import os
import boto3
import zipfile
import rasterio
from datetime import date
import numpy as np
from osgeo import gdal
import sys
import base64
from rasterio.io import MemoryFile
from tempfile import TemporaryFile


import rasterio
from rasterio.fill import fillnodata

from datetime import datetime , timedelta
# Define the S3 bucket and file name
bucket_name = "sentinel-2-cogs-rnil"
file_name = "145_testgis/2023-03-09_NDVI.tif"
s3 = boto3.client('s3')



color_maps = {
    "NDVI": np.zeros((256, 4), dtype=np.uint8),
    "NDMI": np.zeros((256, 4), dtype=np.uint8)
}

def get_color(idx, color_maps, min_value, max_value):
    if idx == "NDVI":
        
        color_maps["NDVI"][0:37] = [247, 252, 245, 255]
        color_maps["NDVI"][37:55] = [211, 242, 199, 255]
        color_maps["NDVI"][55:77] = [160, 240, 127, 255]
        color_maps["NDVI"][77:99] = [133, 240, 89, 255]
        color_maps["NDVI"][99:154] = [103, 227, 52, 255]
        color_maps["NDVI"][154:175] = [73, 191, 25, 255]
        color_maps["NDVI"][175:201] = [44, 138, 6, 255]
        color_maps["NDVI"][201:225] = [25, 84, 2, 255]
        color_maps["NDVI"][225:256] = [16, 54, 1, 255]
        
    elif idx == "NDMI":
        for i in range(255):
            color_maps["NDMI"][i+1] = [int(i), int(i), 255, 255]
        color_maps["NDMI"][0] = [0,0,0,0]
        
    
    
    
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
    
    print(type(event))
    print(event)
    '''
    farmID = event["queryStringParameters"]["farmID"]
    farmName = event["queryStringParameters"]["farmName"]
    index = event["queryStringParameters"]["index"].upper()
    zoom = event["queryStringParameters"]["zoom"]
    date = event["queryStringParameters"]["date"]

    try:
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

    matching_objects = [obj for obj in objects if obj['Key'].endswith(indexToFind) and obj['Key'].startswith(f'{farmID}_') and start_date <= datetime.strptime(obj['Key'].split('/')[1].split('_')[0], '%Y-%m-%d').date() <= end_date]

    if not matching_objects:
        return get_cloud_image()

    object_key = matching_objects[-1]['Key']
    object_path = f"/tmp/{farmID}.tif"
    s3.download_file(bucket_name, object_key, object_path)
    '''
    farmID = 8984
    index = "NDVI"

    object_key = "8984_testGIS/2023-06-20_NDVI.tif"
    object_path = f"/tmp/{farmID}.tif"
    s3.download_file(bucket_name, object_key, object_path)


    if index == "NDMI":
        orig_ds = gdal.Open(object_path)
        orig_extent = gdal.Info(orig_ds, format='json')['cornerCoordinates']
        llx, lly = orig_extent['lowerLeft']
        urx, ury = orig_extent['upperRight']
        resampled_path = "/tmp/NDMI_10m.tif"
        output_ds = gdal.Warp(resampled_path, orig_ds, outputBounds=[llx, lly, urx, ury], xRes=10, yRes=10, resampleAlg="cubic", srcNodata=float('nan'))
        ds = gdal.Open(resampled_path)
        data = ds.ReadAsArray()
        data = np.interp(data, (np.nanmin(data),np.nanmax(data)), (1,255))
        data = np.round_(data)
    elif index == "NDVI":
        ds = gdal.Open(object_path)
        
        orig_extent = gdal.Info(ds, format='json')['cornerCoordinates']
        ulx, uly = orig_extent['upperLeft']
        lrx, lry = orig_extent['lowerRight']
        data = ds.ReadAsArray()
        data = np.interp(data, (np.nanmin(data),np.nanmax(data)), (0, 255))
        data = np.round_(data)

    ds = None
    orig_ds = None
    output_ds = None
    
    
    min_value = np.nanmin(data)
    max_value = np.nanmax(data)
    colors = get_color(index, color_maps, min_value, max_value)
   
    cmap = {i: tuple(colors[i]) for i in range(len(colors))}

    color_data = np.empty((4, data.shape[0], data.shape[1]), dtype=np.uint8)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if np.isnan(data[i, j]):
                print("Inside NaN checking")
                # Set transparent color for NaN values
                color_data[:, i, j] = (0, 0, 0, 0)
            else:
                print("not nan")
                color_data[:, i, j] = cmap[int(data[i, j])]
                
  
    
    color_data = np.repeat(np.repeat(color_data, int(zoom), axis=1), int(zoom), axis=2)
    
    
    metadata = {
        'driver': 'PNG',
        'width': color_data.shape[2],
        'height': color_data.shape[1],
        'count': color_data.shape[0],
        'dtype': np.uint8,
        'nodata': 0,
        'transform': rasterio.Affine(1, 0, 0, 0, -1, color_data.shape[1]),
        'crs': rasterio.crs.CRS.from_epsg(4326)
    }
    
     # Define the output file path
    output_path = '/tmp/output.png'
    
    with rasterio.open(output_path, 'w', **metadata) as dst:
        for i, image in enumerate(color_data):
            print(i,image)
            dst.write(image, i+1)

    with open('/tmp/output.png', 'rb') as f:
        png_data = f.read()
    encoded_image = base64.b64encode(png_data).decode('utf-8')

    # Return the PNG image as binary data
    return {
            "isBase64Encoded": True,
            "statusCode": 200,
            "headers": {
                "Content-Type": "image/png",
                #"Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,access-control-allow-origin",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Origin": "*",
            },
            "body": encoded_image,
        }