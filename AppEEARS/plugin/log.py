from qgis.core import QgsMessageLog, Qgis


class Log:
    """
    Used for QGIS message logging
    """
    def __init__(self, tag='AppEEARS Plugin'):
        self._tag = tag
    
    def _log(self, msg, level):
        QgsMessageLog.logMessage(msg, tag=self._tag, level=level)

    def info(self, msg):
        self._log(msg, Qgis.Info)

    def warn(self, msg):
        self._log(msg, Qgis.Warning)


# a logger for system-wide use
LOGGER = Log()
