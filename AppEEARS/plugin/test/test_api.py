import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, Mock, PropertyMock
from plugin import api

MODULE_PATH = 'plugin.api'

class ClientTest(unittest.TestCase):

    def _get_client(self, creds=('user', 'pw')):
        return api.Client(creds)

    def test_init(self):
        expected_creds = ('steve', 'steves_pw')
        actual_client = self._get_client(creds=expected_creds)

        self.assertEqual(actual_client._creds, expected_creds)

    @patch('requests.post')
    def test_handle_token(self, mock_post):
        expected_creds = ('user', 'pw')
        expected_resp = Mock()
        expected_resp.status_code = 200
        expected_token = '123'
        expected_expire = datetime.now().replace(microsecond=0) + timedelta(days=2)
        expected_expire_str = expected_expire.strftime('%Y-%m-%dT%H:%M:%SZ')
        expected_token_exp = expected_expire.replace(tzinfo=timezone.utc)
        expected_data = {
            'token': expected_token,
            'expiration': expected_expire_str
        }
        expected_resp.json = Mock(return_value=expected_data)
        mock_post.return_value = expected_resp

        actual_client = self._get_client(creds=expected_creds)
        expected_login_url = f'{actual_client._url}login'
        actual_client._handle_token()

        mock_post.assert_called_with(expected_login_url, auth=expected_creds)
        self.assertEqual(actual_client._token, expected_token)
        self.assertEqual(actual_client._token_exp, expected_token_exp)

    @patch('requests.post')
    def test_handle_token_no_data(self, mock_post):
        expected_creds = ('user', 'pw')
        expected_resp = Mock()
        expected_resp.status_code = 200
        expected_token = None
        expected_data = {
            'token': expected_token
        }
        expected_resp.json = Mock(return_value=expected_data)
        mock_post.return_value = expected_resp

        actual_client = self._get_client(creds=expected_creds)

        with self.assertRaises(api.LoginError):
            actual_client._handle_token()

    @patch('requests.post')
    def test_handle_token_bad_api_response(self, mock_post):
        expected_creds = ('user', 'pw')
        expected_resp = Mock()
        expected_resp.status_code = 500
        mock_post.return_value = expected_resp

        actual_client = self._get_client(creds=expected_creds)

        with self.assertRaises(api.LoginError):
            actual_client._handle_token()

    @patch(f'{MODULE_PATH}.Client._handle_token')
    def test_token(self, mock_handle_token):
        expected_creds = ('user', 'pw')
        expected_token = None

        actual_client = self._get_client(creds=expected_creds)
        actual_token = actual_client.token

        mock_handle_token.assert_called_with()
        self.assertEqual(actual_token, expected_token)

    def test_update_creds(self):
        expected_creds = ('steve', 'pw')
        expected_new_creds = ('joe', 'pw')

        actual_client = self._get_client(creds=expected_creds)
        actual_client.update_creds(expected_new_creds)

        self.assertEqual(actual_client._creds, expected_new_creds)

    @patch(f'{MODULE_PATH}.Client.token', new_callable=PropertyMock)
    def test_get_auth_header(self, mock_token):
        expected_token = '123'
        mock_token.return_value = expected_token
        expected_header = {'Authorization': f'Bearer {expected_token}'}

        actual_client = self._get_client()

        self.assertEqual(actual_client._get_auth_header(), expected_header)

    @patch(f'{MODULE_PATH}.Client._get_auth_header')
    @patch('requests.get')
    def test_fetch_task_data_max_reached(self, mock_get, mock_get_auth_header):
        expected_auth_hdr = {}
        mock_get_auth_header.return_value = expected_auth_hdr
        expected_max = 15
        expected_resp_1 = Mock()
        expected_resp_1.status_code = 200
        expected_tasks_1 = [{}] * (expected_max + 1)
        expected_resp_1.json = Mock(return_value=expected_tasks_1)
        mock_get.return_value = expected_resp_1

        actual_client = self._get_client()
        actual_tasks = list(actual_client.fetch_task_data(max=expected_max))

        mock_get_auth_header.assert_called_with()
        mock_get.assert_called_with(
            f'{actual_client._url}task?limit=1000&offset=0',
            headers=expected_auth_hdr
        )
        expected_resp_1.json.assert_called_with()
        self.assertEqual(len(actual_tasks), expected_max)

    @patch(f'{MODULE_PATH}.Client._get_auth_header')
    @patch('requests.get')
    def test_fetch_task_data_all_consumed(self, mock_get, mock_get_auth_header):
        expected_limit = 1000
        expected_auth_hdr = {}
        mock_get_auth_header.return_value = expected_auth_hdr
        expected_resp_1 = Mock()
        expected_resp_1.status_code = 200
        expected_tasks_1 = [{}] * (expected_limit)
        expected_resp_1.json = Mock(return_value=expected_tasks_1)
        expected_resp_2 = Mock()
        expected_resp_2.status_code = 200
        expected_tasks_2 = [{}] * 1
        expected_resp_2.json = Mock(return_value=expected_tasks_2)
        mock_get.side_effect = [expected_resp_1, expected_resp_2]

        actual_client = self._get_client()
        actual_tasks = list(actual_client.fetch_task_data())

        mock_get_auth_header.assert_called_with()
        mock_get.call_args_list[0].assert_called_with(
            f'{actual_client._url}task?limit={expected_limit}&offset=0',
            headers=expected_auth_hdr
        )
        mock_get.call_args_list[1].assert_called_with(
            f'{actual_client._url}task?limit={expected_limit}&offset=1',
            headers=expected_auth_hdr
        )
        expected_resp_1.json.assert_called_with()
        expected_resp_2.json.assert_called_with()
        self.assertEqual(len(actual_tasks), len(expected_tasks_1) + len(expected_tasks_2))

    @patch(f'{MODULE_PATH}.Client._get_auth_header')
    @patch('requests.get')
    def test_fetch_task_data_login_error(self, mock_get, mock_get_auth_header):
        expected_ex = api.LoginError('cannot login')
        mock_get_auth_header.side_effect = expected_ex

        actual_client = self._get_client()
        
        with self.assertRaises(api.ApiError) as ex_context:
            list(actual_client.fetch_task_data())

        mock_get_auth_header.assert_called_with()
        mock_get.assert_not_called()
        self.assertEqual(str(ex_context.exception), str(expected_ex))

    @patch(f'{MODULE_PATH}.Client._get_auth_header')
    @patch('requests.get')
    def test_fetch_task_data_misc_error(self, mock_get, mock_get_auth_header):
        expected_auth_hdr = {}
        mock_get_auth_header.return_value = expected_auth_hdr
        expected_ex = RuntimeError('some requests err')
        mock_get.side_effect = expected_ex

        actual_client = self._get_client()
        with self.assertRaises(api.DataRetrivalError) as ex_context:
            list(actual_client.fetch_task_data())

        mock_get_auth_header.assert_called_with()
        mock_get.assert_called_once()
        self.assertEqual(str(ex_context.exception), str(expected_ex))

    @patch(f'{MODULE_PATH}.Client._get_auth_header')
    @patch('requests.get')
    def test_fetch_bundle_data(self, mock_get, mock_get_auth_header):
        expected_task_id = '1'
        expected_auth_hdr = {}
        mock_get_auth_header.return_value = expected_auth_hdr
        expected_resp = Mock()
        expected_resp.status_code = 200
        expected_files = [{'name': 'file1'}, {'name': 'file2'}]
        expected_data = {'files': expected_files}
        expected_resp.json = Mock(return_value=expected_data)
        mock_get.return_value = expected_resp

        actual_client = self._get_client()
        actual_data = actual_client.fetch_bundle_data(expected_task_id)

        mock_get.assert_called_with(
            f'{actual_client._url}bundle/{expected_task_id}',
            headers=expected_auth_hdr
        )
        self.assertEqual(actual_data, expected_files)

    @patch(f'{MODULE_PATH}.Client._get_auth_header')
    @patch('requests.get')
    def test_fetch_bundle_data_nothing_exists(self, mock_get, mock_get_auth_header):
        expected_task_id = '1'
        expected_auth_hdr = {}
        mock_get_auth_header.return_value = expected_auth_hdr
        expected_resp = Mock()
        expected_resp.status_code = 404
        mock_get.return_value = expected_resp

        actual_client = self._get_client()
        actual_data = actual_client.fetch_bundle_data(expected_task_id)

        mock_get.assert_called_with(
            f'{actual_client._url}bundle/{expected_task_id}',
            headers=expected_auth_hdr
        )
        self.assertIsNone(actual_data)

    @patch(f'{MODULE_PATH}.Client._get_auth_header')
    @patch('requests.get')
    def test_fetch_bundle_data_login_error(self, mock_get, mock_get_auth_header):
        expected_task_id = '1'
        expected_ex = api.LoginError('cannot login')
        mock_get_auth_header.side_effect = expected_ex

        actual_client = self._get_client()
        with self.assertRaises(api.ApiError) as ex_context:
            actual_client.fetch_bundle_data(expected_task_id)

        mock_get.assert_not_called()
        self.assertEqual(str(ex_context.exception), str(expected_ex))

    @patch(f'{MODULE_PATH}.Client._get_auth_header')
    @patch('requests.get')
    def test_fetch_bundle_data_misc_error(self, mock_get, mock_get_auth_header):
        expected_task_id = '1'
        expected_auth_hdr = {}
        mock_get_auth_header.return_value = expected_auth_hdr
        expected_ex = RuntimeError('err')
        mock_get.side_effect = expected_ex

        actual_client = self._get_client()
        with self.assertRaises(api.DataRetrivalError) as ex_context:
            actual_client.fetch_bundle_data(expected_task_id)

        mock_get.assert_called_with(
            f'{actual_client._url}bundle/{expected_task_id}',
            headers=expected_auth_hdr
        )
        self.assertEqual(str(ex_context.exception), str(expected_ex))

    def test_build_file_url(self):
        expected_task_id = '123'
        expected_file_id = 'abc'
        expected_file_name = 'file'
        
        actual_client = self._get_client()
        expected_url = f"{actual_client._url}bundle/{expected_task_id}/{expected_file_id}/{expected_file_name}"
        actual_url = actual_client.build_file_url(expected_task_id, expected_file_id, expected_file_name)

        self.assertEqual(actual_url, expected_url)
