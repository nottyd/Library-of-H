import sys

import urllib
import colorama

from . import Logging
from nhentaiDownloader.Config import Config

__config__ = Config()


def exception_handling(e):
    if isinstance(e, urllib.error.HTTPError):
        if e.getcode() >= 400 and e.getcode() <= 511:
            if e.getcode() == 403:  # Forbidden
                Logging.log_and_print(
                    error_family="URLError", error_type="forbidden", error=e
                )
                return
            elif (
                e.getcode() == 404 or e.getcode() == 410
            ):  # Page Not Found and Page Gone
                Logging.log_and_print(
                    error_family="URLError", error_type="page_not_found", error=e
                )
                return

    if isinstance(e, OSError):
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
