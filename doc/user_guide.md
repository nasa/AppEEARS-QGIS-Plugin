# AppEEARS QGIS Plugin User Guide

The [AppEEARS QGIS Plugin](https://github.com/nasa/AppEEARS-QGIS-Plugin) allows users to browse previously submitted requests from NASA's [Application for Extracting and Exploring Analysis Ready Samples (AppEEARS)](https://appeears.earthdatacloud.nasa.gov/) and load the output files directly into QGIS. This plugin currently only supports opening area sample requests with [cloud-optimized geotiff](https://cogeo.org/) formatted outputs.

This document details how to install and get started using the [AppEEARS QGIS Plugin](https://github.com/nasa/AppEEARS-QGIS-Plugin).

## Installing the Plugin

Until the plugin is available from the official [QGIS Plugin List](https://plugins.qgis.org/plugins/), you can install it from source. Follow these steps:

1. Locate your QGIS plugin directory: launch QGIS and go to `Settings` > `User Profiles` > `Open Active Profile Folder`. This opens the profile folder in your file explorer or Finder, then navigate into `python` > `plugins`. This works the same way on Windows, macOS, and Linux. Once you've found it, close QGIS before continuing to the next step.

2. Clone this repository to the `plugins` directory or download to the `plugins` directory then unzip using extract all. 

<img
  src="assets/plugin-extract.png"
  alt="Extracting to QGIS Plugin Directory"
  width="750"
/>

3. Launch QGIS, then add the plugin going to `Plugins` > `Manage and Install Plugins...` > `Installed` and ensuring the box beside AppEEARS is checked.

<img
  src="assets/manage-plugins-window.png"
  alt="Manage Plugins Window"
  width="750"
/>

4. Launch by going to `Plugins` > `AppEEARS QGIS`

<img
  src="assets/plugin-toolbar-location.png"
  alt="Plugin Toolbar Locations"
  width="750"
/>

## Using the Plugin

1. Submit an area sample request to [AppEEARS](https://appeears.earthdatacloud.nasa.gov/) with cloud-optimized geotiff format selected for the outputs. We've included an example area request, `qgis-plugin-example-request.json` in the `appeears_qgis_plugin/assets` directory that can be uploaded and submitted on the [Extract Area Sample Page](https://appeears.earthdatacloud.nasa.gov/task/area). See the [AppEEARS documentation](https://appeears.earthdatacloud.nasa.gov/help) for more information on how to do this.

<img
  src="assets/upload-appeears-request.png"
  alt="Upload AppEEARS Request"
  width="750"
/>

2. Enter [Earthdata Login Account](https://urs.earthdata.nasa.gov/home) credentials in the login tab the first time the plugin is used. This will save them in a .netrc file in the user's home directory. If you already have your Earthdata Login credentials present in a .netrc file, this step is not necessary.

<img
  src="assets/login-tab.png"
  alt="Login Tab"
  width="750"
/>

3. Browse previously submitted AppEEARS requests in the `Requests` tab by pressing the refresh button at the top. This will populate a table showing the task name, status, task type, and task id.

<img
  src="assets/refresh-button.png"
  alt="Refresh Button"
  width="750"
/>

4. Click on a row in the table to select it, and press the `Select` button to open the task bundle. This will show a table with all of the output files associated with the selected request. The table includes file name, file id and file size.

<img
  src="assets/select-task.png"
  alt="Select Task"
  width="750"
/>

5. Click on a row containing a file name ending in .tif to select it, then press the `Load Data` button to add the file as a layer in QGIS.

<img
  src="assets/load-file.png"
  alt="Load File"
  width="750"
/>

6. Now you should see the loaded geotiff. This might take a while if your connection is slow.

<img
  src="assets/example-imagery.png"
  alt="Example Imagery"
  width="750"
/>

## Development

Aspects relevant to maintainers for development purposes can be found in [this document](doc/development.md).

## Contact Info

Email: LPDAAC@usgs.gov  
Voice: +1-866-573-3222  
Organization: Land Processes Distributed Active Archive Center (LP DAAC)¹  
Website: https://www.earthdata.nasa.gov/centers/lp-daac  

¹Work performed under USGS contract G15PD00467 for NASA contract NNG14HH33I.