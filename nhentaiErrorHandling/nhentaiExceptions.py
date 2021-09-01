import sys

import colorama

from .Logging import *

class nhentaiExceptions(Exception):
    pass

class TimeoutError(nhentaiExceptions):
    def __init__(self, url):
        log_msg = f"Connection timeout. URL => {url}"
        print_msg = f"{colorama.Fore.RED}Connection timeout. URL => {colorama.Fore.BLUE}{url}"
        log_and_print(level='critical', log_type='downloader', log_msg=log_msg, print_msg=print_msg)


class TitleError(nhentaiExceptions):
    pass

class LanguageNotAvailable(TitleError):
    def __init__(self, gallery_title, gallery_code, gallery_folder):
        print_msg = f'{colorama.Fore.RED}Error formatting title with %(translated_title)s and/or %(original_title)s: Title not available in those languages.'

        print_(print_msg=print_msg)

class NameTooLongError(TitleError):
    def __init__(self, gallery_title, gallery_code, gallery_folder):
        print_msg = f'Directory name too long: {gallery_folder}'
        print_(print_msg=print_msg)
        if gallery_title in StaticVariables.name_too_long.keys():
            StaticVariables.name_too_long[gallery_title].append((gallery_folder, gallery_code))
        StaticVariables.name_too_long

class DirectoryExistsError(nhentaiExceptions):
    def __init__(self, msg, log_type):
        log_msg = msg
        print_msg = f"{colorama.Fore.RED}{msg}"
        log_and_print(level='critical', log_type=log_type, log_msg=log_msg, print_msg=print_msg)
        sys.exit()

class DownloadNameFormatError(nhentaiExceptions):
    def __init__(self, error):
        print_(print_msg=f'{colorama.Fore.RED}Error loading downloadnameformat from Config.ini: {error}')
        sys.exit()


class InvalidError(nhentaiExceptions):
    pass

class InvalidCode(InvalidError):
    def __init__(self, gallery_code):
        log_msg = f'Invalid gallery ID: {gallery_code}'
        print_msg = f'{colorama.Fore.RED}{log_msg}'
        log_and_print(level='warning', log_type='downloader', log_msg=log_msg, print_msg=print_msg)
        StaticVariables.invalid_codes.append(gallery_code)
    
class InvalidArtist(InvalidError):
    def __init__(self, artist_name):
        log_msg = f'Invalid artist name: {artist_name}'
        print_msg = f'{colorama.Fore.RED}{log_msg}'
        log_and_print(level='warning', log_type='downloader', log_msg=log_msg, print_msg=print_msg)
        StaticVariables.invalid_codes.append(artist_name)

class InvalidGroup(InvalidError):
    def __init__(self, group_name):
        log_msg = f'Invalid group name: {group_name}'
        print_msg = f'{colorama.Fore.RED}{log_msg}'
        log_and_print(level='warning', log_type='downloader', log_msg=log_msg, print_msg=print_msg)
        StaticVariables.invalid_codes.append(group_name)