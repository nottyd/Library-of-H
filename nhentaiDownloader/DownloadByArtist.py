import os
import re
import sys

import colorama
colorama.init(autoreset=True)

from nhentaiDownloader.GalleriesFilter import GalleriesFilter
from nhentaiDownloader.MetadataHandler import MetadataHandler
import nhentaiDownloader.Helper as Helper
import nhentaiDownloader.DownloadHandler as Downloader

class DownloadByArtist:
    def __init__(self, artists, save_dest):
        self.artists = artists
        self.save_dest = save_dest
        self.invalid_artists = []
        self.invalid_codes = []
        self.name_too_long = dict()

    def artist_galleries_downloader(self, gallery_codes, artist_name, config, gallery_folder=None) -> None:
        for index, gallery_code in enumerate(gallery_codes, start=1):
            get_links_and_title_res = Helper.get_links_and_title(gallery_code, artist_name=artist_name)
            if not isinstance(get_links_and_title_res[0], list):
                if gallery_folder is None:
                    if get_links_and_title_res[1] == 'name too long':
                        if artist_name in self.name_too_long.keys():
                            self.name_too_long[artist_name].append((gallery_code, get_links_and_title_res[3]))
                        else:
                            self.name_too_long[artist_name] = [(gallery_code, get_links_and_title_res[3])]
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
            gallery_progress = f'[{index} of {len(gallery_codes)}]'
            Helper.set_console_title(gallery_progress=gallery_progress, gallery_id=gallery_code)
            Downloader.downloader(image_links=image_links, save_dest=self.save_dest , folder=gallery_folder, config=config)

            metadata = MetadataHandler(gallery_code, config=config)
            try:
                metadata.all_getter()
            except AttributeError:
                pass
                os.chdir(self.save_dest)
            print()

    def download_by_artist(self, config) -> None:
        for index, artist in enumerate(self.artists, start=1):
            filter_ = GalleriesFilter(config, type_='artist')
            try:
                os.chdir(self.save_dest)
            except FileNotFoundError as e:
                sys.exit(e)
            except Exception as e:
                sys.exit(e)
            else:
                artist_name = artist.capitalize()

                input_list_progress = f'[{index} of {len(self.artists)}]'
                Helper.set_console_title(input_list_progress=input_list_progress, artist_name=artist_name, reset=True)

                self.url = 'https://www.nhentai.net/artist/' + re.sub(' ', '-', artist)

                artist_soup = Helper.soup_maker(self.url)
                if str(type(artist_soup)) == "<class 'bs4.BeautifulSoup'>":
                    try:
                        pages = artist_soup.find_all('a', class_='last')[0].get('href')
                    except IndexError:
                            pages = 1
                    else:
                        pages = int(pages[re.search('=', pages).end():])
                    final_gallery_codes = filter_.filter_galleries_getter(pages, self.url, type_=artist_name)
                    if final_gallery_codes != None:
                        self.artist_galleries_downloader(final_gallery_codes, artist_name, config)
                elif artist_soup == 404:
                    if artist not in self.invalid_artists:
                        self.invalid_artists.append(artist)
                else:
                     continue

        if len(self.name_too_long.keys()) > 0:
            for artist_name, gallery_codes_and_folders in self.name_too_long.items():
                for gallery_code_and_folder in gallery_codes_and_folders:
                    Helper.log_and_print(error_family='OSError', error_type='name_too_long', gallery_title=gallery_code_and_folder[1])
                    gallery_folder = input('Enter new, shorter destination name:')
                    self.artist_galleries_downloader(gallery_folder=gallery_folder, gallery_codes=[gallery_code_and_folder[0]], config=config, artist_name=artist_name)

        if len(self.invalid_artists) > 0:
            for invalid_artist in self.invalid_artists:
                print(f'{colorama.Fore.RED}Invalid artist: {colorama.Fore.BLUE}{invalid_artist}')
        
        if len(self.invalid_codes) > 0:
            for invalid_code in self.invalid_codes:
                print(f'{colorama.Fore.RED}Invalid code: {colorama.Fore.BLUE}{invalid_code}')