import os
from typing import Union

import nhentaiDownloader.nhentaiHelper as Helper
from nhentaiDownloader.nhentaiMetadataHandler import MetadataHandler
from nhentaiDownloader.nhentaiDBManager import nhentaiDBBrowser, nhentaiDBWriter

class GalleriesFilter:

    def __init__(self, config=None, type_=None):
        self.config = config
        self.type_ = type_
        self.codes_and_metadata = dict()

# Function to create a {'gallery_title': [metadata]} dictionary for each gallery code found in each artist page
    def metadata_getter(self, gallery_code) -> None:
        self.codes_and_metadata[gallery_code] = MetadataGetter(gallery_code)

    def filter_galleries_titles_getter(self, gallery_codes, type_ = None) -> None:
        if type_ is None: type_=self.type_
        gallery_metadata_dict = {}
        print(f'Collecting metadata for {type_} galleries...')
        Helper.print_bar_progress(total=len(gallery_codes), progress=0, msg='Metadata collected for galleries')
        for i, gallery_code in enumerate(gallery_codes, start=1):
            self.metadata_getter(gallery_code)
            Helper.print_bar_progress(total=len(gallery_codes), progress=i, msg='Metadata collected for galleries')
            links_and_title_getter_res = Helper.links_and_title_getter(gallery_code, filter_call=True)
            gallery_before = Helper.validate_title(links_and_title_getter_res[1][0])
            gallery_title = Helper.validate_title(links_and_title_getter_res[1][1])
            gallery_after = Helper.validate_title(links_and_title_getter_res[1][2])

            if gallery_title not in gallery_metadata_dict:
                gallery_metadata_dict[gallery_title] = (gallery_before, gallery_after, [gallery_code])
            else:
                gallery_metadata_dict[gallery_title][2].append(gallery_code)
        if self.config.collection:
            collection_filter = self.CollectionsFilter(gallery_metadata_dict=gallery_metadata_dict, codes_and_metadata=self.codes_and_metadata, config=self.config)
            gallery_metadata_dict, self.collections_count = collection_filter.get_items()
        if self.config.duplicate:
            duplicates_filter = self.DuplicatesFilter(self.codes_and_metadata, self.filtered_gallery_codes, config=self.config)
            self.filtered_gallery_codes = duplicates_filter.duplicate_galleries_handler(gallery_metadata_dict)
        else:
            for gallery_metadata in gallery_metadata_dict.values():
                for gallery_code in gallery_metadata[2]:
                    if gallery_code not in self.filtered_gallery_codes:
                        self.filtered_gallery_codes.append(gallery_code)

    def filter_galleries_getter(self, pages, url, type_=None) -> Union [None, list]:
        if type_ is None: type_=self.type_
        self.filtered_gallery_codes = list()
        gallery_codes = []
        for page in range(1, pages+1):
            page_url = f'{url}/?page={page}'
            page_soup = Helper.soup_maker(page_url)

            for gallery_code in page_soup.find_all('a', class_='cover'):
                gallery_codes.append(gallery_code.get('href')[3:-1])

        len_gallery_codes = len(gallery_codes)
        # Removing gallery codes that have already been downloaded in previous runs of the script
        gallery_codes = [gallery_code for gallery_code in gallery_codes if not self.check_database(get='ids', filter_option='ids', search_term=str(gallery_code), table='nhentaiLibrary', order_by='ids')]
        if len(gallery_codes) != 0:
            if len(gallery_codes) != len_gallery_codes:
                print(f"{len_gallery_codes-len(gallery_codes)}/{len_gallery_codes} of {type_}'s galleries are already in the database as downloaded.")
        else:
            print(f"All of {type_}'s galleries are already in the database.\n")
            return
        len_gallery_codes = len(gallery_codes)
        # Removing gallery_codes that belong to the collection category that have already been filtered in previous runs of the script, IF self.config.collection IS True (i.e. user doesn't want to download collections)
        if self.config.collection:
            gallery_codes = [gallery_code for gallery_code in gallery_codes if not self.check_database(get='collection_id', filter_option='collection_id', search_term=int(gallery_code), table='collections', order_by='collection_id')]
            if len(gallery_codes) != 0:
                if len(gallery_codes) != len_gallery_codes:
                    print(f"{len_gallery_codes-len(gallery_codes)}/{len_gallery_codes} have previously been filtered out as collections.")
                    len_gallery_codes = len(gallery_codes)
            else:
                print(f"{len_gallery_codes}/{len_gallery_codes} have previously been filtered out as collections.\n")
                return
        # Removing gallery codes that have already been filtered in previous runs of the script
        gallery_codes = [gallery_code for gallery_code in gallery_codes if not self.check_database(get='duplicate_id', filter_option='duplicate_id', search_term=str(gallery_code), table='duplicates', order_by='duplicate_id')]
        if len(gallery_codes) != 0:
            if len(gallery_codes) != len_gallery_codes:
                print(f"{len_gallery_codes-len(gallery_codes)} galleries have previously been filtered out as duplicates.")
                len_gallery_codes = len(gallery_codes)
            self.filter_galleries_titles_getter(gallery_codes, type_=type_)
            if self.config.collection:
                print(f'{self.collections_count} collections have been filtered out.')
            if len(self.filtered_gallery_codes) != len_gallery_codes and self.config.duplicate:
                print(f'{len_gallery_codes - len(self.filtered_gallery_codes) - self.collections_count} galleries have been filtered out as duplicates.')
            print()
            return self.filtered_gallery_codes
        else:
            print(f"{len_gallery_codes}/{len_gallery_codes} have previously been filtered out as duplicates.\n")

    # Function to filter already downloaded galleries
    def check_database(self, filter_option, search_term, get, table, order_by, order_in='ASC') -> Union[list, bool]:
        if os.path.isdir(self.config.databaselocation):
            database_location = self.config.databaselocation
        else:
            Helper.log_and_print(error_family='CONFError', error_type='databaselocation_load_error', cont_default=True)
            database_location = self.config.default_databaselocation

        if os.path.isfile(os.path.join(database_location, 'nhentaiDatabase.db')):
            nhen_DBB = nhentaiDBBrowser()
            nhen_DBB.set_database(database_location=database_location)
            try:
                response = nhen_DBB.sqlite_select(get=get, order_by=order_by, order_in=order_in, table=table, filter_option=filter_option, search_terms=search_term)[0]
            except:
                response = []
        else:
            response = []
        if response != []:
            return response
        else:
            return False

    class CollectionsFilter:
        def __init__(self, gallery_metadata_dict, codes_and_metadata, config) -> None:
            self.config = config
            self.codes_and_metadata = codes_and_metadata
            self.collections_count = 0
            self.nhen_DBW_f =  nhentaiDBWriter.FilteredCollections()
            if os.path.isdir(self.config.databaselocation):
                database_location = self.config.databaselocation
            else:
                Helper.log_and_print(error_family='CONFError', error_type='databaselocation_load_error', cont_default=True)
                database_location = self.config.default_databaselocation
            self.nhen_DBW_f.set_database(database_location=database_location, database_filename='nhentaiDatabase.db')
            self.gallery_metadata_dict = self.comic_galleries_filter(gallery_metadata_dict)
        
        def get_items(self) -> tuple:
            return self.gallery_metadata_dict, self.collections_count

        def anthology_galleries_filter(self, gallery_metadata_dict) -> dict:
            titles_to_del = set()
            for gallery_title, gallery_metadata in gallery_metadata_dict.items():
                codes_to_del = set()
                for gallery_code in gallery_metadata[2]:
                    if 'anthology' in gallery_metadata[0].lower():
                        codes_to_del.add(gallery_code)
                    elif 'anthology' in gallery_title.lower():
                        if len(self.codes_and_metadata[gallery_code].artists) > 2:
                            codes_to_del.add(gallery_code)
                    elif int(self.codes_and_metadata[gallery_code].pages) > 50 and len(self.codes_and_metadata[gallery_code].artists) > 2 and isinstance(self.codes_and_metadata[gallery_code].artists, list):
                        codes_to_del.add(gallery_code)
                self.nhen_DBW_f.update_database(codes_to_del)
                for code_to_del in codes_to_del:
                    gallery_metadata[2].remove(code_to_del)
                    self.collections_count += 1
                if len(gallery_metadata[2]) < 1:
                    titles_to_del.add(gallery_title)
            for title_to_del in titles_to_del:
                del gallery_metadata_dict[title_to_del]
            return gallery_metadata_dict


        def comic_galleries_filter(self, gallery_metadata_dict) -> dict:
            titles_to_del = set()
            for gallery_title, gallery_metadata in gallery_metadata_dict.items():
                codes_to_del = set()
                for gallery_code in gallery_metadata[2]:
                    if 'comic' in gallery_title.lower():
                        if len(self.codes_and_metadata[gallery_code].artists) > 2:
                            codes_to_del.add(gallery_code)
                    elif int(self.codes_and_metadata[gallery_code].pages) > 150 and len(self.codes_and_metadata[gallery_code].artists) > 2 and isinstance(self.codes_and_metadata[gallery_code].artists, list):
                        codes_to_del.add(gallery_code)
                self.nhen_DBW_f.update_database(codes_to_del)
                for code_to_del in codes_to_del:
                    gallery_metadata[2].remove(code_to_del)
                    self.collections_count += 1
                if len(gallery_metadata[2]) < 1:
                    titles_to_del.add(gallery_title)
            for title_to_del in titles_to_del:
                del gallery_metadata_dict[title_to_del]
            return self.anthology_galleries_filter(gallery_metadata_dict)


    class DuplicatesFilter:
        def __init__(self, codes_and_metadata, filtered_gallery_codes, config) -> None:
            self.config = config
            self.codes_and_metadata = codes_and_metadata
            self.filtered_gallery_codes = filtered_gallery_codes
            self.nhen_DBW_f =  nhentaiDBWriter.DownloadedAndDuplicates()
            if os.path.isdir(self.config.databaselocation):
                database_location = self.config.databaselocation
            else:
                Helper.log_and_print(error_family='CONFError', error_type='databaselocation_load_error', cont_default=True)
                database_location = self.config.default_databaselocation
            self.nhen_DBW_f.set_database(database_location=database_location, database_filename='nhentaiDatabase.db')

        def page_discrepancy(self, pages_dict) -> Union[str, list]:
            pages_list = sorted(list(pages_dict.values()))
            if max(pages_list) - min(pages_list) <= 6:
                return 'all_same'
            else:
                similar_galleries = None
                for i in range(len(pages_list)-1, 1, -1):
                    if max(pages_list[:i]) - min(pages_list[:i]) <= 6:
                        similar_galleries = pages_list[:i]
                if similar_galleries == None:
                    return 'all_diff'
                else:
                    return similar_galleries

        def pages_filter(self, gallery_codes, rec=0) -> None:
            pages_dict = {}
            duplicate_pages_dict = {}
            page_discrepancy_result = None
            if rec == 0:
                for gallery_code in gallery_codes:
                    if self.codes_and_metadata[gallery_code].pages is not None:
                        pages_dict[gallery_code] = self.codes_and_metadata[gallery_code].pages
                page_discrepancy_result = self.page_discrepancy(pages_dict)

                if isinstance(page_discrepancy_result, list):
                    keys_to_change = [gallery_code for gallery_code, page in pages_dict.items() if page in page_discrepancy_result]
                    for key in keys_to_change:
                        pages_dict[key] = min(page_discrepancy_result)

            if len(set(pages_dict.values())) == 1 or rec == 1 or page_discrepancy_result=='all_same':
                self.languages_filter(gallery_codes)
            elif len(set(pages_dict.values())) == len(gallery_codes) or rec == 2:
                for gallery_code in gallery_codes:
                    if gallery_code not in self.filtered_gallery_codes:
                        self.filtered_gallery_codes.append(gallery_code)
            else:
                for key, value in pages_dict.items():
                    if list(pages_dict.values()).count(value) > 1:
                        if value not in duplicate_pages_dict:
                            duplicate_pages_dict[value] = [key]
                        else:
                            duplicate_pages_dict[value].append(key)
                for key, values in duplicate_pages_dict.items():
                    for value in values:
                        del pages_dict[value]
                    self.pages_filter(values, rec=1)
                self.pages_filter(list(pages_dict.keys()), rec=2)

        def languages_filter(self, gallery_codes) -> None:
            gallery_language_dict = {gallery_code: self.codes_and_metadata[gallery_code].languages for gallery_code in gallery_codes}
            to_dels = set()
            gallery_codes = list(gallery_language_dict.keys())
            for i in range(0, len(gallery_codes)):
                for j in range(i+1, len(gallery_codes)):
                    if gallery_language_dict[gallery_codes[j]] == gallery_language_dict[gallery_codes[i]]:
                        to_dels.add(gallery_codes[j])
            for gallery_code in to_dels:
                del gallery_language_dict[gallery_code]
                self.nhen_DBW_f.update_database(downloaded_code=-1, duplicate_codes=[gallery_code])
            lang = 0
            for gallery_code, language in gallery_language_dict.items():
                if 'english' in language:
                    if gallery_code not in self.filtered_gallery_codes:
                        self.filtered_gallery_codes.append(gallery_code)
                    lang = 1
                    duplicate_codes = [gallery_code_ for gallery_code_ in gallery_language_dict.keys() if gallery_code_ != gallery_code]
                    self.nhen_DBW_f.update_database(downloaded_code=gallery_code, duplicate_codes=duplicate_codes)
                    break
            if lang != 1:
                for gallery_code, language in gallery_language_dict.items():
                    if 'japanese' in language:
                        if gallery_code not in self.filtered_gallery_codes:
                            self.filtered_gallery_codes.append(gallery_code)
                        lang = 2
                        duplicate_codes = [gallery_code_ for gallery_code_ in gallery_language_dict.keys() if gallery_code_ != gallery_code]
                        self.nhen_DBW_f.update_database(downloaded_code=gallery_code, duplicate_codes=duplicate_codes)
                        break
                if lang != 2:
                    if gallery_code not in self.filtered_gallery_codes:
                        self.filtered_gallery_codes.append(gallery_code)
                    duplicate_codes = [gallery_code_ for gallery_code_ in gallery_language_dict.keys() if gallery_code_ != gallery_code]
                    self.nhen_DBW_f.update_database(downloaded_code=gallery_code, duplicate_codes=duplicate_codes)

        def duplicate_galleries_handler(self, gallery_metadata_dict) -> list:
            for gallery_title, gallery_metadata in gallery_metadata_dict.items():
                if len(gallery_metadata[2]) > 1:
                    self.pages_filter(gallery_metadata[2])
                else:
                    if gallery_metadata[2][0] not in self.filtered_gallery_codes:
                        self.filtered_gallery_codes.append(gallery_metadata[2][0])
            return self.filtered_gallery_codes


class MetadataGetter:
    def __init__(self, gallery_code) -> None:
        metadata = MetadataHandler(gallery_code)
        self.pages = metadata.pages_getter()
        self.artists = metadata.artists_getter()
        self.languages = metadata.languages_getter()
        self.tags = metadata.tags_getter()
        self.characters = metadata.characters_getter()
        self.parodies = metadata.parodies_getter()
