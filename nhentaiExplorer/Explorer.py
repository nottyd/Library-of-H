from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

class Explorer(qtw.QWidget):
    btn_disabled_css = 'background: #772538; color: #757575;'
    btn_enabled_css = 'background-color: #ed2553; color: #fdf8ff;'

    def __init__(self):
        super().__init__()

        self.setLayout(qtw.QVBoxLayout())
        self.setFocusPolicy(qtc.Qt.NoFocus)