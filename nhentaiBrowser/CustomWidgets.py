from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

class ImageScrollArea(qtw.QScrollArea):
    def __init__(self, main_window, objectName=''):
        super().__init__()
        self.objectName = objectName
        self.main_window = main_window
        self.scroll_value = self.verticalScrollBar().minimum()
        self.scroll_constant = 100

    def setObjectName(self, name):
        self.objectName = name

    def wheelEvent(self, event):
        if self.main_window.control_modifier:
            event.ignore()
        else:
            self.scroll_(event.angleDelta().y())

    def scroll_(self, y):
        if y == -120:
            if self.scroll_value + self.scroll_constant >= self.verticalScrollBar().maximum():
                self.scroll_value = self.verticalScrollBar().maximum()
            else:
                self.scroll_value += self.scroll_constant
        elif y == 120:
            if self.scroll_value - self.scroll_constant <= self.verticalScrollBar().minimum():
                self.scroll_value = self.verticalScrollBar().minimum()
            else:
                self.scroll_value -= self.scroll_constant
        self.verticalScrollBar().setValue(self.scroll_value)

class Dock(qtw.QDockWidget):
    def __init__(self, title, objectName=''):
        super().__init__()
        self.setWindowTitle(title)
        self.objectName = objectName
        self.setFocusPolicy(qtc.Qt.NoFocus)
    
    def setObjectName(self, name):
        self.objectName = name


class BrowserItemWidget(qtw.QWidget):

    BIW_viewer_change_signal = qtc.pyqtSignal(str, int)
    BIW_hover_signal = qtc.pyqtSignal(int, int)

    def __init__(self, location=None, index=None):
        super().__init__()
        self.location = location
        self.index = index
        self.selected = False
        self.setAttribute(qtc.Qt.WA_StyledBackground, True)
        self.setFocusPolicy(qtc.Qt.NoFocus)
        # self.setAttribute(qtc.Qt.WA_Hover, True)
        # self.setMouseTracking(True)
    
    def set_location(self, location):
        self.location = location

    def set_index(self, index):
        self.index = index
    
    def mousePressEvent(self, event):
        self.BIW_viewer_change_signal.emit(self.location, self.index)

    def enterEvent(self, event):
        self.BIW_hover_signal.emit(1, self.index)
    
    def leaveEvent(self, event):
        self.BIW_hover_signal.emit(0, self.index)

    def setSelected(self, selected=False):
        self.selected = selected


class SearchBoxWidget(qtw.QWidget):

    returnPressed = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()

    def keyPressEvent(self, event):
        if event.key() == qtc.Qt.Key_Return or event.key() == qtc.Qt.Key_Enter:
            self.returnPressed.emit()
