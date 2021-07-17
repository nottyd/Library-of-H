import sys
import os
import time

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PIL import ImageQt, Image

from nhentaiExplorer.Explorer import Explorer
from nhentaiExplorer.Viewer import Viewer
from nhentaiExplorer.CustomWidgets import Dock
from nhentaiExplorer.CustomWidgets import ImageScrollArea
from nhentaiExplorer.ExplorerSettings import ExplorerSettings
class MainWindow(qtw.QMainWindow):

    resize_constant = 10
    MW_import_signal = qtc.pyqtSignal()

    def __init__(self):
        self.location = None
        self.control_modifier = False
        super().__init__()
        self.setObjectName('MainWindow')
        self.last_session_settings()
        self.main_widget = qtw.QWidget(objectName='W_Widget')
        self.main_widget.setLayout(qtw.QVBoxLayout())
        self.main_widget.layout().setSpacing(0)
        self.setCentralWidget(self.main_widget)
        # self.setWindowFlag(qtc.Qt.FramelessWindowHint)
        self.create_main_window()
        self.menubar()
        self.main_widget.layout().addWidget(self.menu_widget)
        self.main_widget.layout().addWidget(self.main_window)
        self.main_widget.layout().setContentsMargins(0,0,0,0)
        with open(r'.\nhentaiExplorer\stylesheet.css') as f:
            # print(f.read())
            self.setStyleSheet(f.read())
            pass
        self.show()

    def last_session_settings(self):
        setting = ExplorerSettings()
        if setting.Window__last_session_isMaximized.__get__():
            self.setWindowState(qtc.Qt.WindowMaximized)
        else:
            self.setGeometry(setting.Window__last_session_x.__get__(),
                        setting.Window__last_session_y.__get__(),
                        setting.Window__last_session_width.__get__(),
                        setting.Window__last_session_height.__get__())

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

    def create_explorer(self):
        self.dock = Dock('Explorer')
        self.MW_import_signal.connect(lambda: self.explorer.change_search_box_state(True))
        self.explorer.EXP_browser_item_width_signal.connect(lambda width: self.dock.setMaximumWidth(width+40))
        self.explorer.EXP_viewer_change_signal.connect(self.viewer.set_viewer)
        self.dock.setWidget(self.explorer)
        self.dock.setTitleBarWidget(qtw.QWidget())
        self.main_window.setFocusPolicy(qtc.Qt.StrongFocus)
        self.main_window.setFocus()
        self.main_window.addDockWidget(qtc.Qt.LeftDockWidgetArea, self.dock)
    
    def create_viewer(self):
        self.main_window.setCentralWidget(self.viewer)

    def import_database(self):
        file_location = qtw.QFileDialog.getOpenFileName(self, 'Import database', os.path.abspath('.'), 'database files (*.db)')
        if file_location == ('',''):
            return
        self.explorer.set_database(file_location[0])
        gallery_data_dict_list = self.explorer.get_items()
        self.explorer.update_browser_page_number(page_number=1)
        self.explorer.set_items(gallery_data_dict_list)
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
        settings.Window__last_session_isMaximized.__set__(str(self.isMaximized()))
        settings.Window__last_session_height.__set__(self.height())
        settings.Window__last_session_width.__set__(self.width())
        settings.Window__last_session_x.__set__(self.x())
        settings.Window__last_session_y.__set__(self.y())

        # settings.Explorer__last_session_browser_selection.__set__()
        settings.Explorer__last_session_browser_page.__set__(self.explorer.page_number_input.text())

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())