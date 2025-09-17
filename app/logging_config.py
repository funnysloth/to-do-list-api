# Imports from external libraries
from pythonjsonlogger.json import JsonFormatter

# Imports from standard library
import logging
import sys


def setup_logging():
    """
    Configures structured JSON logging for the application.
    Logs are directed to standard output.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logHandler = logging.StreamHandler(sys.stdout)
    
    formatter = JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)