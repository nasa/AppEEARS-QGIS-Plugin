import unittest
from unittest.mock import patch, Mock
from plugin import util

MODULE_PATH = 'plugin.util'


class ModuleTest(unittest.TestCase):

    def _get_test_log(self):
        return log.Log(tag='test')

    @patch('osgeo.gdal.SetConfigOption')
    def test_set_gdal_options(self, mock_SetConfigOption):
        expected_token = '123'
        expected_opts = {
            'SPECIAL_OPT': 'val'
        }
        expected_set_opts = {
            "GDAL_HTTP_AUTH": "BEARER", "GDAL_HTTP_BEARER": expected_token,
            "GDAL_HTTP_MAX_RETRY": "10", "GDAL_HTTP_RETRY_DELAY": "0.5"
        }
        expected_set_opts.update(expected_opts)

        util.set_gdal_options(expected_token, opts=expected_opts)

        for i, itm in enumerate(expected_set_opts.items()):
            mock_SetConfigOption.call_args_list[i].assert_called_with(
                itm[0], itm[1]
            )

    @patch('pathlib.Path')
    def test_get_project_root_path(self, mock_Path):
        expected_root_path = '/path/to/project'
        expected_path = Mock()
        expected_path.parent = Mock()
        expected_path.parent.parent = Mock()
        expected_path.parent.parent.absolute = Mock(return_value=expected_root_path)
        mock_Path.return_value = expected_path

        self.assertEqual(
            util.get_project_root_path(), expected_root_path
        )

    @patch('os.path.join')
    @patch(f'{MODULE_PATH}.get_project_root_path')
    def test_get_path_from_root(self, mock_get_project_root_path, mock_join):
        expected_root_path = '/path/to/project'
        mock_get_project_root_path.return_value = expected_root_path
        expected_parts = [
            'tumbling', 'down', 'the', 'rabbit', 'hole'
        ]
        expected_path = '/root/path'
        mock_join.return_value = expected_path

        actual_path = util.get_path_from_root(*expected_parts)

        mock_get_project_root_path.assert_called_with()
        mock_join.assert_called_with(expected_root_path, *expected_parts)
        self.assertEqual(actual_path, expected_path)
