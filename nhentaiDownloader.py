import sys
import os
import re
from pathlib import Path

import colorama
colorama.init(autoreset=True)

from nhentaiDownloader.DownloadByArtist import DownloadByArtist
from nhentaiDownloader.DownloadByGalleries import DownloadByGalleries
from nhentaiDownloader.DownloadByGroup import DownloadByGroup
from nhentaiDownloader.Config import Config
import nhentaiDownloader.Helper as Helper

menu = """Choose a download method:
1. Download by Galleries
2. Download by Artists
3. Download by Groups
Enter x to exit.
>> """
config = Config()
try:
    while True:
        Helper.set_console_title(title_type="menu")
        choice = input(menu).lower()
        if choice == '1':
            gallery_codes = []
            for gallery_code in input('Enter gallery code(s) separated by space: ').split():
                if gallery_code not in gallery_codes:
                    gallery_codes.append(gallery_code)
            try:
                save_dest = config.gallerydownloadlocation
                if not Path(save_dest).exists():
                    os.makedirs(save_dest)
            except Exception:
                print(f'{colorama.Fore.RED}Error loading gallerydownloadlocation from nhentaiConfig.ini, continuing with default: {colorama.Fore.WHITE}{config.default_gallerydownloadlocation}')
                save_dest = config.default_gallerydownloadlocation
                if not Path(save_dest).exists():
                    os.makedirs(save_dest)
            gallery_downloader = DownloadByGalleries(gallery_codes, save_dest)
            print()
            gallery_downloader.download_by_galleries(config)
            os.chdir(os.path.dirname(__file__))

        elif choice == '2':
            artists = []
            for artist in input('Enter artist name(s) separated by commas: ').split(','):
                if artist not in artists:
                    artists.append(artist.strip().lower())

            try:
                save_dest = config.artistdownloadlocation
                if not Path(save_dest).exists():
                    os.makedirs(save_dest)
            except Exception:
                print(f'{colorama.Fore.RED}Error loading artistdownloadlocation from nhentaiConfig.ini, continuing with default: {colorama.Fore.WHITE}{config.default_artistdownloadlocation}')
                save_dest = config.default_artistdownloadlocation
                if not Path(save_dest).exists():
                    os.makedirs(save_dest)
        
            artist_downloader = DownloadByArtist(artists, save_dest)
            print()
            artist_downloader.download_by_artist(config)
            os.chdir(os.path.dirname(__file__))

        elif choice == '3':
            groups = []
            for group in input('Enter group name(s) separated by commas: ').split(','):
                if group not in groups:
                    groups.append(group.strip().lower())

            try:
                save_dest = config.groupdownloadlocation
                if not Path(save_dest).exists():
                    os.makedirs(save_dest)
            except Exception:
                print(f'{colorama.Fore.RED}Error loading groupdownloadlocation from nhentaiConfig.ini, continuing with default: {colorama.Fore.WHITE}{config.default_groupdownloadlocation}')
                save_dest = config.default_groupdownloadlocation
                if not Path(save_dest).exists():
                    os.makedirs(save_dest)

            group_downloader = DownloadByGroup(groups, save_dest)
            print()
            group_downloader.download_by_group(config)
            os.chdir(os.path.dirname(__file__))

        elif choice == 'x':
            sys.exit()

        else:
            continue

        print()
except KeyboardInterrupt as e:
    Helper.set_console_title(title_type="exit")
    input('\nEnter to exit.')