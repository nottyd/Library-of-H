import re
import os
import sys
from pathlib import Path

import nhentaiDownloader.Helper as Helper

# Function for downloading image
def downloader(image_links, save_dest, folder, config) -> bool:
    already_downloaded = 0
    done = False
    for index, image_link in enumerate(image_links, start=1):
        while not done:
            if image_links[0] == image_link:
                Helper.print_bar_progress(total=len(image_links), progress=0, msg='Downloaded pages')
                Helper.set_console_title(download_progress=f'[{0} / {len(image_links)}]')
            if already_downloaded != 0:
                Helper.print_bar_progress(total=len(image_links), progress=already_downloaded+(index-already_downloaded), msg='Downloaded pages')
                Helper.set_console_title(download_progress=f'[{already_downloaded+(index-already_downloaded)} / {len(image_links)}]')
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

        request = Helper.get_request(image_link)
        image_name = image_link[re.search('[0-9]+.[a-z]+', image_link).start():re.search('[0-9]+.[a-z]+', image_link).end()]
        if not config.overwrite:
            if not os.path.exists(image_name):
                online_image = Helper.get_response_with_retry(request)
                with open(image_name, 'wb') as f:
                    chunk = 4096
                    data_read = online_image.read(chunk)
                    while True:
                        f.write(data_read)
                        data_read = online_image.read(chunk)
                        if not data_read:
                            Helper.print_bar_progress(total=len(image_links), progress=already_downloaded+(index-already_downloaded), msg='Downloaded pages')
                            Helper.set_console_title(download_progress=f'[{already_downloaded+(index-already_downloaded)} / {len(image_links)}]')
                            break
            else:
                already_downloaded+=1
            if already_downloaded == len(image_links):
                print(f'\r{os.path.join(save_dest, folder)} already exists.')
        else:
            online_image = Helper.get_response_with_retry(request)
            with open(image_name, 'wb') as f:
                chunk = 4096
                data_read = online_image.read(chunk)
                while True:
                    f.write(data_read)
                    data_read = online_image.read(chunk)
                    if not data_read:
                        Helper.print_bar_progress(total=len(image_links), progress=index, msg='Downloaded pages')
                        Helper.set_console_title(download_progress=f'[{index} / {len(image_links)}]')
                        break

    return True