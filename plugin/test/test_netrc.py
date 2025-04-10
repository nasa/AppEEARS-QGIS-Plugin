import unittest
from unittest.mock import patch, Mock
from qgis.core import Qgis
from netrc import NetrcParseError
from plugin import netrc

MODULE_PATH = 'plugin.netrc'


class ModuleTest(unittest.TestCase):

    @patch('os.path.expanduser')
    def test_get_user_netrc_path(self, mock_expanduser):
        expected_path = '~/.netrc'
        expected_user_path = '/Users/me/'
        mock_expanduser.return_value = expected_user_path

        actual_user_path = netrc._get_user_netrc_path()

        mock_expanduser.assert_called_with(expected_path)
        self.assertEqual(actual_user_path, expected_user_path)

    @patch(f'{MODULE_PATH}.netrc')
    def test_parse_netrc(self, mock_netrc):
        expected_file_path = '/Users/me/.netrc'
        expected_nrc = {}
        mock_netrc.return_value = expected_nrc

        actual_nrc = netrc._parse_netrc(expected_file_path)

        mock_netrc.assert_called_with(expected_file_path)
        self.assertIs(actual_nrc, expected_nrc)

    @patch(f'{MODULE_PATH}.netrc')
    def test_parse_netrc_failure(self, mock_netrc):
        expected_file_path = '/Users/me/.netrc'
        expected_ex = NetrcParseError('no good')
        mock_netrc.side_effect = expected_ex
        expected_ex_msg = f'Failed to parse {expected_file_path}: {expected_ex}'

        with self.assertRaises(NetrcParseError) as ex_context:
            netrc._parse_netrc(expected_file_path)

        mock_netrc.assert_called_with(expected_file_path)
        self.assertIn(expected_ex_msg, str(ex_context.exception))

    @patch(f'builtins.open')
    @patch('os.chmod')
    @patch('os.path.exists')
    @patch(f'{MODULE_PATH}._parse_netrc')
    @patch(f'{MODULE_PATH}._get_user_netrc_path')
    def test_store_creds_not_existing(self, mock_get_user_netrc_path, mock_parse_netrc, mock_path_exists, mock_chmod, mock_open):
        expected_machine, expected_user, expected_pw = 'm', 'u', 'p'
        expected_file_path = '/Users/me/.netrc'
        mock_get_user_netrc_path.return_value = expected_file_path
        mock_path_exists.return_value = False
        expected_open_1 = Mock()
        expected_open_1_fh = Mock()
        expected_open_1_fh.close = Mock()
        expected_open_1.return_value = expected_open_1_fh
        expected_open_2 = Mock()
        expected_open_2_fh = Mock()
        expected_open_2_fh.write = Mock()
        expected_open_2.__enter__ = Mock(return_value=expected_open_2_fh)
        expected_open_2.__exit__ = Mock()
        mock_open.side_effect = [expected_open_1, expected_open_2]
        expected_nrc = Mock()
        expected_hosts = {
            'another_machine': ('u', 'a', 'p')
        }
        expected_nrc.hosts = expected_hosts
        mock_parse_netrc.return_value = expected_nrc
        expected_write_args_list_1 = [
            f'machine another_machine\n  login {expected_hosts["another_machine"][0]}\n',
            f'  account {expected_hosts["another_machine"][1]}\n',
            f'  password {expected_hosts["another_machine"][2]}\n'
        ]
        expected_write_args_list_2 = [
            f'machine {expected_machine}\n  login {expected_user}\n',
            f'  password {expected_pw}\n'
        ]

        netrc.store_creds(expected_machine, expected_user, expected_pw)

        mock_get_user_netrc_path.assert_called_with()
        mock_path_exists.assert_called_with(expected_file_path)
        mock_open.call_args_list[0].assert_called_with(expected_file_path, 'w')
        mock_chmod.assert_called_with(expected_file_path, 0o600)
        mock_parse_netrc.assert_called_with(expected_file_path)
        mock_open.call_args_list[1].assert_called_with(expected_file_path, 'w')
        for i, c in enumerate(expected_open_2_fh.write.call_args_list[0:3]):
            c.assert_called_with(expected_write_args_list_1[i])
        for i, c in enumerate(expected_open_2_fh.write.call_args_list[3:]):
            c.assert_called_with(expected_write_args_list_2[i])

    @patch('os.path.exists')
    @patch(f'{MODULE_PATH}._parse_netrc')
    @patch(f'{MODULE_PATH}._get_user_netrc_path')
    def test_store_creds_existing_no_force(self, mock_get_user_netrc_path, mock_parse_netrc, mock_path_exists):
        expected_machine, expected_user, expected_pw = 'm', 'u', 'p'
        expected_file_path = '/Users/me/.netrc'
        mock_get_user_netrc_path.return_value = expected_file_path
        mock_path_exists.return_value = True
        expected_nrc = Mock()
        expected_hosts = {}
        expected_nrc.hosts = {
            expected_machine: expected_pw
        }
        mock_parse_netrc.return_value = expected_nrc
        expected_ex_msg = f"Credentials already exist for machine '{expected_machine}' in user netrc file."

        with self.assertRaises(netrc.ConflictError) as ex_context:
            netrc.store_creds(expected_machine, expected_user, expected_pw)
        self.assertEqual(str(ex_context.exception), expected_ex_msg)

    @patch('os.path.exists')
    @patch(f'{MODULE_PATH}._parse_netrc')
    @patch(f'{MODULE_PATH}._get_user_netrc_path')
    def test_retrieve_creds(self, mock_get_user_netrc_path, mock_parse_netrc, mock_path_exists):
        expected_machine = 'm'
        expected_user, expected_pw = 'u', 'p'
        expected_file_path = '/Users/me/.netrc'
        mock_get_user_netrc_path.return_value = expected_file_path
        mock_path_exists.return_value = True
        expected_nrc = Mock()
        expected_hosts = {}
        expected_nrc.hosts = {
            expected_machine: (expected_user, None, expected_pw)
        }
        mock_parse_netrc.return_value = expected_nrc
        expected_creds = (expected_user, expected_pw)

        actual_creds = netrc.retrieve_creds(expected_machine)

        mock_get_user_netrc_path.assert_called_with()
        mock_path_exists.assert_called_with(expected_file_path)
        mock_parse_netrc.assert_called_with(expected_file_path)
        self.assertEqual(actual_creds, expected_creds)

    @patch('os.path.exists')
    @patch(f'{MODULE_PATH}._parse_netrc')
    @patch(f'{MODULE_PATH}._get_user_netrc_path')
    def test_retrieve_creds_no_file(self, mock_get_user_netrc_path, mock_parse_netrc, mock_path_exists):
        expected_machine = 'm'
        expected_user, expected_pw = 'u', 'p'
        expected_file_path = '/Users/me/.netrc'
        mock_get_user_netrc_path.return_value = expected_file_path
        mock_path_exists.return_value = False
        expected_creds = (None, None)

        actual_creds = netrc.retrieve_creds(expected_machine)

        mock_get_user_netrc_path.assert_called_with()
        mock_path_exists.assert_called_with(expected_file_path)
        mock_parse_netrc.assert_not_called()
        self.assertEqual(actual_creds, expected_creds)

    @patch('os.path.exists')
    @patch(f'{MODULE_PATH}._parse_netrc')
    @patch(f'{MODULE_PATH}._get_user_netrc_path')
    def test_retrieve_creds_none_present(self, mock_get_user_netrc_path, mock_parse_netrc, mock_path_exists):
        expected_machine = 'm'
        expected_user, expected_pw = 'u', 'p'
        expected_file_path = '/Users/me/.netrc'
        mock_get_user_netrc_path.return_value = expected_file_path
        mock_path_exists.return_value = True
        expected_nrc = Mock()
        expected_hosts = {}
        expected_nrc.hosts = {
            expected_machine: None
        }
        mock_parse_netrc.return_value = expected_nrc
        expected_creds = (None, None)

        actual_creds = netrc.retrieve_creds(expected_machine)

        mock_get_user_netrc_path.assert_called_with()
        mock_path_exists.assert_called_with(expected_file_path)
        mock_parse_netrc.assert_called_with(expected_file_path)
        self.assertEqual(actual_creds, expected_creds)