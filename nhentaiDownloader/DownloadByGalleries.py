import os

import colorama

import nhentaiDownloader.nhentaiDownloadHandler as Downloader
from nhentaiDownloader.nhentaiMetadataHandler import MetadataHandler
import nhentaiDownloader.nhentaiHelper as Helper
from nhentaiDownloader.GalleriesFilter import GalleriesFilter

class DownloadByGalleries:
    def __init__(self, gallery_codes, save_dest):
        self.gallery_codes = gallery_codes
        self.save_dest = save_dest
        self.invalid_codes = list()
        self.name_too_long = list()

    def download_by_galleries(self, config, gallery_folder=None) -> None:
        for index, gallery_code in enumerate(self.gallery_codes, start=1):
            filter_ = GalleriesFilter(config=config, type_='gallery')
            response = filter_.check_database(get='ids', filter_option='ids', search_term=str(gallery_code), table='nhentaiLibrary', order_by='ids')
            if not response:
                os.chdir(self.save_dest)
                get_links_and_title_res = Helper.get_links_and_title(gallery_code)
                if not isinstance(get_links_and_title_res[0], list):
                    if gallery_folder is None:
                        if get_links_and_title_res[1] == 'name too long':
                            self.name_too_long.append((gallery_code, get_links_and_title_res[3]))
                        if get_links_and_title_res[1] == 'invalid code':
                            self.invalid_codes.append(gallery_code)
                        print()
                        continue
                    else:
                        image_links = get_links_and_title_res[2]
                else:
                    image_links = get_links_and_title_res[0]
                    if gallery_folder is None:
                        gallery_folder = get_links_and_title_res[1]
                print(f'Downloading {gallery_folder}...')
                gallery_progress = f'[{index} of {len(self.gallery_codes)}]'
                Helper.set_console_title(gallery_progress=gallery_progress, gallery_id=gallery_code)
                Downloader.downloader(image_links, os.path.abspath('.'), gallery_folder, config=config)
                
                metadata = MetadataHandler(gallery_code, config=config)
                try:
                    metadata.all_getter()
                except AttributeError:
                    pass
                os.chdir(self.save_dest)
            else:
                print(f'Gallery {gallery_code} is already in the database.')
            gallery_folder = None
            print()

        if len(self.name_too_long) > 0:
            for gallery_code, gallery_folder in self.name_too_long:
                self.gallery_codes = [gallery_code]
                Helper.log_and_print(error_family='OSError', error_type='name_too_long', gallery_title=gallery_folder)
                gallery_folder = input('Enter new, shorter destination name:')
                self.download_by_galleries(config=config, gallery_folder=gallery_folder)

        for invalid_code in self.invalid_codes:
            print(f'{colorama.Fore.RED}Invalid code: {colorama.Fore.BLUE}{invalid_code}')