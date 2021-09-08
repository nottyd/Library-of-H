import os

import colorama

from nhentaiDownloader.GalleriesFilter import GalleriesFilter
from nhentaiDownloader.MetadataHandler import MetadataHandler
from nhentaiDownloader import Helper
from nhentaiDownloader import GalleriesDownloader
from nhentaiErrorHandling.Logging import StaticVariables


class DownloadGallery:
    def __init__(self, gallery_codes, save_dest, config):
        self.config = config
        self.gallery_codes = gallery_codes
        self.save_dest = save_dest

    def download_by_galleries(self, gallery_folder=None) -> None:
        for index, gallery_code in enumerate(self.gallery_codes, start=1):
            filter_ = GalleriesFilter(config=self.config)
            response = filter_.check_database(
                get="ids",
                filter_option="ids",
                search_term=str(gallery_code),
                table="nhentaiLibrary",
                order_by="ids",
            )
            if not response:
                GalleriesDownloader.galleries_downloader(
                    gallery_code,
                    save_dest=self.save_dest,
                    config=self.config,
                )
            else:
                print(f"Gallery {gallery_code} is already in the database.")
            gallery_folder = None
            print()

        self.handle_errors()

    def handle_errors(self):
        if StaticVariables.invalid_galleries:
            print()
            for invalid_gallery in StaticVariables.invalid_galleries:
                print(
                    f"{colorama.Fore.RED}Invalid gallery ID: {colorama.Fore.BLUE}{invalid_gallery}"
                )
