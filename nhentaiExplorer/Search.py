from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

from nhentaiExplorer.CustomWidgets import SearchBoxWidget


class Search(SearchBoxWidget):

    SRCH_set_filters = qtc.pyqtSignal(object, object)
    btn_disabled_css = 'background: #772538; color: #757575;'
    btn_enabled_css = 'background-color: #ed2553; color: #fdf8ff;'

    def __init__(self):
        super().__init__()
        self.search()
        self.filter_option = None
        self.search_terms = None
    def search(self):
        self.setFixedHeight(int(0.15*self.height()))
        self.setLayout(qtw.QFormLayout())
        self.returnPressed.connect(self.set_filters)
        self.search_edit = qtw.QLineEdit(objectName='EXP_LineEdit')
        self.search_edit.setEnabled(False)
        self.search_edit.setPlaceholderText('Enter search term(s)...')
        search_bar = qtw.QHBoxLayout()

        filter_options = ['artists', 'characters', 'ids', 'groups', 'parodies', 'tags', 'titles', 'collections']
        self.filter_option_combobox = qtw.QComboBox(objectName='EXP_ComboBox')
        self.filter_option_combobox.setEnabled(False)
        self.filter_option_combobox.addItems(filter_options)
        self.filter_option_combobox.setCurrentIndex(0)

        self.search_btn = qtw.QPushButton('Search', clicked=self.set_filters, objectName='EXP_PushButton')
        self.reset_btn = qtw.QPushButton('Reset', clicked=self.reset_filters, objectName='EXP_PushButton')
        self.search_btn.setEnabled(False)
        self.search_btn.setStyleSheet(self.btn_disabled_css)
        self.reset_btn.setEnabled(False)
        self.reset_btn.setStyleSheet(self.btn_disabled_css)
        search_bar.addWidget(self.filter_option_combobox)
        search_bar.addWidget(self.search_btn)
        search_bar.addWidget(self.reset_btn)
        self.layout().addRow(self.search_edit)
        self.layout().addRow(search_bar)

        # browser_groupbox = qtw.QGroupBox('Browse')
        # browser_groupbox.setLayout(qtw.QVBoxLayout())
        # self.layout().addWidget(browser_groupbox)

        # Might not need to setFocusPolicy for these: (doing to makes it unable to use tab-key to cycle through them)
        # search_edit.setFocusPolicy(qtc.Qt.ClickFocus)
        # filter_option_combobox.setFocusPolicy(qtc.Qt.ClickFocus)
        # search_btn.setFocusPolicy(qtc.Qt.ClickFocus)

    def change_search_state(self, setEnabled=False):
        self.search_edit.setEnabled(setEnabled)
        self.search_btn.setEnabled(setEnabled)
        self.reset_btn.setEnabled(setEnabled)
        self.filter_option_combobox.setEnabled(setEnabled)
        if setEnabled:
            self.search_btn.setStyleSheet(self.btn_enabled_css)
            self.reset_btn.setStyleSheet(self.btn_enabled_css)
        else:
            self.search_btn.setStyleSheet(self.btn_disabled_css)
            self.reset_btn.setStyleSheet(self.btn_disabled_css)

    def set_filters(self):
        filter_option = self.filter_option_combobox.currentText()
        search_terms = [search_term.strip().replace(' ', '-') for search_term in self.search_edit.text().split(',')]
        if search_terms == ['']:
            self.SRCH_set_filters.emit(None, None)
            return
        self.SRCH_set_filters.emit(filter_option, search_terms)

    def reset_filters(self):
        self.search_edit.setText('')
        self.SRCH_set_filters.emit(None, None)