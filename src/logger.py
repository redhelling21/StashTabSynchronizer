import logging
from logging.handlers import RotatingFileHandler
from confighandler import config as cfg
import sys
import os

LOG_LEVEL = cfg.loadConfig().get("logLevel", logging.DEBUG)
CURRENT_PATH = os.path.dirname(sys.argv[0])

appLogger = logging.getLogger('StashTabSynchronizer')
appLogger.setLevel(LOG_LEVEL)

max_bytes = 10 * 1024 * 1024  # 10 MB - Set the maximum size for each log file
backup_count = 5  # Number of backup files to keep
file_handler = RotatingFileHandler(f"{CURRENT_PATH}/logs/main.log", maxBytes=max_bytes, backupCount=backup_count)
console_handler = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

appLogger.addHandler(file_handler)
appLogger.addHandler(console_handler)

subLogger = logging.getLogger('Callback')
subLogger.setLevel(LOG_LEVEL)

max_bytes = 10 * 1024 * 1024  # 10 MB - Set the maximum size for each log file
backup_count = 5  # Number of backup files to keep
sub_file_handler = RotatingFileHandler(f"{CURRENT_PATH}/logs/callback.log", maxBytes=max_bytes, backupCount=backup_count)
sub_console_handler = logging.StreamHandler()

sub_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

sub_file_handler.setFormatter(sub_formatter)
sub_console_handler.setFormatter(sub_formatter)

subLogger.addHandler(sub_file_handler)
subLogger.addHandler(sub_console_handler)
