import pytest
from qgis.testing import unittest, start_app, stop_app
from qgis.PyQt import QtWidgets
from unittest.mock import patch, Mock, PropertyMock
from plugin import dialog, netrc, api


@pytest.fixture(scope='session', autouse=True)
def qgis_app():
    start_app()
    yield
    stop_app()

MODULE_PATH = 'plugin.dialog'


class DialogTest(unittest.TestCase):

    def test_init(self, return_instance=False):
        expected_machine = 'urs.earthdata.nasa.gov'
        actual_dialog = dialog.Dialog()
        if return_instance:
            return actual_dialog
        
        self.assertEqual(actual_dialog.machine, expected_machine)

    @patch(f'{MODULE_PATH}.QtWidgets.QMessageBox.information')
    def test_open_messagebox(self, mock_information):
        expected_method_name = 'information'
        expected_msg_args = ('title', 'content')
        expected_res = 1
        mock_information.return_value = expected_res

        actual_dialog = self.test_init(return_instance=True)
        actual_res = actual_dialog._open_messagebox(expected_method_name, *expected_msg_args)

        mock_information.assert_called_with(actual_dialog, *expected_msg_args)
        self.assertEqual(actual_res, expected_res)

    def test_open_messagebox_bad_method(self):
        expected_method_name = 'bad'
        expected_msg_args = ('title', 'content')
        expected_ex_msg = str(ValueError(f'messagebox method {expected_method_name} does not exist'))

        actual_dialog = self.test_init(return_instance=True)
        with self.assertRaises(ValueError) as ex_context:
            actual_dialog._open_messagebox(expected_method_name, *expected_msg_args)
        self.assertEqual(str(ex_context.exception), expected_ex_msg)

    @patch(f'{MODULE_PATH}.QDesktopServices.openUrl')
    @patch(f'{MODULE_PATH}.QUrl')
    def test_edl_link_clicked(self, mock_QUrl, mock_openUrl):
        expected_link = 'http://somewhere.com'
        expected_qurl = 'l'
        mock_QUrl.return_value = expected_qurl

        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.edl_link_clicked(expected_link)

        mock_QUrl.assert_called_with(expected_link)
        mock_openUrl.assert_called_with(expected_qurl)

    def test_toggle_password_visibility_checked(self):
        expected_checked = True
        expected_le = Mock()
        expected_le.setEchoMode = Mock()
        expected_mode = QtWidgets.QLineEdit.Normal

        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.password_lineEdit = expected_le
        actual_dialog.toggle_password_visibility(expected_checked)

        expected_le.setEchoMode.assert_called_with(expected_mode)

    def test_toggle_password_visibility_not_checked(self):
        expected_checked = False
        expected_le = Mock()
        expected_le.setEchoMode = Mock()
        expected_mode = QtWidgets.QLineEdit.Password

        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.password_lineEdit = expected_le
        actual_dialog.toggle_password_visibility(expected_checked)

        expected_le.setEchoMode.assert_called_with(expected_mode)

    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    @patch(f'plugin.netrc.store_creds')
    def test_store_entered_credentials(self, mock_store_creds, mock_open_messagebox):
        expected_user, expected_pw = 'u', 'p'
        mock_ule = Mock()
        mock_ule.text = Mock(return_value=expected_user)
        mock_ple = Mock()
        mock_ple.text = Mock(return_value=expected_pw)
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.username_lineEdit = mock_ule
        actual_dialog.password_lineEdit = mock_ple
        expected_machine = actual_dialog.machine
        expected_msgbox_args = (
            "information", "Credentials Updated",
            f"Credentials for '{expected_machine}' stored successfully."
        )

        actual_dialog.store_entered_credentials()

        mock_store_creds.assert_called_with(
            expected_machine, expected_user, expected_pw
        )
        mock_open_messagebox.assert_called_with(*expected_msgbox_args)

    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    @patch(f'plugin.netrc.store_creds')
    def test_store_entered_credentials_already_exist_no_overwrite(self, mock_store_creds, mock_open_messagebox):
        expected_user, expected_pw = 'u', 'p'
        mock_ule = Mock()
        mock_ule.text = Mock(return_value=expected_user)
        mock_ple = Mock()
        mock_ple.text = Mock(return_value=expected_pw)
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.username_lineEdit = mock_ule
        actual_dialog.password_lineEdit = mock_ple
        expected_machine = actual_dialog.machine
        expected_msgbox_args = (
            "question", "Credentials Exist",
            f"Credentials for '{expected_machine}' already exist.  Overwrite them?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No
        )
        mock_open_messagebox.return_value = QtWidgets.QMessageBox.No
        mock_store_creds.side_effect = netrc.ConflictError('err')

        actual_dialog.store_entered_credentials()

        mock_store_creds.assert_called_with(
            expected_machine, expected_user, expected_pw
        )
        mock_open_messagebox.assert_called_with(*expected_msgbox_args)

    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    @patch(f'plugin.netrc.store_creds')
    def test_store_entered_credentials_already_exist_no_overwrite_error(self, mock_store_creds, mock_open_messagebox):
        expected_user, expected_pw = 'u', 'p'
        mock_ule = Mock()
        mock_ule.text = Mock(return_value=expected_user)
        mock_ple = Mock()
        mock_ple.text = Mock(return_value=expected_pw)
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.username_lineEdit = mock_ule
        actual_dialog.password_lineEdit = mock_ple
        expected_machine = actual_dialog.machine
        expected_ex = Exception('err')
        expected_msgbox_args = (
            "critical", "Error", str(expected_ex)
        )
        mock_open_messagebox.return_value = QtWidgets.QMessageBox.No
        
        mock_store_creds.side_effect = expected_ex

        actual_dialog.store_entered_credentials()

        mock_store_creds.assert_called_with(
            expected_machine, expected_user, expected_pw
        )
        mock_open_messagebox.assert_called_with(*expected_msgbox_args)

    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    @patch(f'plugin.netrc.store_creds')
    def test_store_entered_credentials_already_exist_overwrite(self, mock_store_creds, mock_open_messagebox):
        expected_user, expected_pw = 'u', 'p'
        mock_ule = Mock()
        mock_ule.text = Mock(return_value=expected_user)
        mock_ple = Mock()
        mock_ple.text = Mock(return_value=expected_pw)
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.username_lineEdit = mock_ule
        actual_dialog.password_lineEdit = mock_ple
        expected_machine = actual_dialog.machine
        expected_msgbox_args_1 = (
            "question", "Credentials Exist",
            f"Credentials for '{expected_machine}' already exist.  Overwrite them?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No
        )
        expected_msgbox_args_2 = (
            "information", "Credentials Updated",
            f"Credentials for '{expected_machine}' updated successfully."
        )
        mock_open_messagebox.return_value = QtWidgets.QMessageBox.Yes
        mock_store_creds.side_effect = [netrc.ConflictError('err'), None]

        actual_dialog.store_entered_credentials()

        mock_store_creds.call_args_list[0].assert_called_with(
            expected_machine, expected_user, expected_pw
        )
        mock_store_creds.call_args_list[1].assert_called_with(
            expected_machine, expected_user, expected_pw, force_update=True
        )
        mock_open_messagebox.call_args_list[0].assert_called_with(*expected_msgbox_args_1)
        mock_open_messagebox.call_args_list[1].assert_called_with(*expected_msgbox_args_2)

    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    @patch(f'plugin.netrc.store_creds')
    def test_store_entered_credentials_already_exist_overwrite_error(self, mock_store_creds, mock_open_messagebox):
        expected_user, expected_pw = 'u', 'p'
        mock_ule = Mock()
        mock_ule.text = Mock(return_value=expected_user)
        mock_ple = Mock()
        mock_ple.text = Mock(return_value=expected_pw)
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.username_lineEdit = mock_ule
        actual_dialog.password_lineEdit = mock_ple
        expected_machine = actual_dialog.machine
        expected_msgbox_args_1 = (
            "question", "Credentials Exist",
            f"Credentials for '{expected_machine}' already exist.  Overwrite them?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No
        )
        expected_store_ex = Exception('err')
        expected_msgbox_args_2 = (
            "critical", "Error", str(expected_store_ex)
        )
        mock_open_messagebox.return_value = QtWidgets.QMessageBox.Yes
        mock_store_creds.side_effect = [netrc.ConflictError('err'), expected_store_ex]

        actual_dialog.store_entered_credentials()

        mock_store_creds.call_args_list[0].assert_called_with(
            expected_machine, expected_user, expected_pw
        )
        mock_store_creds.call_args_list[1].assert_called_with(
            expected_machine, expected_user, expected_pw, force_update=True
        )
        mock_open_messagebox.call_args_list[0].assert_called_with(*expected_msgbox_args_1)
        mock_open_messagebox.call_args_list[1].assert_called_with(*expected_msgbox_args_2)

    def test_filter_tasks(self):
        expected_tasks = [
            {'task_type': 'area', 'params': {'output': {'format': {'type': 'geotiff'}}}},
            {'task_type': 'point'}
        ]
        expected_filtered_tasks = [expected_tasks[0]]
        actual_dialog = self.test_init(return_instance=True)

        actual_tasks = actual_dialog._filter_tasks(expected_tasks)

        self.assertEqual(actual_tasks, expected_filtered_tasks)

    def test_filter_bundle_files(self):
        expected_files = [{'file_type': 'tif'}, {'file_type': 'md'}]
        expected_filtered_files = [expected_files[0]]
        actual_dialog = self.test_init(return_instance=True)

        actual_files = actual_dialog._filter_bundle_files(expected_files)

        self.assertEqual(actual_files, expected_filtered_files)

    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    @patch(f'plugin.netrc.retrieve_creds')
    def test_refresh_tasks_no_creds(self, mock_retrieve_creds, mock_open_messagebox):
        mock_retrieve_creds.return_value = (None, None)
        actual_dialog = self.test_init(return_instance=True)
        expected_machine = actual_dialog.machine
        expected_mb_args = (
            "warning", "No Credentials", f"No credentials",
            f"No credentials found for {expected_machine}. Please enter credentials on the login tab."
        )
        
        actual_dialog.refresh_tasks()

        mock_retrieve_creds.assert_called_with(expected_machine)
        mock_open_messagebox.assert_called_with(*expected_mb_args)

    @patch(f'{MODULE_PATH}.Dialog.populate_table')
    @patch(f'{MODULE_PATH}.Dialog._filter_tasks')
    @patch(f'plugin.api.Client')
    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    @patch(f'plugin.netrc.retrieve_creds')
    def test_refresh_tasks(
        self, mock_retrieve_creds, mock_open_messagebox, mock_Client,
        mock_filter_tasks, mock_populate_table
    ):
        expected_user, expected_pw = 'u', 'p'
        mock_retrieve_creds.return_value = (expected_user, expected_pw)
        actual_dialog = self.test_init(return_instance=True)
        expected_machine = actual_dialog.machine
        expected_api_client = Mock()
        expected_tasks = [{}]
        expected_api_client.fetch_task_data = Mock(return_value=expected_tasks)
        mock_filter_tasks.return_value = expected_tasks
        mock_Client.return_value = expected_api_client
        
        actual_dialog.refresh_tasks()

        mock_retrieve_creds.assert_called_with(expected_machine)
        mock_open_messagebox.assert_not_called()
        expected_api_client.fetch_task_data.assert_called_with()
        mock_filter_tasks.assert_called_with(expected_tasks)
        mock_populate_table.assert_called_with(expected_tasks)

    @patch(f'{MODULE_PATH}.Dialog.populate_table')
    @patch(f'{MODULE_PATH}.Dialog._filter_tasks')
    @patch(f'plugin.api.Client')
    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    @patch(f'plugin.netrc.retrieve_creds')
    def test_refresh_tasks_api_client_exists(
        self, mock_retrieve_creds, mock_open_messagebox, mock_Client,
        mock_filter_tasks, mock_populate_table
    ):
        expected_user, expected_pw = 'u', 'p'
        mock_retrieve_creds.return_value = (expected_user, expected_pw)
        actual_dialog = self.test_init(return_instance=True)
        expected_machine = actual_dialog.machine
        expected_api_client = Mock()
        expected_tasks = [{}]
        expected_api_client.update_creds = Mock()
        expected_api_client.fetch_task_data = Mock(return_value=expected_tasks)
        mock_filter_tasks.return_value = expected_tasks
        actual_dialog.api = expected_api_client
        
        actual_dialog.refresh_tasks()

        mock_retrieve_creds.assert_called_with(expected_machine)
        mock_open_messagebox.assert_not_called()
        expected_api_client.update_creds.assert_called_with((expected_user, expected_pw))
        expected_api_client.fetch_task_data.assert_called_with()
        mock_filter_tasks.assert_called_with(expected_tasks)
        mock_populate_table.assert_called_with(expected_tasks)

    @patch(f'{MODULE_PATH}.Dialog.populate_table')
    @patch(f'{MODULE_PATH}.Dialog._filter_tasks')
    @patch(f'plugin.api.Client')
    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    @patch(f'plugin.netrc.retrieve_creds')
    def test_refresh_tasks_none_found(
        self, mock_retrieve_creds, mock_open_messagebox, mock_Client,
        mock_filter_tasks, mock_populate_table
    ):
        expected_user, expected_pw = 'u', 'p'
        mock_retrieve_creds.return_value = (expected_user, expected_pw)
        actual_dialog = self.test_init(return_instance=True)
        expected_machine = actual_dialog.machine
        expected_api_client = Mock()
        expected_tasks = []
        expected_api_client.fetch_task_data = Mock(return_value=expected_tasks)
        mock_filter_tasks.return_value = expected_tasks
        mock_Client.return_value = expected_api_client
        
        actual_dialog.refresh_tasks()

        mock_retrieve_creds.assert_called_with(expected_machine)
        mock_open_messagebox.assert_not_called()
        expected_api_client.fetch_task_data.assert_called_with()
        mock_filter_tasks.assert_called_with(expected_tasks)
        mock_populate_table.assert_not_called()

    @patch(f'{MODULE_PATH}.Dialog.populate_table')
    @patch(f'{MODULE_PATH}.Dialog._filter_tasks')
    @patch(f'plugin.api.Client')
    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    @patch(f'plugin.netrc.retrieve_creds')
    def test_refresh_tasks_api_error(
        self, mock_retrieve_creds, mock_open_messagebox, mock_Client,
        mock_filter_tasks, mock_populate_table
    ):
        expected_user, expected_pw = 'u', 'p'
        mock_retrieve_creds.return_value = (expected_user, expected_pw)
        actual_dialog = self.test_init(return_instance=True)
        expected_machine = actual_dialog.machine
        expected_api_client = Mock()
        expected_tasks = []
        expected_api_ex = api.ApiError('err')
        expected_api_client.fetch_task_data = Mock(side_effect=expected_api_ex)
        mock_Client.return_value = expected_api_client
        expected_mb_args = (
            "warning", "Error",
            "Data could not be retrieved from the AppEEARS API. Please check your credentials."
        )
        
        actual_dialog.refresh_tasks()

        mock_retrieve_creds.assert_called_with(expected_machine)
        expected_api_client.fetch_task_data.assert_called_with()
        mock_open_messagebox.assert_called_with(*expected_mb_args)
        mock_filter_tasks.not_called()
        mock_populate_table.assert_not_called()

    @patch(f'{MODULE_PATH}.QtWidgets.QTableWidgetItem')
    def test_populate_table(self, mock_QTableWidgetItem):
        expected_data_list = [
            {'task_name': 't', 'status': 's', 'task_type': 'a', 'task_id': '1'}
        ]
        mock_table_widget = Mock()
        mock_table_widget.clearContents = Mock()
        mock_table_widget.setRowCount = Mock()
        mock_table_widget.setColumnCount = Mock()
        mock_table_widget.setHorizontalHeaderLabels = Mock()
        mock_table_widget.setItem = Mock()
        mock_table_widget.resizeColumnsToContents = Mock()
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.task_tableWidget = mock_table_widget

        actual_dialog.populate_table(expected_data_list)

        mock_table_widget.clearContents.assert_called_with()
        mock_table_widget.setRowCount(len(expected_data_list))
        mock_table_widget.setColumnCount.assert_called_with(len(expected_data_list[0].keys()))
        mock_table_widget.setHorizontalHeaderLabels.assert_called_with(
            list(expected_data_list[0].keys())
        )
        col_proc_count = 0
        for i, t in enumerate(expected_data_list):
            for ci, col in enumerate(t.keys()):
                mock_QTableWidgetItem.call_args_list[col_proc_count].assert_called_with(str(t[col]))
                mock_table_widget.setItem.call_args_list[col_proc_count].assert_called_with(i, ci, t)
        mock_table_widget.resizeColumnsToContents.assert_called_with()

    def test_select_task_no_row_selected(self):
        mock_table_widget = Mock()
        expected_row_idx = -1
        mock_table_widget.currentRow = Mock(return_value=expected_row_idx)
        mock_table_widget.item = Mock()
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.task_tableWidget = mock_table_widget

        actual_dialog.select_task()

        mock_table_widget.currentRow.assert_called_with()
        mock_table_widget.item.assert_not_called()

    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    def test_select_task_no_current_task(self, mock_open_messagebox):
        mock_table_widget = Mock()
        expected_row_idx = 1
        mock_table_widget.currentRow = Mock(return_value=expected_row_idx)
        expected_task_id = None
        expected_item_ret_1 = Mock()
        expected_item_ret_1.text = Mock(return_value=expected_task_id)
        expected_status = None
        expected_item_ret_2 = Mock()
        expected_item_ret_2.text = Mock(return_value=expected_status)
        mock_table_widget.item = Mock(side_effect=[expected_item_ret_1, expected_item_ret_2])
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.task_tableWidget = mock_table_widget
        expected_mb_args = (
            "warning", "Invalid Row", "Could not find task."
        )

        actual_dialog.select_task()

        mock_table_widget.currentRow.assert_called_with()
        mock_table_widget.item.call_args_list[0].assert_called_with(expected_row_idx, 3)
        expected_item_ret_1.text.assert_called_with()
        mock_table_widget.item.call_args_list[1].assert_called_with(expected_row_idx, 1)
        expected_item_ret_2.text.assert_called_with()
        mock_open_messagebox.assert_called_with(*expected_mb_args)

    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    def test_select_task_current_task_not_done(self, mock_open_messagebox):
        mock_table_widget = Mock()
        expected_row_idx = 1
        mock_table_widget.currentRow = Mock(return_value=expected_row_idx)
        expected_task_id = '1'
        expected_item_ret_1 = Mock()
        expected_item_ret_1.text = Mock(return_value=expected_task_id)
        expected_status = 'processing'
        expected_item_ret_2 = Mock()
        expected_item_ret_2.text = Mock(return_value=expected_status)
        mock_table_widget.item = Mock(side_effect=[expected_item_ret_1, expected_item_ret_2])
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.task_tableWidget = mock_table_widget
        expected_mb_args = (
            "information", "Task Not Done",
            f"This task is '{expected_status}' and cannot be selected."
        )

        actual_dialog.select_task()

        mock_table_widget.currentRow.assert_called_with()
        mock_table_widget.item.call_args_list[0].assert_called_with(expected_row_idx, 3)
        expected_item_ret_1.text.assert_called_with()
        mock_table_widget.item.call_args_list[1].assert_called_with(expected_row_idx, 1)
        expected_item_ret_2.text.assert_called_with()
        mock_open_messagebox.assert_called_with(*expected_mb_args)

    @patch(f'{MODULE_PATH}.Dialog._filter_bundle_files')
    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    def test_select_task_api_error(self, mock_open_messagebox, mock_filter_bundle_files):
        mock_table_widget = Mock()
        expected_row_idx = 1
        mock_table_widget.currentRow = Mock(return_value=expected_row_idx)
        expected_task_id = '1'
        expected_item_ret_1 = Mock()
        expected_item_ret_1.text = Mock(return_value=expected_task_id)
        expected_status = 'done'
        expected_item_ret_2 = Mock()
        expected_item_ret_2.text = Mock(return_value=expected_status)
        mock_table_widget.item = Mock(side_effect=[expected_item_ret_1, expected_item_ret_2])
        mock_api_client = Mock()
        expected_ex = api.ApiError('err')
        mock_api_client.fetch_bundle_data = Mock(side_effect=expected_ex)
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.task_tableWidget = mock_table_widget
        actual_dialog.api = mock_api_client
        expected_mb_args = (
            "warning", "Error",
            "Data could not be retrieved from the AppEEARS API. Please check your credentials."
        )

        actual_dialog.select_task()

        mock_table_widget.currentRow.assert_called_with()
        mock_table_widget.item.call_args_list[0].assert_called_with(expected_row_idx, 3)
        expected_item_ret_1.text.assert_called_with()
        mock_table_widget.item.call_args_list[1].assert_called_with(expected_row_idx, 1)
        expected_item_ret_2.text.assert_called_with()
        mock_api_client.fetch_bundle_data.assert_called_with(expected_task_id)
        mock_filter_bundle_files.assert_not_called()
        mock_open_messagebox.assert_called_with(*expected_mb_args)

    @patch(f'{MODULE_PATH}.Dialog._filter_bundle_files')
    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    def test_select_task_no_data(self, mock_open_messagebox, mock_filter_bundle_files):
        mock_table_widget = Mock()
        expected_row_idx = 1
        mock_table_widget.currentRow = Mock(return_value=expected_row_idx)
        expected_task_id = '1'
        expected_item_ret_1 = Mock()
        expected_item_ret_1.text = Mock(return_value=expected_task_id)
        expected_status = 'done'
        expected_item_ret_2 = Mock()
        expected_item_ret_2.text = Mock(return_value=expected_status)
        mock_table_widget.item = Mock(side_effect=[expected_item_ret_1, expected_item_ret_2])
        mock_api_client = Mock()
        expected_files = []
        mock_filter_bundle_files.return_value = expected_files
        mock_api_client.fetch_bundle_data = Mock(return_value=expected_files)
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.task_tableWidget = mock_table_widget
        actual_dialog.api = mock_api_client
        actual_dialog.populate_bundle_table = Mock()

        actual_dialog.select_task()

        mock_table_widget.currentRow.assert_called_with()
        mock_table_widget.item.call_args_list[0].assert_called_with(expected_row_idx, 3)
        expected_item_ret_1.text.assert_called_with()
        mock_table_widget.item.call_args_list[1].assert_called_with(expected_row_idx, 1)
        expected_item_ret_2.text.assert_called_with()
        mock_api_client.fetch_bundle_data.assert_called_with(expected_task_id)
        mock_filter_bundle_files.assert_called_with(expected_files)
        actual_dialog.populate_bundle_table.assert_called_with(expected_files)
        mock_open_messagebox.assert_not_called()

    @patch(f'{MODULE_PATH}.Dialog._filter_bundle_files')
    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    def test_select_task(self, mock_open_messagebox, mock_filter_bundle_files):
        mock_table_widget = Mock()
        expected_row_idx = 1
        mock_table_widget.currentRow = Mock(return_value=expected_row_idx)
        expected_task_id = '1'
        expected_item_ret_1 = Mock()
        expected_item_ret_1.text = Mock(return_value=expected_task_id)
        expected_status = 'done'
        expected_item_ret_2 = Mock()
        expected_item_ret_2.text = Mock(return_value=expected_status)
        mock_table_widget.item = Mock(side_effect=[expected_item_ret_1, expected_item_ret_2])
        mock_api_client = Mock()
        expected_files = [{}]
        mock_filter_bundle_files.return_value = expected_files
        mock_api_client.fetch_bundle_data = Mock(return_value=expected_files)
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.task_tableWidget = mock_table_widget
        actual_dialog.api = mock_api_client
        actual_dialog.populate_bundle_table = Mock()
        expected_mb_args = (
            "warning", "Error",
            "Data could not be retrieved from the AppEEARS API. Please check your credentials."
        )

        actual_dialog.select_task()

        mock_table_widget.currentRow.assert_called_with()
        mock_table_widget.item.call_args_list[0].assert_called_with(expected_row_idx, 3)
        expected_item_ret_1.text.assert_called_with()
        mock_table_widget.item.call_args_list[1].assert_called_with(expected_row_idx, 1)
        expected_item_ret_2.text.assert_called_with()
        mock_api_client.fetch_bundle_data.assert_called_with(expected_task_id)
        mock_filter_bundle_files.assert_called_with(expected_files)
        actual_dialog.populate_bundle_table.assert_called_with(expected_files)
        mock_open_messagebox.assert_not_called()

    @patch(f'{MODULE_PATH}.QtWidgets.QTableWidgetItem')
    def test_populate_bundle_table(self, mock_QTableWidgetItem):
        expected_data_list = [
            {'file_name': 'f', 'file_id': '1', 'file_size': 1}
        ]
        mock_table_widget = Mock()
        mock_table_widget.clearContents = Mock()
        mock_table_widget.setRowCount = Mock()
        mock_table_widget.setColumnCount = Mock()
        mock_table_widget.setHorizontalHeaderLabels = Mock()
        mock_table_widget.setItem = Mock()
        mock_table_widget.resizeColumnsToContents = Mock()
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.bundle_tableWidget = mock_table_widget

        actual_dialog.populate_bundle_table(expected_data_list)

        mock_table_widget.clearContents.assert_called_with()
        mock_table_widget.setRowCount(len(expected_data_list))
        mock_table_widget.setColumnCount.assert_called_with(len(expected_data_list[0].keys()))
        mock_table_widget.setHorizontalHeaderLabels.assert_called_with(
            list(expected_data_list[0].keys())
        )
        col_proc_count = 0
        for i, t in enumerate(expected_data_list):
            for ci, col in enumerate(t.keys()):
                mock_QTableWidgetItem.call_args_list[col_proc_count].assert_called_with(str(t[col]))
                mock_table_widget.setItem.call_args_list[col_proc_count].assert_called_with(i, ci, t)
        mock_table_widget.resizeColumnsToContents.assert_called_with()

    def test_load_selected_file_none_selected(self):
        expected_row_idx = -1
        mock_table_widget = Mock()
        mock_table_widget.currentRow = Mock(return_value=expected_row_idx)
        mock_table_widget.item = Mock()
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.bundle_tableWidget = mock_table_widget

        actual_dialog.load_selected_file()

        mock_table_widget.currentRow.assert_called_with()
        mock_table_widget.item.assert_not_called()

    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    def test_load_selected_file_no_file_id(self, mock_open_messagebox):
        expected_row_idx = 1
        mock_table_widget = Mock()
        mock_table_widget.currentRow = Mock(return_value=expected_row_idx)
        expected_file_id = None
        expected_file_name = None
        expected_item_ret_1 = Mock()
        expected_item_ret_1.text = Mock(return_value=expected_file_id)
        expected_status = 'done'
        expected_item_ret_2 = Mock()
        expected_item_ret_2.text = Mock(return_value=expected_file_name)
        mock_table_widget.item = Mock(side_effect=[expected_item_ret_1, expected_item_ret_2])
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.bundle_tableWidget = mock_table_widget
        expected_mb_args = (
            "warning", "Invalid Row", "Could not find task."
        )

        actual_dialog.load_selected_file()

        mock_table_widget.currentRow.assert_called_with()
        mock_table_widget.item.call_args_list[0].assert_called_with(expected_row_idx, 1)
        expected_item_ret_1.text.assert_called_with()
        mock_table_widget.item.call_args_list[1].assert_called_with(expected_row_idx, 0)
        expected_item_ret_2.text.assert_called_with()
        mock_open_messagebox.assert_called_with(*expected_mb_args)

    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    def test_load_selected_file_unsupported_file(self, mock_open_messagebox):
        expected_row_idx = 1
        mock_table_widget = Mock()
        mock_table_widget.currentRow = Mock(return_value=expected_row_idx)
        expected_task_id = '1'
        expected_file_id = '1'
        expected_file_name = 'f'
        expected_item_ret_1 = Mock()
        expected_item_ret_1.text = Mock(return_value=expected_file_id)
        expected_status = 'done'
        expected_item_ret_2 = Mock()
        expected_item_ret_2.text = Mock(return_value=expected_file_name)
        mock_table_widget.item = Mock(side_effect=[expected_item_ret_1, expected_item_ret_2])
        expected_api_client = Mock()
        expected_file_url = 'u'
        expected_api_client.build_file_url = Mock(return_value=expected_file_url)
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.bundle_tableWidget = mock_table_widget
        actual_dialog.current_task_id = expected_task_id
        actual_dialog.api = expected_api_client
        expected_mb_args = (
            "critical", "Error", (
                "Currently this plugin shows all AppEEARS requests and output filetypes, "
                "but only supports opening cloud-optimized geotiff files from area task requests."
            )
        )

        actual_dialog.load_selected_file()

        mock_table_widget.currentRow.assert_called_with()
        mock_table_widget.item.call_args_list[0].assert_called_with(expected_row_idx, 1)
        expected_item_ret_1.text.assert_called_with()
        mock_table_widget.item.call_args_list[1].assert_called_with(expected_row_idx, 0)
        expected_item_ret_2.text.assert_called_with()
        expected_api_client.build_file_url.assert_called_with(
            expected_task_id, expected_file_id, expected_file_name
        )
        mock_open_messagebox.assert_called_with(*expected_mb_args)

    @patch('plugin.util.set_gdal_options')
    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    def test_load_selected_file_api_error(self, mock_open_messagebox, mock_set_gdal_options):
        expected_row_idx = 1
        mock_table_widget = Mock()
        mock_table_widget.currentRow = Mock(return_value=expected_row_idx)
        expected_task_id = '1'
        expected_file_id = '1'
        expected_file_name = 'f'
        expected_item_ret_1 = Mock()
        expected_item_ret_1.text = Mock(return_value=expected_file_id)
        expected_status = 'done'
        expected_item_ret_2 = Mock()
        expected_item_ret_2.text = Mock(return_value=expected_file_name)
        mock_table_widget.item = Mock(side_effect=[expected_item_ret_1, expected_item_ret_2])
        expected_api_client = Mock()
        expected_file_url = 'u'
        expected_api_client.build_file_url = Mock(side_effect=api.ApiError('err'))
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.bundle_tableWidget = mock_table_widget
        actual_dialog.current_task_id = expected_task_id
        actual_dialog.api = expected_api_client

        actual_dialog.load_selected_file()

        mock_table_widget.currentRow.assert_called_with()
        mock_table_widget.item.call_args_list[0].assert_called_with(expected_row_idx, 1)
        expected_item_ret_1.text.assert_called_with()
        mock_table_widget.item.call_args_list[1].assert_called_with(expected_row_idx, 0)
        expected_item_ret_2.text.assert_called_with()
        expected_api_client.build_file_url.assert_called_with(
            expected_task_id, expected_file_id, expected_file_name
        )
        mock_open_messagebox.assert_not_called()
        mock_set_gdal_options.assert_not_called()

    @patch(f'{MODULE_PATH}.QgsProject.instance')
    @patch(f'{MODULE_PATH}.QgsRasterLayer')
    @patch('plugin.util.set_gdal_options')
    @patch(f'{MODULE_PATH}.Dialog._open_messagebox')
    def test_load_selected_file(
        self, mock_open_messagebox, mock_set_gdal_options, mock_QgsRasterLayer, mock_instance
    ):
        expected_row_idx = 1
        mock_table_widget = Mock()
        mock_table_widget.currentRow = Mock(return_value=expected_row_idx)
        expected_task_id = '1'
        expected_file_id = '1'
        expected_file_name = 'f'
        expected_item_ret_1 = Mock()
        expected_item_ret_1.text = Mock(return_value=expected_file_id)
        expected_status = 'done'
        expected_item_ret_2 = Mock()
        expected_item_ret_2.text = Mock(return_value=expected_file_name)
        mock_table_widget.item = Mock(side_effect=[expected_item_ret_1, expected_item_ret_2])
        expected_api_client = Mock()
        expected_file_url = 'file.tif'
        expected_api_client.build_file_url = Mock(return_value=expected_file_url)
        expected_token = '1'
        expected_api_client.token = expected_token
        actual_dialog = self.test_init(return_instance=True)
        actual_dialog.bundle_tableWidget = mock_table_widget
        actual_dialog.current_task_id = expected_task_id
        actual_dialog.api = expected_api_client
        expected_raster_layer = 'l'
        mock_QgsRasterLayer.return_value = expected_raster_layer
        expected_proj_instance = Mock()
        expected_proj_instance.addMapLayer = Mock()
        mock_instance.return_value = expected_proj_instance

        actual_dialog.load_selected_file()

        mock_table_widget.currentRow.assert_called_with()
        mock_table_widget.item.call_args_list[0].assert_called_with(expected_row_idx, 1)
        expected_item_ret_1.text.assert_called_with()
        mock_table_widget.item.call_args_list[1].assert_called_with(expected_row_idx, 0)
        expected_item_ret_2.text.assert_called_with()
        expected_api_client.build_file_url.assert_called_with(
            expected_task_id, expected_file_id, expected_file_name
        )
        mock_open_messagebox.assert_not_called()
        mock_set_gdal_options.assert_called_with(expected_token)
        mock_QgsRasterLayer.assert_called_with(expected_file_url, expected_file_name)
        expected_proj_instance.addMapLayer.assert_called_with(expected_raster_layer)
    

