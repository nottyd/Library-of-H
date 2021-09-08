import os
import sys

from nhentaiDownloader import DownloadHandler as Downloader
from nhentaiDownloader import Helper
from nhentaiDownloader.MetadataHandler import MetadataHandler
from nhentaiErrorHandling import nhentaiExceptions
from nhentaiErrorHandling.ExceptionHandling import exception_handling


def galleries_downloader(
    *gallery_codes,
    save_dest,
    config,
    gallery_folder=None,
    artist_name=None,
    group_name=None,
):
    os.chdir(save_dest)
    for index, gallery_code in enumerate(gallery_codes, start=1):
        try:
            get_links_and_title_res = Helper.get_links_and_title(
                gallery_code, artist_name=artist_name, group_name=group_name
            )
        except Exception as e:
            print("yep", e)
            exception_handling(e)
            continue

        if not gallery_folder is None:
            pass
        else:
            image_links = get_links_and_title_res[0]
            gallery_folder = get_links_and_title_res[1]
        print(f"Downloading {gallery_folder}...")
        gallery_progress = f"[{index} of {len(gallery_codes)}]"
        Helper.set_console_title(
            gallery_progress=gallery_progress, gallery_id=gallery_code
        )
        Downloader.downloader(
            image_links=image_links,
            save_dest=save_dest,
            folder=gallery_folder,
            config=config,
        )

        metadata = MetadataHandler(gallery_code, config=config)
        try:
            metadata.all_getter()
        except AttributeError:
            pass
        os.chdir(save_dest)
        print()
        gallery_folder = None
