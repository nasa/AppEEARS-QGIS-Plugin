import unittest
from unittest.mock import patch, Mock, PropertyMock
import plugin

MODULE_PATH = 'plugin'


class PluginTest(unittest.TestCase):

    @patch(f'{MODULE_PATH}.Plugin.tr')
    @patch(f'{MODULE_PATH}.QCoreApplication.installTranslator')
    @patch(f'{MODULE_PATH}.QTranslator')
    @patch('os.path.exists')
    @patch(f'{MODULE_PATH}.util.get_path_from_root')
    @patch(f'{MODULE_PATH}.QSettings')
    def test_init(
        self, mock_QSettings, mock_get_path_from_root, mock_path_exists,
        mock_QTranslator, mock_installTranslator, mock_tr, return_instance=False
    ):
        expected_iface = Mock()
        expected_qsettings = Mock()
        expected_locale_key = 'locale/userLocale'
        expected_locale_val = 'en'
        expected_qsettings.value = Mock(return_value=expected_locale_val)
        mock_QSettings.return_value = expected_qsettings
        expected_local_path_parts = [
            'i18n', f'AppEEARS_{expected_locale_val}.qm'
        ]
        expected_locale_path = '/path/to/locale'
        mock_get_path_from_root.return_value = expected_locale_path
        mock_path_exists.return_value = True
        expected_translator = Mock()
        expected_translator.load = Mock()
        mock_QTranslator.return_value = expected_translator
        expected_tr_name = u'&AppEEARS_QGIS'
        expected_menu = {}
        mock_tr.return_value = expected_menu

        actual_plugin = plugin.Plugin(expected_iface)
        if return_instance:
            return actual_plugin

        expected_qsettings.value.assert_called_with(expected_locale_key)
        mock_get_path_from_root.assert_called_with(
            *expected_local_path_parts
        )
        mock_path_exists.assert_called_with(expected_locale_path)
        mock_QTranslator.assert_called_with()
        expected_translator.load.assert_called_with(expected_locale_path)
        mock_installTranslator.assert_called_with(expected_translator)
        self.assertEqual(actual_plugin.actions, [])
        self.assertEqual(actual_plugin.first_start, None)
        mock_tr.assert_called_with(expected_tr_name)
        self.assertEqual(actual_plugin.menu, expected_menu)

    @patch(f'{MODULE_PATH}.QCoreApplication.translate')
    def test_tr(self, mock_translate):
        expected_msg = 'message'
        expected_translation = 'msg'
        mock_translate.return_value = expected_translation

        actual_plugin = self.test_init(return_instance=True)
        actual_translation = actual_plugin.tr(expected_msg)

        mock_translate.assert_called_with('AppEEARS', expected_msg)
        self.assertEqual(actual_translation, expected_translation)

    @patch(f'{MODULE_PATH}.QAction')
    @patch(f'{MODULE_PATH}.QIcon')
    def test_add_action(self, mock_QIcon, mock_QAction):
        expected_text = 'text'
        expected_callback = lambda x: x
        expected_status_tip = 'tip'
        expected_whats_this = 'what?!'
        expected_icon_path = '/path/to/icon.png'
        expected_icon = Mock()
        mock_QIcon.return_value = expected_icon
        expected_action = Mock()
        expected_action.triggered.connect = Mock()
        expected_action.setEnabled = Mock()
        expected_action.setStatusTip = Mock()
        expected_action.setWhatsThis = Mock()
        mock_QAction.return_value = expected_action
        actual_plugin = self.test_init(return_instance=True)
        actual_plugin.iface.addToolBarIcon = Mock()
        actual_plugin.iface.addPluginToMenu = Mock()

        actual_action = actual_plugin.add_action(expected_icon_path, expected_text, expected_callback, status_tip=expected_status_tip, whats_this=expected_whats_this, add_to_toolbar=True, add_to_menu=True)

        mock_QIcon.assert_called_with(expected_icon_path)
        mock_QAction.assert_called_with(expected_icon, expected_text, None)
        expected_action.triggered.connect.assert_called_with(expected_callback)
        expected_action.setEnabled.assert_called_with(True)
        expected_action.setStatusTip.assert_called_with(expected_status_tip)
        expected_action.setWhatsThis.assert_called_with(expected_whats_this)
        actual_plugin.iface.addToolBarIcon.assert_called_with(expected_action)
        actual_plugin.iface.addPluginToMenu.assert_called_with(
            actual_plugin.menu, expected_action
        )
        self.assertIn(expected_action, actual_plugin.actions)
        self.assertIs(actual_action, expected_action)

    @patch(f'{MODULE_PATH}.Plugin.tr')
    @patch(f'{MODULE_PATH}.Plugin.add_action')
    @patch(f'{MODULE_PATH}.util.get_path_from_root')
    def test_initGui(self, mock_get_path_from_root, mock_add_action, mock_tr):
        expected_icon_path = '/path/to/icon.png'
        mock_get_path_from_root.return_value = expected_icon_path
        expected_path_parts = ['assets', 'icon.png']
        expected_tr_val = u'AppEEARS'
        expected_text = 't'
        mock_tr.return_value = expected_text
        actual_plugin = self.test_init(return_instance=True)
        expected_parent = 'p'
        actual_plugin.iface.mainWindow = Mock(return_value=expected_parent)

        actual_plugin.initGui()

        mock_get_path_from_root.assert_called_with(*expected_path_parts)
        mock_tr.assert_called_with(expected_tr_val)
        actual_plugin.iface.mainWindow.assert_called_with()
        mock_add_action.assert_called_with(
            expected_icon_path, text=expected_text,
            callback=actual_plugin.run, parent=expected_parent
        )
        self.assertTrue(actual_plugin.first_start)

    @patch(f'{MODULE_PATH}.Plugin.tr')
    def test_unload(self, mock_tr):
        expected_tr_res = 't'
        mock_tr.return_value = expected_tr_res
        expected_actions = [0, 1]
        actual_plugin = self.test_init(return_instance=True)
        actual_plugin.iface.removePluginMenu = Mock()
        actual_plugin.iface.removeToolBarIcon = Mock()

        actual_plugin.actions = expected_actions
        actual_plugin.unload()

        for i, act in enumerate(expected_actions):
            actual_plugin.iface.removePluginMenu.call_args_list[i].assert_called_with(
                expected_tr_res, act
            )
            actual_plugin.iface.removeToolBarIcon.call_args_list[i].assert_called_with(act)

    @patch(f'{MODULE_PATH}.Dialog')
    def test_run(self, mock_Dialog):
        expected_dlg = Mock()
        expected_dlg.show = Mock()
        expected_exec = 'result'
        expected_dlg.exec_ = Mock(return_value=expected_exec)
        mock_Dialog.return_value = expected_dlg

        actual_plugin = self.test_init(return_instance=True)
        actual_plugin.first_start = True
        actual_plugin.run()

        mock_Dialog.assert_called_with()
        expected_dlg.show.assert_called_with()
        expected_dlg.exec_.assert_called_with()

