import logging
import os
import sys

_log_location = os.path.abspath(f"{os.path.dirname(__file__)}{os.sep}..{os.sep}logs")


class StaticVariables:

    """
    A class namespace to store respective variables with their respective values, they will be updated as the program runs.
    Only to be used at the end.
    """

    invalid_galleries = list()
    invalid_artists = list()
    invalid_groups = list()
    name_too_long = dict()
    language_not_available = dict()


formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = None


def _downloader_logging() -> logging.Logger:
    downloader_logger = logging.getLogger("nhentaiDownloader")
    downloader_file_handler = logging.FileHandler(f"{_log_location}/DownloaderLogs.log")
    downloader_file_handler.setFormatter(formatter)
    downloader_logger.addHandler(downloader_file_handler)
    return downloader_logger


def _explorer_logging() -> logging.Logger:
    explorer_logger = logging.getLogger("nhentaiExplorer")
    explorer_file_handler = logging.FileHandler(f"{_log_location}/ExplorerLogs.log")
    explorer_file_handler.setFormatter(formatter)
    explorer_logger.addHandler(explorer_file_handler)
    return explorer_logger


def _dbmanager_logging() -> logging.Logger:
    dbmanager_logger = logging.getLogger("nhentaiDBManager")
    dbmanager_file_handler = logging.FileHandler(f"{_log_location}/DBManagerLogs.log")
    dbmanager_file_handler.setFormatter(formatter)
    dbmanager_logger.addHandler(dbmanager_file_handler)
    return dbmanager_logger


def log_and_print(level, log_type, log_msg=None, print_msg=None) -> None:
    if log_msg:
        log(level, log_msg, log_type)
    if print_msg:
        print_(print_msg)


def log(level, log_msg, log_type=""):
    global logger
    if not os.path.exists(_log_location):
        os.mkdir(_log_location)
    if log_type == "downloader" and "nhentaiDownloader" not in str(logger):
        logger = _downloader_logging()
    if log_type == "explorer" and "nhentaiExplorer" not in str(logger):
        logger = _explorer_logging()
    if log_type == "dbmanager" and "nhentaiDBManager" not in str(logger):
        logger = _dbmanager_logging()

    if level == "info":
        logger.info(log_msg)
    if level == "debug":
        logger.debug(log_msg)
    if level == "warning":
        logger.warning(log_msg)
    if level == "error":
        logger.error(log_msg)
    if level == "critical":
        logger.critical(log_msg)


def print_(print_msg):
    print(print_msg)
    print()
