import os
import re
import sys

import colorama
colorama.init(autoreset=True)

from nhentaiDownloader.GalleriesFilter import GalleriesFilter
from nhentaiDownloader.nhentaiMetadataHandler import MetadataHandler
import nhentaiDownloader.nhentaiHelper as Helper
import nhentaiDownloader.nhentaiDownloadHandler as Downloader

class DownloadByGroup:
    def __init__(self, groups, save_dest):
        self.groups = groups
        self.save_dest = save_dest
        self.invalid_groups = []
        self.invalid_codes = []
        self.name_too_long = dict()

    def group_galleries_downloader(self, gallery_codes, group_name, config, gallery_folder=None) -> None:
        for gallery_code in gallery_codes:
            get_links_and_title_res = Helper.get_links_and_title(gallery_code, group_name=group_name)
            if not isinstance(get_links_and_title_res[0], list):
                if gallery_folder is None:
                    if get_links_and_title_res[1] == 'name too long':
                        if group_name in self.name_too_long.keys():
                            self.name_too_long[group_name].append((gallery_code, get_links_and_title_res[3]))
                        else:
                            self.name_too_long[group_name] = [(gallery_code, get_links_and_title_res[3])]
                    if get_links_and_title_res[1] == 'invalid code':
                        self.invalid_codes.append(gallery_code)
                    print()
                    continue
                else:
                    image_links = get_links_and_title_res[2]
            else:
                image_links = get_links_and_title_res[0]
                gallery_folder = get_links_and_title_res[1]
            print(f'Downloading {gallery_folder}...')
            Downloader.downloader(image_links=image_links, save_dest=self.save_dest , folder=gallery_folder, config=config)

            metadata = MetadataHandler(gallery_code, config=config)
            try:
                metadata.all_getter()
            except AttributeError:
                pass
                os.chdir(self.save_dest)
            print()

    def download_by_group(self, config) -> None:
        for group in self.groups:
            filter_ = GalleriesFilter(config, type_='group')
            try:
                os.chdir(self.save_dest)
            except FileNotFoundError as e:
                sys.exit(e)
            except Exception as e:
                sys.exit(e)
            else:
                group_name = group.capitalize()
                self.url = 'https://www.nhentai.net/group/' + re.sub(' ', '-', group)

                group_soup = Helper.soup_maker(self.url)
                if str(type(group_soup)) == "<class 'bs4.BeautifulSoup'>":
                    try:
                        pages = group_soup.find_all('a', class_='last')[0].get('href')
                    except IndexError:
                            pages = 1
                    else:
                        pages = int(pages[re.search('=', pages).end():])
                    final_gallery_codes = filter_.filter_galleries_getter(pages, self.url, type_=group_name)
                    if final_gallery_codes != None:
                        self.group_galleries_downloader(final_gallery_codes, group_name, config)
                elif group_soup == 404:
                    if group not in self.invalid_groups:
                        self.invalid_groups.append(group)
                else:
                     continue

        if len(self.name_too_long.keys()) > 0:
            for group_name, gallery_codes_and_folders in self.name_too_long.items():
                for gallery_code_and_folder in gallery_codes_and_folders:
                    Helper.log_and_print(error_family='OSError', error_type='name_too_long', gallery_title=gallery_code_and_folder[1])
                    gallery_folder = input('Enter new, shorter destination name:')
                    self.group_galleries_downloader(gallery_folder=gallery_folder, gallery_codes=[gallery_code_and_folder[0]], config=config, group_name=group_name)

        if len(self.invalid_groups) > 0:
            for invalid_group in self.invalid_groups:
                print(f'{colorama.Fore.RED}Invalid group: {colorama.Fore.BLUE}{invalid_group}')
        
        if len(self.invalid_codes) > 0:
            for invalid_code in self.invalid_codes:
                print(f'{colorama.Fore.RED}Invalid code: {colorama.Fore.BLUE}{invalid_code}')