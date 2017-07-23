import logging
import logging.handlers
from time import gmtime, strftime
from config_class import Config
config = Config()

log_path = config.system['log_path']


class FileLogger:
    """
    Logger class for logging to file with rotation
    """
    LOG_FILENAME = log_path
    logger = logging.getLogger(__name__)

    def __init__(self, log_to_console=False):
        self.log_to_console = log_to_console
        self.log_format = '%(asctime)s [%(threadName)-12.12s] %(levelname)s - %(message)s'
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # create a file handler
        handler = logging.handlers.RotatingFileHandler(self.LOG_FILENAME,
                                                       maxBytes=1000000, backupCount=10)
        handler.setLevel(logging.INFO)
        # create a logging format
        formatter = logging.Formatter(self.log_format)
        handler.setFormatter(formatter)

        # add the handlers to the logger
        self.logger.addHandler(handler)

    def log(self, level, message):
        """
        Log message
        @param level: log level - 'info', 'warning', 'error', 'critical'
        @param message: message string
        """
        self.logger.__getattribute__(level)(message)


class ConsoleLogger:
    """
    Logger class for logging to console
    """
    def __init__(self):
        self.log_format = '{timestamp} {level} - {message}'

    def log(self, level, message):
        """
        Log message
        @param level: log level - 'info', 'warning', 'error', 'critical'
        @param message: message string
        """
        timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        print self.log_format.format(timestamp=timestamp, level=level.upper(), message=message)
