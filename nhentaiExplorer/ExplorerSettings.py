import os
import itertools
from PyQt5.QtCore import QSettings

class SettingItems:
    def __init__(self, section, option, default):
        self.section = section
        self.option = option
        self.default = default


class SettingDescriptor:
    def __init__(self, name):
        self._name = name
        self.setting = QSettings(ExplorerSettings.settings_file, QSettings.IniFormat)

    def __set__(self, value):
        self.setting.setValue(self._name.replace('__', '/'), value)
        self.setting.sync()
    
    def __get__(self):
        value = self.setting.value(self._name.replace('__', '/'))
        try:
            value = eval(value)
            return value
        except:
            return value


class ExplorerSettings:

    settings_file = os.sep.join('.', "nhentaiExplorer", "ExplorerSettings.conf")

    setting_defaults = [
        SettingItems('Window', 'last_session_isMaximized', 'False'),
        SettingItems('Window', 'last_session_height', 500),
        SettingItems('Window', 'last_session_width', 720),
        SettingItems('Window', 'last_session_x', 400),
        SettingItems('Window', 'last_session_y', 400),

        SettingItems('Viewer', 'last_session_image', 'None'),
        SettingItems('Viewer', 'last_session_page', 'None'),
        # SettingItems('Viewer', 'last_session_zoom', 0),

        SettingItems('Explorer', 'last_session_database_file', 'None'),

        SettingItems('Search', 'last_session_filter_option', 'None'),
        SettingItems('Search', 'last_session_search_terms', 'None'),

        SettingItems('Browser', 'last_session_browser_page', 'None'),
        SettingItems('Browser', 'last_session_browser_selection', 'None')
    ]

    def __init__(self):
        self.setting = QSettings(ExplorerSettings.settings_file, QSettings.IniFormat)
        for item in self.setting_defaults:
            attr_name = f'{item.section}__{item.option}'
            setattr(self, attr_name, SettingDescriptor(attr_name))
        if not os.path.isfile(ExplorerSettings.settings_file):
            self.write_defaults()


    def write_defaults(self):
        groups = itertools.groupby(self.setting_defaults, lambda x: f'{x.section}/{x.option}')
        for k, g in groups:
            attr_name = k.replace('/', '__')
            for item in g:
                self.__dict__[attr_name].__set__(item.default)
            self.setting.sync()
    
    def reset_settings(self):
        self.write_defaults()

    def load_config(self):
        pass

    def config_checker(self):
        pass

if __name__ == '__main__':
    settings = ExplorerSettings()
    # settings.Window__last_session_height.__set__(600)
    # settings.Window__last_session_width.__set__(600)
    # settings.Window__last_session_x.__set__(600)
    # settings.Window__last_session_y.__set__(600)
    # print(settings.Window__last_session_x.__get__())