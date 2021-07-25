import sys
import os
import time

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

from nhentaiExplorer.Explorer import Explorer
from nhentaiExplorer.Viewer import Viewer
from nhentaiExplorer.CustomWidgets import Dock
from nhentaiExplorer.ExplorerSettings import ExplorerSettings
from nhentaiExplorer.Search import Search
from nhentaiExplorer.Browser import Browser


class MainWindow(qtw.QMainWindow):

    MW_import_signal = qtc.pyqtSignal()

    def __init__(self):
        self.location = None
        self.control_modifier = False
        super().__init__()
        self.setWindowTitle('nhentaiExplorer')
        self.setObjectName('MainWindow')
        self.main_widget = qtw.QWidget(objectName='W_Widget')
        self.main_widget.setLayout(qtw.QVBoxLayout())
        self.main_widget.layout().setSpacing(0)
        self.setCentralWidget(self.main_widget)
        # self.setWindowFlag(qtc.Qt.FramelessWindowHint)
        self.create_main_window()
        self.menubar()
        self.set_last_session_settings()
        self.main_widget.layout().addWidget(self.menu_widget)
        self.main_widget.layout().addWidget(self.main_window)
        self.main_widget.layout().setContentsMargins(0,0,0,0)

        with open(r'.\nhentaiExplorer\stylesheet.css') as f:
            self.setStyleSheet(f.read())
            pass
        self.show()

    def set_last_session_settings(self):
        settings = ExplorerSettings()
        # Window
        if settings.Window__last_session_isMaximized.__get__():
            self.setWindowState(qtc.Qt.WindowMaximized)
        else:
            self.setGeometry(settings.Window__last_session_x.__get__(),
                        settings.Window__last_session_y.__get__(),
                        settings.Window__last_session_width.__get__(),
                        settings.Window__last_session_height.__get__())

        # Viewer
        last_session_image = settings.Viewer__last_session_image.__get__()
        if last_session_image:
            last_session_image = os.path.split(last_session_image)
            last_session_image_directory = os.path.join(*last_session_image[:-1])
            last_session_image_name = last_session_image[-1]
            self.viewer.set_viewer(last_session_image_directory, last_session_image_name)

        # Explorer
        self.database_file_location = settings.Explorer__last_session_database_file.__get__()
        if self.database_file_location:
            self.set_database_file()

        # Search
        last_session_browser_page = settings.Browser__last_session_browser_page.__get__()
        last_session_filter_option = settings.Search__last_session_filter_option.__get__()
        last_session_search_terms = settings.Search__last_session_search_terms.__get__()
        if all(item for item in [last_session_filter_option, last_session_search_terms]):
            self.search.search_edit.setText(', '.join(last_session_search_terms))
            self.search.filter_option_combobox.setCurrentText(last_session_filter_option)
            self.browser.set_filters(filter_options=last_session_filter_option, search_terms=last_session_search_terms, page_number=last_session_browser_page)
        else:
            # Browser
            if last_session_browser_page:
                self.browser.update_browser_page_number(page_number=last_session_browser_page)

        last_session_browser_selection = settings.Browser__last_session_browser_selection.__get__()
        if isinstance(last_session_browser_selection, int):
            self.browser.selection_changed(index=last_session_browser_selection)

    def menubar(self):
        self.menu_widget = qtw.QWidget(objectName='W_Widget')
        self.menu_widget.setLayout(qtw.QHBoxLayout())
        self.menu_widget.layout().setContentsMargins(0,0,0,0)
        self.menu_widget.layout().setSpacing(0)
        self.menu_widget.layout().setAlignment(qtc.Qt.AlignLeft)
        import_btn = qtw.QPushButton('Import', clicked=self.import_database, objectName='MW_PushButtons')
        explorer_btn = qtw.QPushButton('Explorer', clicked=self.show_hide_explorer, objectName='MW_PushButtons')
        import_btn.setFixedWidth(70)
        explorer_btn.setFixedWidth(70)
        self.menu_widget.layout().addWidget(import_btn)
        self.menu_widget.layout().addWidget(explorer_btn)
        import_btn.setFocusPolicy(qtc.Qt.ClickFocus)
        explorer_btn.setFocusPolicy(qtc.Qt.ClickFocus)

    def create_main_window(self):
        self.main_window = qtw.QMainWindow()
        self.explorer = Explorer()
        self.viewer = Viewer(main_window=self)
        self.create_viewer()
        self.create_explorer()

    def create_viewer(self):
        self.main_window.setCentralWidget(self.viewer)

    def create_explorer(self):
        self.create_search()
        self.create_browser()
        self.search.SRCH_set_filters.connect(self.browser.set_filters)
        self.explorer.layout().addWidget(self.search)
        self.explorer.layout().addWidget(self.browser)

        self.dock = Dock('Explorer')
        self.MW_import_signal.connect(lambda: self.search.change_search_state(True))
        self.browser.BRW_browser_item_width_signal.connect(lambda width: self.dock.setMaximumWidth(width+40))
        self.browser.BRW_viewer_change_signal.connect(self.viewer.change_viewer)
        self.dock.setTitleBarWidget(qtw.QWidget())
        self.main_window.setFocusPolicy(qtc.Qt.StrongFocus)
        self.main_window.setFocus()
        self.main_window.addDockWidget(qtc.Qt.LeftDockWidgetArea, self.dock)
        self.dock.setWidget(self.explorer)

    def create_search(self):
        self.search = Search()

    def create_browser(self):
        self.browser = Browser()

    def import_database(self):
        self.database_file_location = qtw.QFileDialog.getOpenFileName(self, 'Import database', os.path.abspath('.'), 'database files (*.db)')
        self.database_file_location = self.database_file_location[0]
        if not self.database_file_location:
            return
        else:
            self.set_database_file()

    def set_database_file(self):
        self.browser.set_database(self.database_file_location)
        self.browser.update_browser_page_number(page_number=1)
        self.browser.set_items(self.browser.get_items())
        self.MW_import_signal.emit()

    def show_hide_explorer(self):
        if self.dock.isVisible():
            self.dock.hide()
        else:
            self.dock.show()

    def keyPressEvent(self, event):
        if event.key() == qtc.Qt.Key_Left:
            self.viewer.change_image(qtc.Qt.Key_Left)
        if event.key() == qtc.Qt.Key_Right:
            self.viewer.change_image(qtc.Qt.Key_Right)
        if event.key() == qtc.Qt.Key_Up:
            self.viewer.scroll_(120)
        if event.key() == qtc.Qt.Key_Down:
            self.viewer.scroll_(-120)
        if event.key() == qtc.Qt.Key_Escape:
            if self.dock.isVisible():
                self.dock.hide()
        if event.key() == qtc.Qt.Key_Control:
            self.control_modifier = True
        if self.control_modifier:
            if event.key() == qtc.Qt.Key_E:
                self.show_hide_explorer()
    
    def keyReleaseEvent(self, event):
        if event.key() == qtc.Qt.Key_Control:
            self.control_modifier = False

    def closeEvent(self, event):
        settings = ExplorerSettings()
        # Window
        settings.Window__last_session_isMaximized.__set__(str(self.isMaximized()))
        settings.Window__last_session_height.__set__(self.height())
        settings.Window__last_session_width.__set__(self.width())
        settings.Window__last_session_x.__set__(self.x())
        settings.Window__last_session_y.__set__(self.y())

        # Explorer
        settings.Browser__last_session_browser_selection.__set__(self.browser.current_browser_items_index)
        settings.Browser__last_session_browser_page.__set__(self.browser.current_page_number)
        try:
            settings.Explorer__last_session_database_file.__set__(self.database_file_location)
        except AttributeError:
            pass
        settings.Browser__last_session_browser_page.__set__(self.browser.current_page_number)

        # Search
        settings.Search__last_session_filter_option.__set__(str(self.browser.filter_option))
        settings.Search__last_session_search_terms.__set__(str(self.browser.search_terms))

        # Viewer
        try:
            settings.Viewer__last_session_image.__set__(os.path.join(self.viewer.location, self.viewer.current_image_name))
        except AttributeError:
            pass

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
