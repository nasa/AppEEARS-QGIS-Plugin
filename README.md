# AppEEARS-QGIS-Plugin

This QGIS plugin allows users to browse previously submitted requests from NASA's [Application for Extracting and Exploring Analysis Ready Samples (AppEEARS)](https://appeears.earthdatacloud.nasa.gov/) and load the output files directly into QGIS. This plugin currently only supports opening area sample requests with [cloud-optimized geotiff](https://cogeo.org/) formatted outputs.

## Requirements
- [NASA Earthdata Login Account](https://urs.earthdata.nasa.gov/home)
- [QGIS](https://qgis.org/) including [GDAL](https://gdal.org/en/stable/) version 3.7 or higher. Currently this means the plugin only works on **Windows**.

## Installation

Until the plugin is available on the QGIS plugin repository, you can install it from source. Follow these steps:

1. Navigate to your QGIS plugin directory. This is usually located at `C:\Users\<username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins` on Windows.
2. Clone or download and unzip the repository to this directory. 
3. Add the plugin to QGIS by going to `Plugins` > `Manage and Install Plugins...` > `Installed` and clicking the `Add` button.

## Use

1. Submit an area sample request to [AppEEARS](https://appeears.earthdatacloud.nasa.gov/) and request cloud-optimized geotiff format for the outputs. See the [AppEEARS documentation](https://appeears.earthdatacloud.nasa.gov/help) for more information on how to do this.
2. Enter [Earthdata Login Account](https://urs.earthdata.nasa.gov/home) credentials in the login tab the first time the plugin is used. This will save them in a .netrc file in the user's home directory. If you already have your Earthdata Login credentials present in a .netrc file, this step is not necessary.
3. Browse previously submitted AppEEARS requests in the `Requests` tab by pressing the refresh button at the top. This will populate a table showing the task name, status, task type, and task id.
4. Click on a row in the table to select it, and press the `Select` button to open the task bundle. This will show a table with all of the output files associated with the selected request. The table includes file name, file id and file size.
5. Click on a row containing a file name ending in .tif to select it, then press the `Load Data` button to add the file as a layer in QGIS.

## Development

Aspects relevant to maintainers for development purposes can be found in [this document](doc/development.md).

## Contact Info

Email: LPDAAC@usgs.gov  
Voice: +1-866-573-3222  
Organization: Land Processes Distributed Active Archive Center (LP DAAC)¹  
Website: https://lpdaac.usgs.gov/  

¹Work performed under USGS contract G15PD00467 for NASA contract NNG14HH33I.