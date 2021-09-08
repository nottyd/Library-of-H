import os
import re

import colorama

colorama.init(autoreset=True)

from nhentaiDownloader.GalleriesFilter import GalleriesFilter
from nhentaiDownloader import Helper
from nhentaiDownloader import GalleriesDownloader
from nhentaiErrorHandling.Logging import StaticVariables
from nhentaiErrorHandling.ExceptionHandling import exception_handling


class DownloadArtist:
    def __init__(self, artists, save_dest, config):
        self.artists = artists
        self.save_dest = save_dest
        self.config = config

    def download_by_artist(self) -> None:
        for index, artist in enumerate(self.artists, start=1):
            artist_name = artist.capitalize()

            input_list_progress = f"[{index} of {len(self.artists)}]"
            Helper.set_console_title(
                input_list_progress=input_list_progress,
                artist_name=artist_name,
                reset=True,
            )

            self.url = "https://www.nhentai.net/artist/" + re.sub(" ", "-", artist)
            try:
                artist_soup = Helper.soup_maker(self.url)
            except BaseException as e:
                exception_handling(e)
                continue

            filter_ = GalleriesFilter(self.config)
            try:
                pages = artist_soup.find_all("a", class_="last")[0].get("href")
            except IndexError:
                pages = 1
            else:
                pages = int(pages[re.search("=", pages).end() :])
            final_gallery_codes = filter_.filter_galleries_getter(
                pages, self.url, name=artist_name
            )
            if final_gallery_codes != None:
                GalleriesDownloader.galleries_downloader(
                    *final_gallery_codes,
                    save_dest=self.save_dest,
                    config=self.config,
                    artist_name=artist_name,
                )

        self.handle_errors()

    def handle_errors(self):
        if StaticVariables.invalid_artists:
            print()
            for invalid_artist in StaticVariables.invalid_artists:
                print(
                    f"{colorama.Fore.RED}Invalid artist name: {colorama.Fore.BLUE}{invalid_artist}"
                )
