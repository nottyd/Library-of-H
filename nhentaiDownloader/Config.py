import configparser
import os
import itertools
import sys
import re

_config_file_location = os.path.dirname(__file__)

class ConfigItems:
    def __init__(self, section, option, default, fallback=None):
        self.section = section
        self.option = option
        self.default = default


class Config:
    config_default = [
        ConfigItems('Network', 'useragent',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36'),
        ConfigItems('Network', 'retry', 3),
        ConfigItems('Network', 'retrywait', 5),

        ConfigItems('Filters', 'collection', True),
        ConfigItems('Filters', 'duplicate', True),

        ConfigItems('GeneralSettings', 'gallerydownloadlocation', f'.{os.sep}nhentaiDownloaded{os.sep}galleries'),
        ConfigItems('GeneralSettings', 'artistdownloadlocation', f'.{os.sep}nhentaiDownloaded{os.sep}artists'),
        ConfigItems('GeneralSettings', 'groupdownloadlocation', f'.{os.sep}nhentaiDownloaded{os.sep}groups'),
        ConfigItems('GeneralSettings', 'databaselocation', f'.{os.sep}nhentaiDownloaded'),

        ConfigItems('Filenames', 'gallerydownloadnameformat', f'%(gallery_code)s'),
        ConfigItems('Filenames', 'artistdownloadnameformat', f'%(artist_name)s{os.sep}%%(gallery_code)s'),
        ConfigItems('Filenames', 'groupdownloadnameformat', f'%(group_name)s{os.sep}%(gallery_code)s'),

        ConfigItems('DownloadSettings', 'overwrite', False)
    ]

    def __init__(self) -> None:
        for item in self.config_default:
            setattr(self, f'default_{item.option}', item.default)
        if not os.path.isfile(os.path.join(_config_file_location, 'Config.ini')):
            self.write_config()
        self.load_config()

    def write_config(self) -> None:
        config = configparser.RawConfigParser()
        groups = itertools.groupby(self.config_default, lambda x: x.section)
        for k, g in groups:
            config.add_section(k)
            for item in g:
                config.set(k, item.option, self.__getattribute__(f'default_{item.option}'))
        with open(os.path.join(_config_file_location, 'Config.ini'), 'w') as f:
            config.write(f)
    
    def load_config(self) -> None:
        config = configparser.RawConfigParser()
        config.read(os.path.join(_config_file_location, 'Config.ini'))
        for item, value in config.items():
            for i, v in value.items():
                try:
                    setattr(self, i, config.getboolean(item, i))
                except Exception:
                    try:
                        setattr(self, i, config.getint(item, i))
                    except Exception:
                        try:
                            setattr(self, i, config.getfloat(item, i))
                        except Exception:
                            setattr(self, i, v.strip())
        self.config_checker()

    def config_checker(self) -> None:
        if not isinstance(self.collection, bool):
            sys.exit('Error loading collection preferences from Config.ini, only accepted values are True or False.')
        if not isinstance(self.duplicate, bool):
            sys.exit('Error loading duplicate preferences from Config.ini, only accepted values are True or False.')
        if not isinstance(self.overwrite, bool):
            sys.exit('Error loading overwrite preferences from Config.ini, only accepted values are True or False.')

        if isinstance(self.retry, float):
            self.retry = int(self.retry)
        elif not isinstance(self.retry, int):
            sys.exit('Error loading retry preferences from Config.ini, only accepted values are int.')
        if not isinstance(self.retrywait, (float, int)):
            sys.exit('Error loading retrywait preferences from Config.ini, only accepted values are int or float.')

        self.gallerydownloadlocation = re.sub('\\\\', re.escape(os.sep), self.gallerydownloadlocation)
        self.gallerydownloadlocation = re.sub('/', re.escape(os.sep), self.gallerydownloadlocation)
        self.databaselocation = re.sub('\\\\', re.escape(os.sep), self.databaselocation)
        self.databaselocation = re.sub('/', re.escape(os.sep), self.databaselocation)
        self.gallerydownloadnameformat = re.sub('\\\\', re.escape(os.sep), self.gallerydownloadnameformat)
        self.gallerydownloadnameformat = re.sub('/', re.escape(os.sep), self.gallerydownloadnameformat)
        self.artistdownloadlocation = re.sub('\\\\', re.escape(os.sep), self.artistdownloadlocation)
        self.artistdownloadlocation = re.sub('/', re.escape(os.sep), self.artistdownloadlocation)
        self.artistdownloadnameformat = re.sub('\\\\', re.escape(os.sep), self.artistdownloadnameformat)
        self.artistdownloadnameformat = re.sub('/', re.escape(os.sep), self.artistdownloadnameformat)
        self.groupdownloadnameformat = re.sub('\\\\', re.escape(os.sep), self.groupdownloadnameformat)
        self.groupdownloadnameformat = re.sub('/', re.escape(os.sep), self.groupdownloadnameformat)

        self.default_gallerydownloadlocation = re.sub('\\\\', re.escape(os.sep), self.default_gallerydownloadlocation)
        self.default_gallerydownloadlocation = re.sub('/', re.escape(os.sep), self.default_gallerydownloadlocation)
        self.default_databaselocation = re.sub('\\\\', re.escape(os.sep), self.default_databaselocation)
        self.default_databaselocation = re.sub('/', re.escape(os.sep), self.default_databaselocation)
        self.default_gallerydownloadnameformat = re.sub('\\\\', re.escape(os.sep), self.default_gallerydownloadnameformat)
        self.default_gallerydownloadnameformat = re.sub('/', re.escape(os.sep), self.default_gallerydownloadnameformat)
        self.default_artistdownloadlocation = re.sub('\\\\', re.escape(os.sep), self.default_artistdownloadlocation)
        self.default_artistdownloadlocation = re.sub('/', re.escape(os.sep), self.default_artistdownloadlocation)
        self.default_artistdownloadnameformat = re.sub('\\\\', re.escape(os.sep), self.default_artistdownloadnameformat)
        self.default_artistdownloadnameformat = re.sub('/', re.escape(os.sep), self.default_artistdownloadnameformat)
        self.default_groupdownloadnameformat = re.sub('\\\\', re.escape(os.sep), self.default_groupdownloadnameformat)
        self.default_groupdownloadnameformat = re.sub('/', re.escape(os.sep), self.default_groupdownloadnameformat)

        if self.gallerydownloadlocation.startswith(f'.{os.sep}'):
            self.gallerydownloadlocation = os.path.join(os.path.abspath('.'), self.gallerydownloadlocation[2:])
        if self.artistdownloadlocation.startswith(f'.{os.sep}'):
            self.artistdownloadlocation = os.path.join(os.path.abspath('.'), self.artistdownloadlocation[2:])
        if self.groupdownloadlocation.startswith(f'.{os.sep}'):
            self.groupdownloadlocation = os.path.join(os.path.abspath('.'), self.groupdownloadlocation[2:])
        if self.databaselocation.startswith(f'.{os.sep}'):
            self.databaselocation = os.path.join(os.path.abspath('.'), self.databaselocation[2:])

        if self.default_gallerydownloadlocation.startswith(f'.{os.sep}'):
            self.default_gallerydownloadlocation = os.path.join(os.path.abspath('.'), self.default_gallerydownloadlocation[2:])
        if self.default_artistdownloadlocation.startswith(f'.{os.sep}'):
            self.default_artistdownloadlocation = os.path.join(os.path.abspath('.'), self.default_artistdownloadlocation[2:])
        if self.default_groupdownloadlocation.startswith(f'.{os.sep}'):
            self.default_groupdownloadlocation = os.path.join(os.path.abspath('.'), self.default_groupdownloadlocation[2:])
        if self.default_databaselocation.startswith(f'.{os.sep}'):
            self.default_databaselocation = os.path.join(os.path.abspath('.'), self.default_databaselocation[2:])

# config = Config()