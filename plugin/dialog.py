import os
from qgis.core import QgsApplication, QgsAuthManager, QgsAuthMethodConfig, Qgis, QgsMessageLog, QgsRasterLayer, QgsProject
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtCore import QUrl
from . import netrc, util, api
from . log import LOGGER

# Load .ui file so that PyQt can populate plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dialog.ui'
))


class Dialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(Dialog, self).__init__(parent)

        # data members used in various methods
        self.machine = 'urs.earthdata.nasa.gov'
        self.api = None
        
        # Set default parameters
        self.current_task_id = None

        # Set up UI
        self.setupUi(self)

        # intro section of the login tab
        self.auth_gridLayout.setSpacing(5)
        self.login_intro.setWordWrap(True)
        self.login_intro.setContentsMargins(0, 0, 0, 15)
        self.login_intro.linkActivated.connect(self.edl_link_clicked)
        self.login_intro.setText(
            'An <a href="https://urs.earthdata.nasa.gov/users/new">Earthdata Login</a> '
            'account is required to use AppEEARS.&nbsp;Your user .netrc file will be '
            'used to store and source those credentials.<br/><br/>To modify the credentials '
            'in that file,&nbsp;please use the form below.&nbsp;If the file doesn\'t '
            'exist,&nbsp;it will be created.'
        )

        # Connect Signals
        self.save_credentials_pushButton.clicked.connect(self.store_entered_credentials)
        self.refresh_pushButton.clicked.connect(self.refresh_tasks)
        self.select_pushButton.clicked.connect(self.select_task)
        self.load_data_pushButton.clicked.connect(self.load_selected_file)

        # Configure table selection behavior
        self.task_tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.task_tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.bundle_tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.bundle_tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # Password Checkbox
        self.password_lineEdit.setPlaceholderText("Enter your password")
        self.show_password_checkBox.toggled.connect(self.toggle_password_visibility)

    def _open_messagebox(self, method_name: str, *args, **kwargs):
        if (method := getattr(QtWidgets.QMessageBox, method_name, None)) is None:
            raise ValueError(f'messagebox method {method_name} does not exist')
        return method(self, *args, **kwargs)

    def edl_link_clicked(self, link):
        QDesktopServices.openUrl(QUrl(link))

    def toggle_password_visibility(self, checked):
        """
        Toggles password visibility
        """
        self.password_lineEdit.setEchoMode(
            QtWidgets.QLineEdit.Normal if checked else QtWidgets.QLineEdit.Password
        )

    def store_entered_credentials(self):
        """
        Stores lineEdit credentials into the .netrc file.
        """
        username = self.username_lineEdit.text().strip()
        password = self.password_lineEdit.text().strip()

        # Add to .netrc file
        try:
            netrc.store_creds(self.machine, username, password)
            self._open_messagebox(
                "information", "Credentials Updated",
                f"Credentials for '{self.machine}' stored successfully."
            )
        except netrc.ConflictError:
            # This means the credentials existed for the given machine
            reply = self._open_messagebox(
                "question", "Credentials Exist",
                f"Credentials for '{self.machine}' already exist.  Overwrite them?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No
            )

            if reply == QtWidgets.QMessageBox.No:
                return

            try:
                netrc.store_creds(self.machine, username, password, force_update=True)
                self._open_messagebox(
                    "information", "Credentials Updated",
                    f"Credentials for '{self.machine}' updated successfully."
                )
            except Exception as e:
                self._open_messagebox("critical", "Error", str(e))

        except Exception as e:
            self._open_messagebox("critical", "Error", str(e))

    def refresh_tasks(self):
        """
        Runs upon click of refresh button - gets an appeears token if necessary and populates tasks table.
        """

        username, password = netrc.retrieve_creds(self.machine)
        if not username or not password:
            self._open_messagebox(
                "warning", "No Credentials", f"No credentials",
                f"No credentials found for {self.machine}. Please enter credentials on the login tab."
            )
            return

        if self.api is None:
            self.api = api.Client((username, password))
        else:
            # if the user has changed creds, incorporate them
            self.api.update_creds((username, password))

        try:
            data_list = self.api.fetch_task_data()
        except api.ApiError:
            self._open_messagebox(
                "warning", "Error",
                "Data could not be retrieved from the AppEEARS API. Please check your credentials."
            )
            return
        
        if not data_list:
            LOGGER.info("No data retrieved from AppEEARS API or failed to load data.")
            return
        self.populate_table(data_list)
        LOGGER.info("Populated Task Table")

    def populate_table(self, data_list):
        """"
        Populate the tasks table widget from a list of dicts using only
        the desired keys.
        """    
        desired_columns = ["task_name", "status", "task_type", "task_id"]
        num_rows = len(data_list)
        num_cols = len(desired_columns)
        
        # Clear existing rows
        self.task_tableWidget.clearContents()
        self.task_tableWidget.setRowCount(num_rows)
        self.task_tableWidget.setColumnCount(num_cols)

        # Set Header Labels
        self.task_tableWidget.setHorizontalHeaderLabels(desired_columns)

        # Populate Table
        for row_index, entry in enumerate(data_list):
            for col_index, key in enumerate(desired_columns):
                value = entry.get(key,"")
                item = QtWidgets.QTableWidgetItem(str(value))
                self.task_tableWidget.setItem(row_index, col_index, item)
        self.task_tableWidget.resizeColumnsToContents()
    
    def select_task(self):
        """
        Selects the currently highlighted row from the task table, and use it to populate the bundle table.
        """

        row = self.task_tableWidget.currentRow()
        if row < 0:
            LOGGER.info("No row is currently selected.")
            return
        
        # Set task_id and status using hard-coded task-id column
        self.current_task_id = self.task_tableWidget.item(row,3).text()
        task_status = self.task_tableWidget.item(row, 1).text()

        if not self.current_task_id:
            self._open_messagebox("warning", "Invalid Row", "Could not find task.")
            return

        # Restrict selection only to tasks with status == "DONE" (adjust string as needed)
        if task_status != "done":
            self._open_messagebox(
                "information", "Task Not Done",
                f"This task is '{task_status}' and cannot be selected."
            )
            return

        # Fetch bundle data from AppEEARS API
        try:
            bundle_data = self.api.fetch_bundle_data(self.current_task_id)
        except api.ApiError:
            self._open_messagebox(
                "warning", "Error",
                "Data could not be retrieved from the AppEEARS API. Please check your credentials."
            )
            return

        if not bundle_data:
            LOGGER.info("Error fetching bundle data.")

        # Populate Bundle Table
        self.populate_bundle_table(bundle_data)
        
    def populate_bundle_table(self, bundle_data_list):
        """
        Populate the tasks table widget from a list of dicts using only
        the desired keys.
        """
        desired_columns = ["file_name", "file_id", "file_size"]
        num_rows = len(bundle_data_list)
        num_cols = len(desired_columns)
        
        # Clear existing rows
        self.bundle_tableWidget.clearContents()
        self.bundle_tableWidget.setRowCount(num_rows)
        self.bundle_tableWidget.setColumnCount(num_cols)

        # Set Header Labels
        self.bundle_tableWidget.setHorizontalHeaderLabels(desired_columns)

        # Populate Table
        LOGGER.info(f"{bundle_data_list[0]}")
        for row_index, entry in enumerate(bundle_data_list):
            for col_index, key in enumerate(desired_columns):
                value = entry.get(key,"")
                if key == "file_name":
                    value = value.split("/")[-1]
                item = QtWidgets.QTableWidgetItem(str(value))
                self.bundle_tableWidget.setItem(row_index, col_index, item)
        # Resize
        self.bundle_tableWidget.resizeColumnsToContents()

    def load_selected_file(self):
        """
        Uses the current_task_id, file_id, and file_name to build a url path, then opens the url and adds the layer to the current project.
        Currently only works for cloud-optimized geotiff files.
        """

        # Retrieve current row
        row = self.bundle_tableWidget.currentRow()
        if row < 0:
            LOGGER.info("No file selected.")
            return

        # Get ID and Name and Open File
        try: 
            file_id = self.bundle_tableWidget.item(row,1).text()
            file_name = self.bundle_tableWidget.item(row,0).text()

            if not file_id:
                self._open_messagebox("warning", "Invalid Row", "Could not find task.")
                return

            # Build File URL from selection
            file_url = self.api.build_file_url(self.current_task_id, file_id, file_name)
            
            # Handle non-tif cases
            if file_url.split('.')[-1] != 'tif':
                self._open_messagebox(
                    "critical", "Error", (
                        "Currently this plugin shows all AppEEARS requests and output filetypes, "
                        "but only supports opening cloud-optimized geotiff files from area sample requests."
                    )
                )
                return

            # Set Necessary GDAL Options
            util.set_gdal_options(self.api.token)
            LOGGER.info("Required GDAL options set.")
        
            # Load data into memory
            LOGGER.info(f"Opening Data from source: {file_url}")
            raster_layer = QgsRasterLayer(file_url, file_name)

            # Add Layer to QGIS Project
            QgsProject.instance().addMapLayer(raster_layer)
            LOGGER.info(f"Added raster layer: {file_name}")

        except Exception as e:
            LOGGER.info(f"Error loading COG. {e}")
            return None     
