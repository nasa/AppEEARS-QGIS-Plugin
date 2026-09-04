import unittest
from unittest.mock import patch
from qgis.core import Qgis
from plugin import log

MODULE_PATH = 'plugin.log'


class ModuleTest(unittest.TestCase):

    def test_system_logger(self):
        self.assertIsInstance(log.LOGGER, log.Log)


class LogTest(unittest.TestCase):

    def _get_test_log(self):
        return log.Log(tag='test')

    def test_init(self):
        expected_tag = 'test'

        actual_log = log.Log(tag=expected_tag)
        
        self.assertEqual(actual_log._tag, expected_tag)

    @patch('qgis.core.QgsMessageLog.logMessage')
    def test_log(self, mock_logMessage):
        expected_msg, expected_lvl = 'info', Qgis.Info

        actual_log = self._get_test_log()
        expected_tag = actual_log._tag
        actual_log._log(expected_msg, expected_lvl)

        mock_logMessage.assert_called_with(
            expected_msg, tag=expected_tag, level=expected_lvl
        )

    @patch(f'{MODULE_PATH}.Log._log')
    def test_info(self, mock_log):
        expected_msg, expected_lvl = 'info', Qgis.Info

        actual_log = self._get_test_log()
        actual_log.info(expected_msg)

        mock_log.assert_called_with(
            expected_msg, expected_lvl
        )

    @patch(f'{MODULE_PATH}.Log._log')
    def test_warn(self, mock_log):
        expected_msg, expected_lvl = 'info', Qgis.Warning

        actual_log = self._get_test_log()
        actual_log.warn(expected_msg)

        mock_log.assert_called_with(
            expected_msg, expected_lvl
        )
