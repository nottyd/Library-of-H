import os

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PIL import ImageQt, Image

from nhentaiDownloader.nhentaiDBManager import nhentaiDBBrowser
from nhentaiExplorer.CustomWidgets import BrowserItemWidget, SearchBoxWidget

class Explorer(qtw.QWidget):

    EXP_viewer_change_signal = qtc.pyqtSignal(str)
    EXP_browser_item_width_signal = qtc.pyqtSignal(int)
    btn_disabled_css = 'background: #772538; color: #757575;'
    btn_enabled_css = 'background-color: #ed2553; color: #fdf8ff;'

    def __init__(self):
        super().__init__()
        self.limit = 7
        self.offset = 0
        self.max_page_numbers = 0
        self.curr_page_number = 0
        self.filter_option = None
        self.search_terms = None

        self.setLayout(qtw.QVBoxLayout())
        self.search()
        self.browser()
        self.layout().addWidget(self.search_box)
        self.layout().addWidget(self.browser_groupbox)

        self.setFocusPolicy(qtc.Qt.NoFocus)

    def search(self):
        self.search_box = SearchBoxWidget()
        self.search_box.setFixedHeight(int(0.15*self.height()))
        self.search_box.setLayout(qtw.QFormLayout())
        self.search_box.returnPressed.connect(self.set_filters)
        self.search_edit = qtw.QLineEdit(objectName='EXP_LineEdit')
        self.search_edit.setEnabled(False)
        self.search_edit.setPlaceholderText('Enter search term(s)...')
        search_bar = qtw.QHBoxLayout()

        filter_options = ['artists', 'characters', 'ids', 'groups', 'parodies', 'tags', 'titles', 'collections', 'custom...']
        self.filter_option_combobox = qtw.QComboBox(objectName='EXP_ComboBox')
        self.filter_option_combobox.setEnabled(False)
        self.filter_option_combobox.addItems(filter_options)
        self.filter_option_combobox.setCurrentIndex(0)
        self.filter_option_combobox.currentTextChanged.connect(self.custom_filters)

        self.search_btn = qtw.QPushButton('Search', clicked=self.set_filters, objectName='EXP_PushButton')
        self.search_btn.setEnabled(False)
        self.search_btn.setStyleSheet(self.btn_disabled_css)
        search_bar.addWidget(self.filter_option_combobox)
        search_bar.addWidget(self.search_btn)
        self.search_box.layout().addRow(self.search_edit)
        self.search_box.layout().addRow(search_bar)

        # browser_groupbox = qtw.QGroupBox('Browse')
        # browser_groupbox.setLayout(qtw.QVBoxLayout())
        # self.layout().addWidget(browser_groupbox)

        # Might not need to setFocusPolicy for these: (doing to makes it unable to use tab-key to cycle through them)
        # search_edit.setFocusPolicy(qtc.Qt.ClickFocus)
        # filter_option_combobox.setFocusPolicy(qtc.Qt.ClickFocus)
        # search_btn.setFocusPolicy(qtc.Qt.ClickFocus)

    def browser(self):
        self.browser_pages()
        self.browser_pages_widget.setStyleSheet('#browser_pages_widget {border-top: 1px solid white}')
        self.browser_scrollarea = qtw.QScrollArea(objectName='browser_scrollbar')
        # self.browser_scrollarea.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOn)
        # self.browser_scrollarea.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOn)
        self.browser_scrollarea.setFocusPolicy(qtc.Qt.NoFocus)
        browser_horizontal_scrollbar = qtw.QScrollBar(objectName='browser_scrollbar_horizontal')
        browser_vertical_scrollbar = qtw.QScrollBar(objectName='browser_scrollbar_vertical')
        self.browser_scrollarea.setVerticalScrollBar(browser_vertical_scrollbar)
        self.browser_scrollarea.setHorizontalScrollBar(browser_horizontal_scrollbar)

        self.browser_groupbox = qtw.QGroupBox()
        self.browser_groupbox.setLayout(qtw.QVBoxLayout())
        self.browser_groupbox.layout().setContentsMargins(0,0,0,0)
        self.browser_groupbox.layout().addWidget(self.browser_scrollarea)
        self.browser_groupbox.layout().addWidget(self.browser_pages_widget)

    def browser_pages(self):
        def check_int():
            text = self.page_number_input.text()
            try:
                int(text[-1])
            except:
                self.page_number_input.setText(text[:-1])

        self.browser_pages_widget = qtw.QWidget(objectName='browser_pages_widget')
        self.browser_pages_widget.setLayout(qtw.QHBoxLayout())
        self.browser_pages_widget.setFocusPolicy(qtc.Qt.NoFocus)
        self.left_btn = qtw.QPushButton('<', clicked=lambda: self.prev_next_btn_clicked(mode='<'), objectName='EXP_PushButton')
        self.right_btn = qtw.QPushButton('>', clicked=lambda: self.prev_next_btn_clicked(mode='>'), objectName='EXP_PushButton')
        self.first_btn = qtw.QPushButton('<<', clicked=lambda: self.prev_next_btn_clicked(mode='<<'), objectName='EXP_PushButton')
        self.last_btn = qtw.QPushButton('>>', clicked=lambda: self.prev_next_btn_clicked(mode='>>'), objectName='EXP_PushButton')
        self.change_btn_state(False, False, False, False)
        self.page_number_input = qtw.QLineEdit('0', alignment=qtc.Qt.AlignCenter, objectName='EXP_LineEdit')
        self.page_number_input.setEnabled(False)
        self.page_number_input.returnPressed.connect(lambda: self.update_browser_page_number(mode='returnPressed'))
        self.page_number_input.textChanged.connect(check_int)
        self.page_number_label = qtw.QLabel(f'/ {self.max_page_numbers}', alignment=qtc.Qt.AlignCenter)
        self.page_number_label.setStyleSheet('background: #1f1f1f;')
        self.browser_pages_widget.layout().addWidget(self.first_btn)
        self.browser_pages_widget.layout().addWidget(self.left_btn)
        self.browser_pages_widget.layout().addWidget(self.page_number_input)
        self.browser_pages_widget.layout().addWidget(self.page_number_label)
        self.browser_pages_widget.layout().addWidget(self.right_btn)
        self.browser_pages_widget.layout().addWidget(self.last_btn)

    def get_items(self, mode=None):
        temp = self.nhen_DBB.sqlite_select(get='rowid', order_by='ids', order_in='ASC', table='nhentaiLibrary', filter_option=self.filter_option, search_terms=self.search_terms)
        results = self.nhen_DBB.sqlite_select(get='*', order_by='ids', order_in='ASC', table='nhentaiLibrary', filter_option=self.filter_option, search_terms=self.search_terms, limit=self.limit, offset=self.offset)
        self.max_page_numbers = len(temp)/self.limit
        del temp
        if isinstance(self.max_page_numbers, float):
            if int(self.max_page_numbers) != self.max_page_numbers:
                self.max_page_numbers = int(self.max_page_numbers) + 1
        self.max_page_numbers = int(self.max_page_numbers)
        self.page_number_label.setText(f'/ {self.max_page_numbers}')
        self.update_browser_page_number()
        gallery_data_dict_list = [{
            'id' : result[0],
            'title' : result[1],
            'artist' : result[2],
            'group' : result[3],
            'parodies' : result[4],
            'characters' : result[5],
            'language' : result[6],
            'categories' : result[7],
            'pages' : result[8],
            'upload_date' : result[9],
            'tags' : result[10],
            'location' : result[11]
        } for result in results]
        return gallery_data_dict_list

    def set_items(self, gallery_data_dict_list):
        self.browser_widget = qtw.QWidget()
        self.browser_widget.setFocusPolicy(qtc.Qt.NoFocus)
        self.browser_widget.setStyleSheet('background: #1f1f1f')
        self.browser_widget.setLayout(qtw.QVBoxLayout())
        self.browser_widget.layout().setSpacing(0)
        self.browser_widget.layout().setContentsMargins(0,0,0,0)
        self.browser_items = [BrowserItemWidget() for i in range(len(gallery_data_dict_list))]
        for index, gallery_data_dict in enumerate(gallery_data_dict_list):
            browser_item = self.browser_items[index]
            browser_item.setMinimumHeight(240)
            location = gallery_data_dict['location']
            browser_item.set_location(location=location)
            browser_item.set_index(index=index)
            browser_item.BIW_viewer_change_signal.connect(self.selection_changed)
            browser_item.setLayout(qtw.QHBoxLayout())
            browser_item.BIW_hover_signal.connect(lambda mode, index: self.hover_event(mode, index))
            browser_item.setStyleSheet('background: #1f1f1f')
            description = qtw.QScrollArea()
            description.verticalScrollBar().hide()
            description.horizontalScrollBar().hide()
            description.setFocusPolicy(qtc.Qt.NoFocus)
            self.create_metadata(gallery_data_dict)
            # text = qtw.QLabel(self.create_metadata(gallery_data_dict))
            description.setWidget(self.metadata_widget)
            thumbnail = Image.open(os.path.join(location, sorted(os.listdir(location))[0]))
            thumbnail = thumbnail.convert('RGB')
            # thumbnail.thumbnail((250,250), Image.BOX)
            thumbnail = ImageQt.ImageQt(thumbnail)
            thumbnail_pixmap = qtg.QPixmap.fromImage(thumbnail)
            thumbnail_pixmap = thumbnail_pixmap.scaled(150, 200, qtc.Qt.KeepAspectRatio, qtc.Qt.SmoothTransformation)
            thumb = qtw.QLabel(pixmap=thumbnail_pixmap)
            # text.setFixedWidth(int(browser_scrollarea.width()*50/100))
            browser_item.layout().addWidget(thumb)
            browser_item.layout().addWidget(description)
            self.browser_widget.layout().addWidget(browser_item)
            index += 1
        self.EXP_browser_item_width_signal.emit(browser_item.width())
        self.browser_scrollarea.setWidget(self.browser_widget)

    def selection_changed(self, location, index):
        for item in self.browser_items:
            item.setStyleSheet('background: #1f1f1f;')
            item.setSelected(False)
            item.layout().itemAt(1).widget().verticalScrollBar().hide()
            item.layout().itemAt(1).widget().horizontalScrollBar().hide()
        self.browser_items[index].setStyleSheet('background: #363636;')
        self.browser_items[index].setSelected(True)
        self.browser_items[index].layout().itemAt(1).widget().verticalScrollBar().show()
        self.browser_items[index].layout().itemAt(1).widget().horizontalScrollBar().show()
        self.EXP_viewer_change_signal.emit(location)

    def set_database(self, location):
        self.offset = 0
        self.database_location = location
        self.nhen_DBB = nhentaiDBBrowser()
        self.nhen_DBB.set_database(database_location=self.database_location)

    def create_metadata(self, gallery_data_dict):
        self.metadata_widget = qtw.QWidget()
        self.metadata_widget.setLayout(qtw.QFormLayout())
        # self.metadata_widget.layout().setSpacing(0)
        self.metadata_widget.layout().setContentsMargins(10, 0, 0, 10)
        title_id = qtw.QLabel(f"{gallery_data_dict['title']} ({gallery_data_dict['id']})")
        title_id.setStyleSheet('font-weight: bold; font-size: 20px')
        artist = qtw.QLabel(f"{gallery_data_dict['artist']}")
        group = qtw.QLabel(f"{gallery_data_dict['group']}")
        parodies = qtw.QLabel(f"{gallery_data_dict['parodies']}")
        characters = qtw.QLabel(f"{gallery_data_dict['characters']}")
        language = qtw.QLabel(f"{gallery_data_dict['language']}")
        pages = qtw.QLabel(f"{gallery_data_dict['pages']}")
        upload_date = qtw.QLabel(f"{gallery_data_dict['upload_date']}")
        tags = qtw.QLabel(f"{gallery_data_dict['tags']}")
        location = qtw.QLabel(f"{gallery_data_dict['location']}")
        description = qtw.QLabel(f'{gallery_data_dict["artist"]}')
        self.metadata_widget.layout().addRow(title_id)
        self.metadata_widget.layout().addRow('Artist: ', artist)
        self.metadata_widget.layout().addRow('Group: ', group)
        self.metadata_widget.layout().addRow('Parodies: ', parodies)
        self.metadata_widget.layout().addRow('Characters: ', characters)
        self.metadata_widget.layout().addRow('Language: ', language)
        self.metadata_widget.layout().addRow('Pages: ', pages)
        self.metadata_widget.layout().addRow('Upload date: ', upload_date)
        self.metadata_widget.layout().addRow('Tags: ', tags)
        self.metadata_widget.layout().addRow('Location: ', location)
#         metadata = f"""Title: {gallery_data_dict['title']} ({gallery_data_dict['id']})
# Artist: {gallery_data_dict['artist']}
# Group: {gallery_data_dict['group']}
# Parodies: {gallery_data_dict['parodies']}
# Characters: {gallery_data_dict['characters']}
# Language: {gallery_data_dict['language']}
# Categories: {gallery_data_dict['categories']}
# Pages: {gallery_data_dict['pages']}
# Upload date: {gallery_data_dict['upload_date']}
# Tags: {gallery_data_dict['tags']}
# Location: {gallery_data_dict['location']}
# Description: None"""
        # return metadata

    def prev_next_btn_clicked(self, mode):
        if mode == '<':
            if self.curr_page_number-1 <= 0:
                return
            self.curr_page_number-=1
        if mode == '>':
            if self.curr_page_number+1 > self.max_page_numbers:
                return
            self.curr_page_number+=1
        if mode == '<<':
            self.curr_page_number = 1
        if mode == '>>':
            self.curr_page_number = self.max_page_numbers
        self.change_offset()
        gallery_data_dict_list = self.get_items()
        self.set_items(gallery_data_dict_list)
        self.update_browser_page_number()

    def change_btn_state(self, first=False, left=False, right=False, last=False):
        self.first_btn.setEnabled(first)
        self.left_btn.setEnabled(left)
        self.right_btn.setEnabled(right)
        self.last_btn.setEnabled(last)
        if not first:
            self.first_btn.setStyleSheet(self.btn_disabled_css)
        elif first:
            self.first_btn.setStyleSheet(self.btn_enabled_css)
        if not left:
            self.left_btn.setStyleSheet(self.btn_disabled_css)
        elif left:
            self.left_btn.setStyleSheet(self.btn_enabled_css)
        if not right:
            self.right_btn.setStyleSheet(self.btn_disabled_css)
        elif right:
            self.right_btn.setStyleSheet(self.btn_enabled_css)
        if not last:
            self.last_btn.setStyleSheet(self.btn_disabled_css)
        elif last:
            self.last_btn.setStyleSheet(self.btn_enabled_css)

    def change_search_box_state(self, setEnabled=False):
        self.search_edit.setEnabled(setEnabled)
        self.search_btn.setEnabled(setEnabled)
        self.filter_option_combobox.setEnabled(setEnabled)
        if setEnabled:
            self.search_btn.setStyleSheet(self.btn_enabled_css)
        else:
            self.search_btn.setStyleSheet(self.btn_disabled_css)

    def update_browser_page_number(self, page_number=None, mode=None):
        if page_number != None:
            self.curr_page_number = page_number
            self.change_offset()
            gallery_data_dict_list = self.get_items()
            self.set_items(gallery_data_dict_list)
            self.page_number_input.setText(str(self.curr_page_number))
            self.page_number_label.setText(f'/ {self.max_page_numbers}')
        page_number = int(self.page_number_input.text())
        if mode == 'returnPressed':
            if page_number <= self.max_page_numbers and page_number > 0:
                self.curr_page_number = page_number
                self.change_offset()
                gallery_data_dict_list = self.get_items()
                self.set_items(gallery_data_dict_list)
        self.page_number_input.setText(str(self.curr_page_number))

    def change_offset(self):
        self.offset = (self.curr_page_number-1) * self.limit

    def custom_filters(self, value):
        if value == 'custom...':
            pass

    def set_filters(self):
        self.filter_option = self.filter_option_combobox.currentText()
        self.search_terms = [search_term.strip().replace(' ', '-') for search_term in self.search_edit.text().split(',')]
        if self.search_terms == '':
            self.filter_option=None
            self.search_terms=None
        self.update_browser_page_number(page_number=1)
        # self.set_database()
        gallery_data_dict_list = self.get_items()
        self.set_items(gallery_data_dict_list)

    def paintEvent(self, event):
        if self.curr_page_number-1 <= 0:
            self.change_btn_state(False, False, True, True)
        if self.curr_page_number+1 > self.max_page_numbers:
            self.change_btn_state(True, True, False, False)
        if self.curr_page_number-1 <= 0 and self.curr_page_number+1 > self.max_page_numbers:
            self.change_btn_state(False, False, False, False)
        if not self.curr_page_number-1 <= 0 and not self.curr_page_number+1 > self.max_page_numbers:
            self.change_btn_state(True, True, True, True)

    def hover_event(self, mode, index):
        if self.browser_items[index].selected == True:
            return
        if mode == 1:
            self.browser_items[index].setStyleSheet('background: #363636;')
            self.browser_items[index].layout().itemAt(1).widget().verticalScrollBar().show()
            self.browser_items[index].layout().itemAt(1).widget().horizontalScrollBar().show()
        if mode == 0:
            self.browser_items[index].setStyleSheet('background: #1f1f1f;')
            self.browser_items[index].layout().itemAt(1).widget().verticalScrollBar().hide()
            self.browser_items[index].layout().itemAt(1).widget().horizontalScrollBar().hide()
