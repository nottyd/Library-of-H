import os
import csv
import sys
import re

import nhentaiDownloader.nhentaiHelper as Helper
from nhentaiDownloader.nhentaiDBManager import nhentaiDBWriter

class MetadataHandler:
    def __init__(self, gallery_code, gallery_folder=None, config=None):
        try:
            self.config = config
            if 'metadata.csv' not in os.listdir():
                self.gallery_link = f'https://www.nhentai.net/g/{gallery_code}'
                self.tags_dict_list = []
                self.soup = Helper.soup_maker(self.gallery_link)
                self.collection = None
                if self.soup is None:
                    sys.exit()
            else:
                self.database_writer()
                raise Exception(f"metadata.csv already exists. Location: {os.path.abspath('.')}")
        except Exception as e:
            if 'metadata.csv already exists.' in str(e):
                print(e)

    def database_writer(self, all_=False):
        nhen_DBW_l = nhentaiDBWriter.nhentaiLibrary()
        if os.path.isdir(f'{self.config.databaselocation}'):
            nhen_DBW_l.set_database(self.config.databaselocation, metadata_location=os.path.abspath('.'))
        else:
            Helper.log_and_print(error_family='CONFError', error_type='databaselocation_load_error', cont_default=True)
            nhen_DBW_l.set_database(self.config.default_databaselocation, metadata_location=os.path.abspath('.'))

    def writer(self, tags_dict_list):
        if self.collection == 2:
            tags_dict_list.append({'tag': 'Type', 'tag_values': ['collection']})
        fieldnames = ['tag', 'tag_values']
        with open('metadata.csv', 'w', encoding='utf-8') as metadata_file:
            csv_writer = csv.DictWriter(metadata_file, fieldnames = fieldnames, delimiter=':')
            csv_writer.writeheader()
            csv_writer.writerows(tags_dict_list)

    def dict_list_maker(self, data_name, data):
        self.tags_dict_list.append({'tag': data_name, 'tag_values': data})
        if data_name == 'upload date':
            self.writer(self.tags_dict_list)

    def title_getter(self, all_=False):
        data = self.soup.find('span', class_='pretty').text
        if all_ == True:
            self.dict_list_maker('title', data)
        else:
            return data
        
    def code_getter(self, all_ = False):
        data = self.soup.find('h3', id='gallery_id').text[1:]
        if all_ == True:
            self.dict_list_maker('code', data)
        else:
            return data

    def parodies_getter(self, all_=False):
        data = [parody.get('href')[8:-1] for parody in self.soup.find_all('a', class_='tag') if parody.get('href').startswith('/parody/')]
        if len(data) == 1:
            data = data[0]
        elif len(data) <= 0:
            data = 'original'
        elif data == ['original'] or data == ['Original']:
            data = 'original'
        if all_ == True:
            self.dict_list_maker('parodies', data)
        else:
            if isinstance(data, list):
                return list(re.sub(' ', '-', data) for data in data)
            else:
                return data

    def characters_getter(self, all_=False):
        data = [character.get('href')[11:-1] for character in self.soup.find_all('a', class_='tag') if character.get('href').startswith('/character/')]
        if len(data) <= 0:
            data = 'None'
        if all_ == True:
            self.dict_list_maker('characters',data)
        else:
            if isinstance(data, list):
                return list(re.sub(' ', '-', data) for data in data)
            else:
                return data

    def tags_getter(self, all_=False):
        data = [tag.get('href')[5:-1] for tag in self.soup.find_all('a', class_='tag') if tag.get('href').startswith('/tag/')]
        if len(data) <= 0:
            data = 'None'
        if all_ == True:
            self.dict_list_maker('tags',data)
        else:
            if isinstance(data, list):
                return list(re.sub(' ', '-', data) for data in data)
            else:
                return data

    def artists_getter(self, all_=False):
        data = [artist.get('href')[8:-1] for artist in self.soup.find_all('a', class_='tag') if artist.get('href').startswith('/artist/')]
        if len(data) <= 0:
            data = 'None'
        if len(data) > 5:
            self.collection = 1
        if all_ == True:
            self.dict_list_maker('artists',data)
        else:
            return data
    
    def groups_getter(self, all_=False):
        data = [group.get('href')[7:-1] for group in self.soup.find_all('a', class_='tag') if group.get('href').startswith('/group/')]
        if len(data) <= 0:
            data = 'None'
        if all_ == True:
            self.dict_list_maker('groups',data)
        else:
            return data

    def languages_getter(self, all_=False):
        data = [language.get('href')[10:-1] for language in self.soup.find_all('a', class_='tag') if language.get('href').startswith('/language/')]
        if len(data) <= 0:
            data = 'None'
        if all_ == True:
            self.dict_list_maker('languages',data)
        else:
            if isinstance(data, list):
                return list(re.sub(' ', '-', data) for data in data)
            else:
                return data

    def categories_getter(self, all_=False):
        data = [category.get('href')[10:-1] for category in self.soup.find_all('a', class_='tag') if category.get('href').startswith('/category/')]
        if len(data) <= 0:
            data = 'None'
        if all_ == True:
            self.dict_list_maker('categories',data)
        else:
            if isinstance(data, list):
                return list(re.sub(' ', '-', data) for data in data)
            else:
                return data

    def pages_getter(self, all_=False):
        data = [str(page.string) for page in self.soup.find_all('a', class_='tag') if page.get('href').startswith('/search/?q=pages')]
        try:
            data = int(data[0])
        except Exception:
            data = 'None'
        if self.collection == 1 and isinstance(data, int) and data > 300:
            self.collection = 2
        if all_ == True:
            self.dict_list_maker('pages', data)
        else:
            return data

    def upload_date_getter(self, all_=False):
        upload_date = self.soup.find('time').get('datetime')
        if len(upload_date) <= 0:
            upload_date = 'None'
        else:
            upload_date = upload_date[:re.search('T', upload_date).start()]
        if all_ == True:
            self.dict_list_maker('upload date',upload_date)
        else:
            return upload_date

    def all_getter(self):
        self.title_getter(True)
        self.code_getter(True)
        self.parodies_getter(True)
        self.characters_getter(True)
        self.tags_getter(True)
        self.artists_getter(True)
        self.groups_getter(True)
        self.languages_getter(True)
        self.categories_getter(True)
        self.pages_getter(True)
        self.upload_date_getter(True)
        self.database_writer(True)