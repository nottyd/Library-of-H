import os
import re

import colorama

colorama.init(autoreset=True)

from nhentaiDownloader.GalleriesFilter import GalleriesFilter
from nhentaiDownloader import Helper
from nhentaiDownloader import GalleriesDownloader
from nhentaiErrorHandling import nhentaiExceptions
from nhentaiErrorHandling.Logging import StaticVariables
from nhentaiErrorHandling.ExceptionHandling import exception_handling


class DownloadGroup:
    def __init__(self, groups, save_dest, config):
        self.groups = groups
        self.save_dest = save_dest
        self.config = config

    def download_by_group(self) -> None:
        for index, group in enumerate(self.groups, start=1):
            group_name = group.capitalize()

            input_list_progress = f"[{index} of {len(self.groups)}]"
            Helper.set_console_title(
                input_list_progress=input_list_progress,
                group_name=group_name,
                reset=True,
            )

            self.url = "https://www.nhentai.net/group/" + re.sub(" ", "-", group)
            try:
                group_soup = Helper.soup_maker(self.url)
            except BaseException as e:
                print(e)
                print(type(e))
                exception_handling(e)
                continue

            filter_ = GalleriesFilter(self.config)
            try:
                pages = group_soup.find_all("a", class_="last")[0].get("href")
            except IndexError:
                pages = 1
            else:
                pages = int(pages[re.search("=", pages).end() :])
            final_gallery_codes = filter_.filter_galleries_getter(
                pages, self.url, name=group_name
            )
            if final_gallery_codes != None:
                GalleriesDownloader.galleries_downloader(
                    *final_gallery_codes,
                    save_dest=self.save_dest,
                    config=self.config,
                    group_name=group_name,
                )

        self.handle_errors()

    def handle_errors(self):
        if StaticVariables.name_too_long.keys():
            for (
                group_name,
                gallery_codes_and_folders,
            ) in StaticVariables.name_too_long.items():
                for gallery_code_and_folder in gallery_codes_and_folders:
                    Helper.log_and_print(
                        error_family="OSError",
                        error_type="name_too_long",
                        gallery_title=gallery_code_and_folder[1],
                    )
                    gallery_folder = input("Enter new, shorter destination name:")
                    GalleriesDownloader.galleries_downloader(
                        gallery_folder=gallery_folder,
                        gallery_codes=[gallery_code_and_folder[0]],
                        group_name=group_name,
                    )

        if StaticVariables.invalid_groups:
            for invalid_group in StaticVariables.invalid_groups:
                print(
                    f"{colorama.Fore.RED}Invalid group: {colorama.Fore.BLUE}{invalid_group}"
                )
