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

    def handle_errors(self):
        if len(StaticVariables.name_too_long) > 0:
            for gallery_code, gallery_folder in StaticVariables.name_too_long:
                self.gallery_codes = [gallery_code]
                Helper.log_and_print(
                    error_family="OSError",
                    error_type="name_too_long",
                    gallery_title=gallery_folder,
                )
                gallery_folder = input("Enter new, shorter destination name:")
                self.download_by_galleries(
                    config=self.config, gallery_folder=gallery_folder
                )

        for invalid_code in StaticVariables.invalid_codes:
            print(
                f"{colorama.Fore.RED}Invalid code: {colorama.Fore.BLUE}{invalid_code}"
            )
