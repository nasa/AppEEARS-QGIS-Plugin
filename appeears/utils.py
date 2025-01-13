
"""
Functions for interacting with the AppEEARS API.
"""

import requests
from osgeo import gdal

def fetch_task_data(api_url:str, token:str):
    """Uses the AppeEARS token to retrieve task info from the api endpoint"""
    if not token:
        return None
    try:
        response = requests.get(f'{api_url}task', headers={'Authorization': 'Bearer {0}'.format(token)})
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None
    except Exception as e:
        return None

def fetch_bundle_data(api_url:str, token:str, task_id:str):
    """
    Retrieves the AppEEARS bundle using a task id.
    """
    try:
        response = requests.get(f'{api_url}bundle/{task_id}', headers={'Authorization': 'Bearer {0}'.format(token)})
        if response.status_code == 200:
            data = response.json()['files']
            return data
        else:
            return None
    except Exception as e:
        return None

def build_file_url(api_url: str, task_id: str, file_id:str, file_name: str):
    """
    Composes the file url when given the AppEEARS API url, task id, file id, and file name.
    """
    url = f"{api_url}bundle/{task_id}/{file_id}/{file_name}"
    return url

def set_gdal_options(token: str, gdal_opts:dict = None):
    """
    Sets required gdal options.
    """
    required_gdal_opts = {'GDAL_HTTP_AUTH':'BEARER','GDAL_HTTP_BEARER': token, 'GDAL_HTTP_MAX_RETRY': "10", "GDAL_HTTP_RETRY_DELAY": "0.5"}

    if not gdal_opts:
        gdal_opts = required_gdal_opts
    else:
        gdal_opts = {**gdal_opts, **required_gdal_opts}

    for key, value in gdal_opts.items():
        gdal.SetConfigOption(key, value)