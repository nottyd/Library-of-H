import sys
import re
import time
import itertools
import logging

import mechanize
from bs4 import BeautifulSoup
import colorama
colorama.init(autoreset=True)

from nhentaiDownloader.nhentaiConfig import nhentaiConfig

config = nhentaiConfig()

def log_and_print(error_family=None, error_type=None, error=None, error_msg='', gallery_title=None, original_title=None, download_type=None, cont_default=None, retry=None):
    if error_msg != '':
        print(error_msg)
        return

    if error_family == 'URLError':
        error_msg = f'{colorama.Fore.RED}<{str(error)}>'
        if error_type == 'temporary':
            error_msg += ' Temporary Error.'
        error_msg += f'\n{colorama.Fore.RED}URL => {colorama.Fore.BLUE}{error.url}'

    elif error_family == 'OSError':
        if error_type == 'network':
            error_msg = f'{colorama.Fore.RED}{str(error)}'
        elif error_type == 'name_too_long':
            error_msg = f'{colorama.Fore.RED}[file name too long]: {colorama.Fore.BLUE}{gallery_title}'
            if retry:
                error_msg += f'\n{colorama.Fore.RED}Retrying with: {colorama.Fore.BLUE}{original_title}'

    elif error_family == 'CONFError':
        if error_type == 'unavailable_languages':
            error_msg = f'{colorama.Fore.RED}Error formatting title with %(translated_title)s and/or %(original_title)s: Title not available in those languages.'
        elif error_type == 'downloadname_load_error':
            error_msg = f'{colorama.Fore.RED}Error loading {download_type}downloadnameformat from nhentaiConfig.ini: {error}'
            if cont_default:
                if download_type == 'artist':
                    defaults = config.default_artistdownloadnameformat
                elif download_type == 'group':
                    defaults = config.default_groupdownloadnameformat
                elif download_type == 'gallery':
                    defaults = config.default_gallerydownloadnameformat
        elif error_type == 'databaselocation_load_error':
            error_msg = f'{colorama.Fore.RED}Error loading databaselocation from nhentaiConfig.ini: {error}'
            if cont_default:
                defaults = config.default_databaselocation
        if cont_default:
            error_msg += f'\n{colorama.Fore.RED}Continuing with defaults: {colorama.Fore.BLUE}{defaults}'



    error_msg += '\n'
    print(error_msg)

# Funcction to create Browser object
def browser_factory():
    br = mechanize.Browser()
    br.set_handle_robots(False)
    request = get_request('https://www.nhentai.net')
    return br

# Function to create beautifulsoup object
def soup_maker(url):
    request = get_request(url)
    response = get_response_with_retry(request)
    if str(type(response)) == "<class 'mechanize._response.response_seek_wrapper'>":
        response = response.read()
        soup = BeautifulSoup(response, 'lxml')
    else:
        soup = response

    return soup

# Function to get response with mechanize and retry 3 times
def get_response_with_retry(request):
    errno = 0
    br = browser_factory()
    for i in range(config.retry+1):
        try:
           response = br.open(request)
        except mechanize.HTTPError as e:
            if e.getcode() >= 400 and e.getcode() <= 511:
                if e.getcode() == 403: # Forbidden
                    log_and_print(error_family='URLError', error_type='forbidden', error=e)
                    return e.getcode()
                elif e.getcode() == 404 or e.getcode() == 410: # Page Not Found and Page Gone
                    log_and_print(error_family='URLError', error_type='page_not_found', error=e)
                    return e.getcode()
                elif e.getcode() in [408, 429, 500, 502, 503, 504]:
                    # 408: Request Timeout;
                    # 429: Too Many Requests;
                    # 500: Internal Server Error;
                    # 502: Bad Gateway;
                    # 504: Gateway Timeout
                    print()
                    log_and_print(error_family='URLError', error_type='temporary', error=e)
                    print(f'{colorama.Fore.WHITE}{i+1} try out of {config.retry}.')
                    time.sleep(config.retrywait)
        except OSError as e:
            if i+1 == config.retry+1:
                print(f'{colorama.Fore.RED}Out of retries.')
                return None
            if e.args[0].errno == 10053 or errno == 10053:
                log_and_print(error_family='OSError', error_type='network', error=e)
                while True:
                    print(f'{colorama.Fore.WHITE}Would you like to retry?(y/n) ', end='')
                    retry = input()
                    if retry.lower() == 'y':
                        print(f'{i+1} try out of {config.retry}.')
                        break
                    if retry.lower() == 'n':
                        return None
                    print()
                errno = 10053
            elif e.args[0].errno == 2:
                log_and_print(error_family='OSError', error_type='network', error=e)
                while True:
                    print(f'{colorama.Fore.WHITE}Would you like to retry?(y/n) ', end='')
                    retry = input()
                    if retry.lower() == 'y':
                        print(f'{i+1} try out of {config.retry}.')
                        break
                    if retry.lower() == 'n':
                        return None
                    print()
            print()
        else:
            return response
    print()
    return None

# Function to get request
def get_request(url):
    return mechanize.Request(url, None, {'User-Agent':config.useragent})

# Functions for printing progress
# Function for printing bar progress: [########-------]
def print_bar_progress(bar_length=20, total=20, progress=1, msg=None):
    if total == 0: total = 1
    done = (progress*100)/total
    done = int((done/100)*bar_length)
    print('\r{}{} {} of {}: [{}{}]'.format(colorama.Fore.WHITE, msg, progress, total, '#'*done, '-'*(bar_length-done)), end='')
    if done == bar_length:
        print()

# Function for converting list of thumbnail links to list of actual image links.
def link_converter(image_links):  
    t_image_links = [re.sub('https://t.nhentai.net/galleries/', 'https://i.nhentai.net/galleries/', image_link) for image_link in image_links]
    image_links = t_image_links
    t_image_links = [re.sub('t', '', image_link[::-1], count=1) for image_link in image_links]
    image_links = [t_image_link[::-1] for t_image_link in t_image_links]

    return list(image_links)

# Function for creating a list of thumbnail links.
def links_and_title_getter(gallery_code, filter_call=False):
    gallery_url = 'https://www.nhentai.net/g/{}'.format(gallery_code)
    soup = soup_maker(gallery_url)
    try:
        gallery_before = soup.find('span', class_='before').text
    except Exception:
        gallery_before = ''
    try:
        gallery_pretty = soup.find('span', class_='pretty').text
        temp = gallery_pretty.split('|') # translated and original titles are usually seperated my a '|'
        if len(temp) == 2 and not filter_call:
            translated_title = temp[1]
            original_title = temp[0]
            gallery_pretty = (original_title, translated_title)
    except Exception:
        gallery_pretty = ''
    try:
        gallery_after = soup.find('span', class_='after').text
    except Exception:
        gallery_after = ''
    gallery_title = (gallery_before, gallery_pretty, gallery_after)
    if soup is not None:
        page_links = [str(link.get('src')) for link in soup.find_all('img')]
        image_links = [t_image_link for page_link in page_links for t_image_link in re.findall('https://t.nhentai.net/galleries/.+/.+t\..+', page_link)]
        return (link_converter(image_links), gallery_title)
    else:
        return gallery_code

def get_links_and_title(gallery_code=None, artist_name=None, group_name=None):
    if gallery_code is not None:
        links_and_title_getter_res = links_and_title_getter(gallery_code)
        if type(links_and_title_getter_res) is str:
            return gallery_code, 'invalid code'
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
            try:
                temp = original_title
                log_and_print(error_family='OSError', error_type='name_too_long', gallery_title=gallery_title, original_title=original_title, retry=True)
                gallery_title = original_title
            except Exception:
                pass
        gallery_after = validate_title(links_and_title_getter_res[1][2])
    if artist_name is not None:
        try:
            gallery_folder = config.artistdownloadnameformat % locals()
        except KeyError as e:
            if not translated_title or not original_title:
                log_and_print(error_family='CONFError', error_type='unavailable_languages', download_type='artist', cont_default=True)
                gallery_folder = config.default_artistdownloadnameformat % locals()
            else:
                log_and_print(error_family='CONFError', error_Type='downloadname_load_error', error=e, download_type='artist', cont_default=True)
                gallery_folder = config.default_artistdownloadnameformat % locals()
        except Exception as e:
            log_and_print(error_family='CONFError', error_Type='downloadname_load_error', error=e, download_type='artist', cont_default=True)
            gallery_folder = config.default_artistdownloadnameformat % locals()
    elif group_name is not None:
        try:
            gallery_folder = config.groupdownloadnameformat % locals()
        except KeyError as e:
            if not translated_title or not original_title:
                log_and_print(error_family='CONFError', error_type='unavailable_languages', download_type='group', cont_default=True)
                gallery_folder = config.default_groupdownloadnameformat % locals()
            else:
                log_and_print(error_family='CONFError', error_Type='downloadname_load_error', error=e, download_type='group', cont_default=True)
                gallery_folder = config.default_groupdownloadnameformat % locals()
        except Exception as e:
            log_and_print(error_family='CONFError', error_Type='downloadname_load_error', error=e, download_type='group', cont_default=True)
            gallery_folder = config.default_groupdownloadnameformat % locals()
    else:
        try:
            gallery_folder = config.gallerydownloadnameformat % locals()
        except KeyError as e:
            if not translated_title or not original_title:
                log_and_print(error_family='CONFError', error_type='unavailable_languages', download_type='gallery', cont_default=True)
                gallery_folder = config.default_gallerydownloadnameformat % locals()
            else:
                log_and_print(error_family='CONFError', error_Type='downloadname_load_error', error=e, download_type='gallery', cont_default=True)
                gallery_folder = config.default_gallerydownloadnameformat % locals()

        except Exception as e:
            log_and_print(error_family='CONFError', error_Type='downloadname_load_error', error=e, download_type='gallery', cont_default=True)
            gallery_folder = config.default_gallerydownloadnameformat % locals()

    if len(gallery_folder.split('\\')[-1]) > 250:
        log_and_print()
        log_and_print(error_family='OSError', error_type='name_too_long', gallery_title=gallery_title, retry=False)
        return gallery_code, 'name too long', image_links, gallery_folder

    return image_links, gallery_folder

# Function to validate title i.e: remove/replace special characters
def validate_title(gallery_title):
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