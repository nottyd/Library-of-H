import sys

import requests
import colorama

from nhentaiErrorHandling import Logging
from nhentaiErrorHandling.Logging import StaticVariables
from nhentaiErrorHandling import nhentaiExceptions


def exception_handling(e):
    if isinstance(e, requests.exceptions.HTTPError):
        if e.response.status_code == 403:  # Forbidden
            Logging.log_and_print(
                level="warning",
                log_type="downloader",
                log_msg=f"Access forbidden. URL => {e.response.url}",
                print_msg=f"{colorama.Fore.RED}Access forbidden. URL => {colorama.Fore.BLUE}{e.response.url}",
            )
        elif (
            e.response.status_code == 404 or e.response.status_code == 410
        ):  # Page Not Found and Page Gone
            Logging.log_and_print(
                level="warning",
                log_type="downloader",
                log_msg=f"Page not found. URL => {e.response.url}",
                print_msg=f"{colorama.Fore.RED}Page not found. URL => {e.response.url}",
            )
    elif isinstance(e, OSError):
        print(e.args[0].errno)
        if e.args[0].errno == 10053:
            """
            [WinError 10053] An established connection was aborted by the software in your host machine
            Lost connection to internet.
            """
            Logging.log_and_print(
                level="critical",
                log_msg=e,
                print_msg=f"{colorama.Fore.RED}{str(e)}",
                log_type="downloader",
            )
            sys.exit()

        elif e.args[0].errno == 2:
            Logging.log_and_print(
                level="critical",
                log_msg=e,
                print_msg=f"{colorama.Fore.RED}{str(e)}",
                log_type="downloader",
            )
            sys.exit()

        elif e.args[0].errno == 8:
            """
            <urlopen error EOF occurred in violation of protocol (_ssl.c:1123)>
            Don't know what it means, got it when I tried to access nhentai without VPN i.e. banned by ISP.
            """
            Logging.log_and_print(
                level="critical",
                log_msg=e,
                print_msg=f"{colorama.Fore.RED}{str(e)}",
                log_type="downloader",
            )
            sys.exit()

    elif isinstance(e, nhentaiExceptions.nhentaiExceptions):
        if e.error_code == nhentaiExceptions.nhentaiExceptions.TIMEOUT_ERROR:
            Logging.log_and_print(
                level="critical",
                log_type="downloader",
                log_msg=e.log_msg,
                print_msg=e.print_msg,
            )

        elif e.error_code == nhentaiExceptions.nhentaiExceptions.DIRECTORY_EXISTS_ERROR:
            Logging.log_and_print(
                level="critical",
                log_type=e.log_type,
                log_msg=e.log_msg,
                print_msg=e.print_msg,
            )
            sys.exit()

        elif (
            e.error_code
            == nhentaiExceptions.nhentaiExceptions.DOWNLOAD_NAME_FORMAT_ERROR
        ):
            Logging.log_and_print(
                level="critical",
                log_type=e.log_type,
                log_msg=e.log_msg,
                print_msg=e.print_msg,
            )
            sys.exit()

        elif e.error_code == nhentaiExceptions.nhentaiExceptions.INVALID_CODE:
            Logging.log_and_print(
                level="warning",
                log_type="downloader",
                log_msg=e.log_msg,
                print_msg=e.print_msg,
            )
            StaticVariables.invalid_codes.append(e.gallery_code)

        elif e.error_code == nhentaiExceptions.nhentaiExceptions.INVALID_ARTIST:
            Logging.log_and_print(
                level="warning",
                log_type="downloader",
                log_msg=e.log_msg,
                print_msg=e.print_msg,
            )
            StaticVariables.invalid_codes.append(e.invalid_artist)

        elif e.error_code == nhentaiExceptions.nhentaiExceptions.INVALID_GROUP:
            Logging.log_and_print(
                level="warning",
                log_type="downloader",
                log_msg=e.log_msg,
                print_msg=e.print_msg,
            )
            StaticVariables.invalid_artists.append(e.invalid_group)

        elif (
            e.error_code
            == nhentaiExceptions.nhentaiExceptions.LANGUAGE_NOT_AVAILABLE_ERROR
        ):
            Logging.print_(print_msg=e.print_msg)
            if e.gallery_title in StaticVariables.language_not_available.keys():
                StaticVariables.language_not_available[e.gallery_title].append(
                    (e.gallery_folder, e.gallery_code)
                )
            else:
                StaticVariables.language_not_available[e.gallery_title] = [
                    (e.gallery_folder, e.gallery_code)
                ]

        elif e.error_code == nhentaiExceptions.nhentaiExceptions.NAME_TOO_LONG_ERROR:
            if e.gallery_title in StaticVariables.name_too_long.keys():
                StaticVariables.name_too_long[e.gallery_title].append(
                    (e.gallery_folder, e.gallery_code)
                )
