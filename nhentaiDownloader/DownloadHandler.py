import re
import os
import sys
from pathlib import Path

import requests

from nhentaiDownloader import Helper

# Function for downloading image
def downloader(image_links, save_dest, folder, config) -> None:

    """
    Function to get image from link and write the data to disk.
    image_links: List of links of images in a single gallery.
    save_dest: Base save destination from config.ini. Example: ./nhentaiDownloaded/artists
    folder: Destation to save the downloaded images to, is added on top of save_dest. Example: artist_name/gallery_id
    config: Config.py object.
    """

    already_downloaded = 0
    done = False
    len_image_links = len(image_links)

    for index, image_link in enumerate(image_links, start=1):
        while not done:
            # Initiating console title and download progressbar
            if image_links[0] == image_link:
                Helper.print_bar_progress(total=len_image_links, progress=0, msg='Downloaded pages')
                Helper.set_console_title(download_progress=f'[{0} / {len_image_links}]')
            if already_downloaded != 0:
                Helper.print_bar_progress(total=len_image_links, progress=already_downloaded+(index-already_downloaded), msg='Downloaded pages')
                Helper.set_console_title(download_progress=f'[{already_downloaded+(index-already_downloaded)} / {len_image_links}]')

            try:
                if not Path(os.path.join(save_dest, folder)).exists():
                    os.makedirs(os.path.join(save_dest, folder))
                os.chdir(os.path.join(save_dest, folder))
                done = True
            except OSError as e:
                if '[chinese]' in folder.lower():
                    msg = f'{e} \nRemoving Chinese title and retrying. (Some Chinese characters are not counted as a single character by the OS.)'
                    Helper.log_and_print(error_family='OSError', error_msg=msg)
                    gallery_code = folder[re.search('\([0-9]+\)$', folder).start():re.search('\([0-9]+\)$', folder).end()]
                    folder = folder.split('[Chinese]')
                    folder = folder[0] + f' {gallery_code}'
                else:
                    sys.exit(e)

        image_name = image_link[re.search('[0-9]+.[a-z]+', image_link).start():re.search('[0-9]+.[a-z]+', image_link).end()]

        if not config.overwrite:
            if not os.path.exists(image_name):
                _write_to_disk(image_link=image_link, config=config, image_name=image_name, len_image_links=len_image_links, index=index)
            else:
                already_downloaded+=1
            if already_downloaded == len_image_links:
                print(f'\r{os.path.join(save_dest, folder)} already exists.')
        else:
            _write_to_disk(image_link=image_link, config=config, image_name=image_name, len_image_links=len_image_links, index=index)

def _write_to_disk(image_link, config, image_name, len_image_links, index):
    with requests.get(image_link, headers={'User-Agent':config.useragent}, stream=True) as online_image:
        online_image.raise_for_status()
        with open(image_name, 'wb') as f:
            for chunk in online_image.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
            Helper.print_bar_progress(total=len_image_links, progress=index, msg='Downloaded pages')
            Helper.set_console_title(download_progress=f'[{index} / {len_image_links}]')