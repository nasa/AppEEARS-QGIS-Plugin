from .plugin import Plugin


def classFactory(iface):  # pylint: disable=invalid-name
    """
    Loads the plugin for QGIS
    """
    return Plugin(iface)
