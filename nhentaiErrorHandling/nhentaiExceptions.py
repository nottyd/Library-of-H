import nhentaiErrorHandling
import sys

import colorama

from .Logging import *


class nhentaiExceptions(Exception):
    # Temporary network errors
    TIMEOUT_ERROR = 10001

    # Config errors
    DIRECTORY_EXISTS_ERROR = 20001
    DOWNLOAD_NAME_FORMAT_ERROR = 20002

    # Invalid user input errors
    INVALID_GALLERY = 30001
    INVALID_ARTIST = 30002
    INVALID_GROUP = 30003

    # Errors mitigatable with user cognition
    LANGUAGE_NOT_AVAILABLE_ERROR = 40001
    NAME_TOO_LONG_ERROR = 40002


class TimeoutError(nhentaiExceptions):
    def __init__(self, url, log_type="downloader"):
        self.log_msg = f"Connection timeout. URL => {url}"
        self.print_msg = (
            f"{colorama.Fore.RED}Connection timeout. URL => {colorama.Fore.BLUE}{url}"
        )
        self.log_type = log_type
        self.error_code = nhentaiExceptions.TIMEOUT_ERROR


class DirectoryExistsError(nhentaiExceptions):
    def __init__(self, msg, log_type):
        self.log_msg = msg
        self.print_msg = f"{colorama.Fore.RED}{msg}"
        self.log_type = log_type
        self.error_code = nhentaiExceptions.DIRECTORY_EXISTS_ERROR


class DownloadNameFormatError(nhentaiExceptions):
    def __init__(self, msg, error, log_type="downloader"):
        self.log_type = log_type
        self.log_msg = msg
        self.print_msg = f"{colorama.Fore.RED}{msg}"
        self.error_code = nhentaiExceptions.DOWNLOAD_NAME_FORMAT_ERROR
        self.error = error.__str__()


class InvalidError(nhentaiExceptions):
    pass


class InvalidGallery(InvalidError):
    def __init__(self, invalid_gallery, log_type="downloader"):
        self.log_type = log_type
        self.invalid_gallery = invalid_gallery
        self.log_msg = f"Invalid gallery ID: {invalid_gallery}"
        self.print_msg = f"{colorama.Fore.RED}{self.log_msg}"
        self.error_code = nhentaiExceptions.INVALID_GALLERY


class InvalidArtist(InvalidError):
    def __init__(self, invalid_artist, log_type="downloader"):
        self.log_type = log_type
        self.invalid_artist = invalid_artist
        self.log_msg = f"Invalid artist name: {invalid_artist}"
        self.print_msg = f"{colorama.Fore.RED}{self.log_msg}"
        self.error_code = nhentaiExceptions.INVALID_ARTIST


class InvalidGroup(InvalidError):
    def __init__(self, invalid_group, log_type="downloader"):
        self.log_type = log_type
        self.invalid_group = invalid_group
        self.log_msg = f"Invalid group name: {invalid_group}"
        self.print_msg = f"{colorama.Fore.RED}{self.log_msg}"
        self.error_code = nhentaiExceptions.INVALID_GROUP


class TitleError(nhentaiExceptions):
    def __init__(
        self, gallery_title, gallery_code, gallery_folder, log_type="downloader"
    ):
        self.gallery_title = gallery_title
        self.gallery_code = gallery_code
        self.gallery_folder = gallery_folder
        self.log_type = "downloader"


class LanguageNotAvailable(TitleError):
    def __init__(
        self, msg, gallery_title, gallery_code, gallery_folder, log_type="downloader"
    ):
        super().__init__(
            gallery_title, gallery_code, gallery_folder, log_type="downloader"
        )
        self.log_msg = msg
        self.print_msg = f"{colorama.Fore.RED}Error formatting title with %(translated_title)s and/or %(original_title)s: Title not available in those languages."
        self.error_code = nhentaiExceptions.LANGUAGE_NOT_AVAILABLE_ERROR


class NameTooLongError(TitleError):
    def __init__(
        self, gallery_title, gallery_code, gallery_folder, log_type="downloader"
    ):
        super().__init__(
            gallery_title, gallery_code, gallery_folder, log_type="downloader"
        )
        self.print_msg = f"Directory name too long: {self.gallery_folder}"
        self.error_code = nhentaiExceptions.NAME_TOO_LONG_ERROR
