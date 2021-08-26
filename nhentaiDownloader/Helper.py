import sys
import os
import platform
import subprocess
import re
import time
import logging
from typing import Union

import mechanize
from bs4 import BeautifulSoup
import colorama
colorama.init(autoreset=True)

from nhentaiDownloader.Config import Config
from nhentaiErrorHandling import Logging, nhentaiExceptions

program_title = "nhentaiDownloader"
title = {'program_title': program_title, 'title_type':  None, 'input_list_progress': None, 'artist_name': None, 'group_name': None, 'gallery_progress': None, 'gallery_id': None, 'download_progress': None}

config = Config()

# Funcction to create Browser object
def browser_factory() -> mechanize.Browser:
    br = mechanize.Browser()
    br.set_handle_robots(False)
    request = get_request('https://www.nhentai.net')
    return br

# Function to create beautifulsoup object
def soup_maker(url) -> Union[BeautifulSoup, str]:
    request = get_request(url)
    response = get_response_with_retry(request)
    response = response.read()
    soup = BeautifulSoup(response, 'lxml')
    return soup

# Function to get response with mechanize and retry config.retry times
def get_response_with_retry(request) -> mechanize._response.response_seek_wrapper:
    errno = 0
    br = browser_factory()
    for i in range(config.retry+1):
        try:
           response = br.open(request)
        except mechanize.HTTPError as e:
            if e.getcode() in [408, 429, 500, 502, 503, 504]:
                # 408: Request Timeout; 429: Too Many Requests; 500: Internal Server Error; 502: Bad Gateway; 504: Gateway Timeout;
                print_msg = f'\n{colorama.Fore.RED}<{str(e)}> Temporary Error\
                    \n{colorama.Fore.RED}URL => {colorama.Fore.BLUE}{e.url}'
                Logging.print_(print_msg=print_msg)
                print(f'{colorama.Fore.WHITE}{i+1} try out of {config.retry}.')
                if i+1 == config.retry+1:
                    print(f'{colorama.Fore.RED}Out of retries.')
                    raise nhentaiExceptions.TimeoutError(e.url)
                time.sleep(config.retrywait)
            else:
                raise

        except OSError as e:
            if e.args[0].errno == 10053 or errno == 10053:
                print(f'{colorama.Fore.RED}{str(e)}')
                while True:
                    print(f'{colorama.Fore.WHITE}Would you like to retry?(y/n) ', end='')
                    retry = input()
                    if retry.lower() == 'y':
                        print(f'{i+1} try out of {config.retry}.')
                        break
                    if retry.lower() == 'n':
                        Logging.log_and_print(level='critical', log_msg=e, print_msg=f'{colorama.Fore.RED}{str(e)}', log_type='downloader')
                        raise
                    print()
                errno = 10053

            elif e.args[0].errno == 2:
                print(f'{colorama.Fore.RED}{str(e)}')
                while True:
                    print(f'{colorama.Fore.WHITE}Would you like to retry?(y/n) ', end='')
                    retry = input()
                    if retry.lower() == 'y':
                        print(f'{i+1} try out of {config.retry}.')
                        break
                    if retry.lower() == 'n':
                        Logging.log_and_print(level='critical', log_msg=e, print_msg=f'{colorama.Fore.RED}{str(e)}', log_type='downloader')
                        raise
                    print()

            if i+1 == config.retry+1:
                raise
        else:
            return response

# Function to get request
def get_request(url) -> mechanize._request.Request:
    return mechanize.Request(url, None, {'User-Agent':config.useragent})

# Functions for printing progress
# Function for printing bar progress: [########-------]
def print_bar_progress(bar_length=20, total=20, progress=1, msg=None) -> None:
    if total == 0: total = 1
    done = (progress*100)/total
    done = int((done/100)*bar_length)
    print('\r{}{} {} of {}: [{}{}]'.format(colorama.Fore.WHITE, msg, progress, total, '#'*done, '-'*(bar_length-done)), end='')
    if done == bar_length:
        print()

# Function for converting list of thumbnail links to list of actual image links.
def link_converter(image_links) -> list:
    t_image_links = [re.sub('https://t.nhentai.net/galleries/', 'https://i.nhentai.net/galleries/', image_link) for image_link in image_links]
    image_links = t_image_links
    t_image_links = [re.sub('t', '', image_link[::-1], count=1) for image_link in image_links]
    image_links = [t_image_link[::-1] for t_image_link in t_image_links]

    return list(image_links)

# Function for creating a list of thumbnail links.
def links_and_title_getter(gallery_code, filter_call=False) -> Union[tuple, str]:
    gallery_url = 'https://www.nhentai.net/g/{}'.format(gallery_code)
    soup = soup_maker(gallery_url)

    try:
        gallery_before = soup.find('span', class_='before').text
    except AttributeError:
        gallery_before = ''
        log_msg = "Gallery name does not contain class: 'before'"
        print_msg = log_msg
        Logging.log_and_print(level="warning", log_msg=log_msg, print_msg=print_msg, log_type="downloader")

    try:
        gallery_pretty = soup.find('span', class_='pretty').text
    except AttributeError:
        gallery_pretty = ''
        log_msg = "Gallery name does not contain class: 'pretty'"
        print_msg = log_msg
        Logging.log_and_print(level="warning", log_msg=log_msg, print_msg=print_msg, log_type="downloader")
    else:
        temp = gallery_pretty.split('|') # translated and original titles are usually seperated by a '|'
        if len(temp) == 2 and not filter_call:
            translated_title = temp[1]
            original_title = temp[0]
            gallery_pretty = (original_title, translated_title)

    try:
        gallery_after = soup.find('span', class_='after').text
    except AttributeError:
        gallery_after = ''
        log_msg = "Gallery name does not contain class: 'after'"
        print_msg = log_msg
        Logging.log_and_print(level="warning", log_msg=log_msg, print_msg=print_msg, log_type="downloader")

    gallery_title = (gallery_before, gallery_pretty, gallery_after)
    if soup is not None:
        page_links = [str(link.get('src')) for link in soup.find_all('img')]
        image_links = [t_image_link for page_link in page_links for t_image_link in re.findall('https://t.nhentai.net/galleries/.+/.+t\..+', page_link)]
        return (link_converter(image_links), gallery_title)
    else:
        raise nhentaiExceptions.InvalidCode(gallery_code)


def get_links_and_title(gallery_code=None, artist_name=None, group_name=None) -> tuple:
    if gallery_code is not None:
        links_and_title_getter_res = links_and_title_getter(gallery_code)
        image_links = links_and_title_getter_res[0]
        gallery_before = validate_title(links_and_title_getter_res[1][0])
        translated_title = None
        original_title = None
        if isinstance(links_and_title_getter_res[1][1], tuple):
            gallery_title = validate_title(' | '.join(links_and_title_getter_res[1][1]))
            translated_title = validate_title(links_and_title_getter_res[1][1][1])
            original_title = validate_title(links_and_title_getter_res[1][1][0])
        else:
            gallery_title = validate_title(links_and_title_getter_res[1][1])
        if len(gallery_title) > 250:
            raise nhentaiExceptions.InvalidTitleError(gallery_title=gallery_title, gallery_code=gallery_code)
        gallery_after = validate_title(links_and_title_getter_res[1][2])

        if artist_name:
            gallery_folder = artist_gallery_title(gallery_title, gallery_code, translated_title, original_title)
        elif group_name:
            gallery_folder = artist_gallery_title(gallery_title, gallery_code, translated_title, original_title)
        else:
            gallery_folder = artist_gallery_title(gallery_title, gallery_code, translated_title, original_title)

        if len(gallery_folder.split(os.sep)[-1]) > 250:
            Logging.log_and_print()
            Logging.log_and_print(error_family='OSError', error_type='name_too_long', gallery_title=gallery_title, retry=False)
            return gallery_code, 'name too long', image_links, gallery_folder

        return image_links, gallery_folder

def artist_gallery_title(gallery_title, gallery_code, translated_title, original_title) -> str:
    try:
        gallery_folder = config.artistdownloadnameformat % locals()
    except KeyError as e:
        if (not translated_title and '%(translated_title)s' in config.artistdownloadnameformat) or (not original_title and '%(original_title)s' in config.artistdownloadnameformat):
            Logging.print_(print_msg=f'{colorama.Fore.RED}Error formatting title with %(translated_title)s and/or %(original_title)s: Title not available in those languages.')
            raise nhentaiExceptions.InvalidTitleError(gallery_title=gallery_title, gallery_code=gallery_code)
        else:
            Logging.print_(print_msg=f'{colorama.Fore.RED}Error loading artistdownloadnameformat from Config.ini: {e}')
            sys.exit()
    except Exception as e:
        Logging.log_and_print(error_family='CONFError', error_Type='downloadname_load_error', error=e, download_type='artist', cont_default=True)
        sys.exit()
    return gallery_folder

def group_gallery_title(gallery_title, gallery_code, translated_title, original_title) -> str:
    try:
        gallery_folder = config.groupdownloadnameformat % locals()
    except KeyError as e:
        if (not translated_title and '%(translated_title)s' in config.groupdownloadnameformat) or (not original_title and '%(original_title)s' in config.groupdownloadnameformat):
            Logging.print_(print_msg=f'{colorama.Fore.RED}Error formatting title with %(translated_title)s and/or %(original_title)s: Title not available in those languages.')
            raise nhentaiExceptions.InvalidTitleError(gallery_title=gallery_title, gallery_code=gallery_code)
        else:
            Logging.print_(print_msg=f'{colorama.Fore.RED}Error loading groupdownloadnameformat from Config.ini: {e}')
            sys.exit()
    except Exception as e:
        Logging.log_and_print(error_family='CONFError', error_Type='downloadname_load_error', error=e, download_type='group', cont_default=True)
        sys.exit()
    return gallery_folder

def gallery_title(gallery_title, gallery_code, translated_title, original_title) -> str:
    try:
        gallery_folder = config.gallerydownloadnameformat % locals()
    except KeyError as e:
        if (not translated_title and '%(translated_title)s' in config.gallerydownloadnameformat) or (not original_title and '%(original_title)s' in config.gallerydownloadnameformat):
            Logging.print_(print_msg=f'{colorama.Fore.RED}Error formatting title with %(translated_title)s and/or %(original_title)s: Title not available in those languages.')
            raise nhentaiExceptions.InvalidTitleError(gallery_title=gallery_title, gallery_code=gallery_code)
        else:
            Logging.print_(print_msg=f'{colorama.Fore.RED}Error loading gallerydownloadnameformat from Config.ini: {e}')
            sys.exit()
    except Exception as e:
        Logging.log_and_print(error_family='CONFError', error_Type='downloadname_load_error', error=e, download_type='gallery', cont_default=True)
        sys.exit()
    return gallery_folder


# Function to validate title i.e: remove/replace special characters
def validate_title(gallery_title) -> str:
    if any(chara in r'/\:*?"<>|' for chara in gallery_title):
        for chara in gallery_title:
            if chara in ['|', r'\\', r'/', ':']:
                gallery_title = re.sub(f'\{chara}', '-', gallery_title)
            elif chara == '"':
                gallery_title = re.sub(chara, "'", gallery_title)
            elif chara in '?*':
                gallery_title = re.sub(f'\{chara}', '', gallery_title)
            elif chara == '<':
                gallery_title = re.sub(chara, '(', gallery_title)
            elif chara == '>':
                gallery_title = re.sub(chara, ')', gallery_title)
    return gallery_title


def set_console_title(title_type=None, input_list_progress=None,artist_name=None, group_name=None, gallery_progress=None, gallery_id=None, download_progress=None, reset=False) -> None:
    global title
    final_title = ''
    if reset:
        title = {'program_title': program_title, 'title_type':  None, 'input_list_progress': None, 'artist_name': None, 'group_name': None, 'gallery_progress': None, 'gallery_id': None, 'download_progress': None}

    if title_type:
        title['title_type'] = title_type
        final_title = title['program_title'] + ' -   ' + title['title_type']

    else:
        final_title = title['program_title']
        if input_list_progress:
            title['input_list_progress'] = input_list_progress
            final_title += ' -   ' + title['input_list_progress']
        elif title['input_list_progress']:
            final_title += ' -   ' + title['input_list_progress']

        if artist_name:
            title['artist_name'] = artist_name
            final_title += '   Artist:' + title['artist_name']
        elif title['artist_name']:
            final_title += '   Artist:' + title['artist_name']

        if group_name:
            title['group_name'] = group_name
            final_title += '   Group:' + title['group_name']
        elif title['group_name']:
            final_title += '   Group:' + title['group_name']

        if gallery_progress:
            title['gallery_progress'] = gallery_progress
            final_title += '   ' + title['gallery_progress']
        elif title['gallery_progress']:
            final_title += '   ' + title['gallery_progress']

        if gallery_id:
            title['gallery_id'] = gallery_id
            final_title += '   Id:' + title['gallery_id']
        elif title['gallery_id']:
            final_title += '   Id:' + title['gallery_id']

        if download_progress:
            title['download_progress'] = download_progress
            final_title += '   ' + title['download_progress']
        elif title['download_progress']:
            final_title += '   ' + title['download_progress']

    if platform.system() == "Windows":
        try:
            subprocess.call('title ' + final_title, shell=True)
        except FileNotFoundError:
            print("error", f"Cannot set console title to {final_title}")
    else:
        sys.stdout.write(f"\x1b]2;{final_title}\x07")