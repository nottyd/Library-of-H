import sys
import os
import re
from pathlib import Path

import colorama

colorama.init(autoreset=True)

from nhentaiDownloader.DownloadArtist import DownloadArtist
from nhentaiDownloader.DownloadGallery import DownloadGallery
from nhentaiDownloader.DownloadGroup import DownloadGroup
from nhentaiDownloader.Config import Config
import nhentaiDownloader.Helper as Helper
import nhentaiErrorHandling.Logging as Logging

menu = """Choose a download method:
1. Download by Galleries
2. Download by Artists
3. Download by Groups
Enter x to exit.
>> """
config = Config()
while True:
    try:
        Helper.set_console_title(title_type="menu")
        choice = input(menu).lower()
        if choice == "1":
            gallery_codes = []
            for gallery_code in input(
                "Enter gallery code(s) separated by space: "
            ).split():
                if gallery_code not in gallery_codes:
                    gallery_codes.append(gallery_code)

            try:
                save_dest = config.gallerydownloadlocation
                if not Path(save_dest).exists():
                    os.makedirs(save_dest)
            except Exception as e:
                Logging.log_and_print(
                    print(
                        f"{colorama.Fore.RED}Error loading gallerydownloadlocation from nhentaiConfig.ini\
                    \ngallerydownloadlocation: {config.gallerydownloadlocation}\
                    \nError: {e}"
                    )
                )
                sys.exit()

            gallery_downloader = DownloadGallery(gallery_codes, save_dest, config)
            print()
            gallery_downloader.download_by_galleries()
            os.chdir(os.path.dirname(__file__))

        elif choice == "2":
            artists = []
            for artist in input("Enter artist name(s) separated by commas: ").split(
                ","
            ):
                if artist not in artists:
                    artists.append(artist.strip().lower())

            try:
                save_dest = config.artistdownloadlocation
                if not Path(save_dest).exists():
                    os.makedirs(save_dest)
            except Exception as e:
                Logging.log_and_print(
                    print(
                        f"{colorama.Fore.RED}Error loading artistdownloadlocation from nhentaiConfig.ini\
                    \artistdownloadlocation: {config.artistdownloadlocation}\
                    \nError: {e}"
                    )
                )
                sys.exit()

            artist_downloader = DownloadArtist(artists, save_dest, config)
            print()
            artist_downloader.download_by_artist()
            os.chdir(os.path.dirname(__file__))

        elif choice == "3":
            groups = []
            for group in input("Enter group name(s) separated by commas: ").split(","):
                if group not in groups:
                    groups.append(group.strip().lower())

            try:
                save_dest = config.groupdownloadlocation
                if not Path(save_dest).exists():
                    os.makedirs(save_dest)
            except Exception as e:
                Logging.log_and_print(
                    print(
                        f"{colorama.Fore.RED}Error loading groupdownloadlocation from nhentaiConfig.ini\
                    \groupdownloadlocation: {config.groupdownloadlocation}\
                    \nError: {e}"
                    )
                )
                sys.exit()

            group_downloader = DownloadGroup(groups, save_dest, config)
            print()
            group_downloader.download_by_group()
            os.chdir(os.path.dirname(__file__))

        elif choice == "x":
            sys.exit()

        else:
            continue

        print()
    except KeyboardInterrupt as e:
        print()
        print()
        continue
