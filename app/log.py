import logging


class AppLogger:
    _logger = None

    def __init__(self):
        logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
        self._logger = logging.getLogger(__name__)

    def get_logger(self):
        return self._logger
