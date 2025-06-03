import os
import pathlib
from osgeo import gdal


def set_gdal_options(token: str, opts: dict = {}):
    """
    Sets required GDAL options.
    """
    required_opts = {
        "GDAL_HTTP_AUTH": "BEARER", "GDAL_HTTP_BEARER": token,
        "GDAL_HTTP_MAX_RETRY": "10", "GDAL_HTTP_RETRY_DELAY": "0.5"
    }
    all_opts = {**opts, **required_opts}

    for key, value in all_opts.items():
        gdal.SetConfigOption(key, value)


def get_project_root_path():
    return str(pathlib.Path(__file__).parent.parent.absolute())


def get_path_from_root(*parts):
    return os.path.join(get_project_root_path(), *parts)
