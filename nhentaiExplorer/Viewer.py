import os

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PIL import ImageQt, Image

from nhentaiExplorer.CustomWidgets import ImageScrollArea

class Viewer(ImageScrollArea):
    def __init__(self, main_window):
        self.resized = 0
        super().__init__()
        self.set_main_window(main_window)
        self.set_viewer()
        self.image_label = qtw.QLabel(alignment=qtc.Qt.AlignCenter, objectName='MW_Label')
        self.setWidget(self.image_label)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)

        self.setFocusPolicy(qtc.Qt.NoFocus)

    def image_handler(self):
        self.images = sorted([image for image in os.listdir(self.location) if os.path.isfile(os.path.join(self.location, image)) and not image.endswith('.csv')],
         key=lambda image: int(image.split(os.extsep)[0]))

    def set_viewer(self, location=None):
        if location == None or location == self.main_window.location:
            return
        self.location = location
        self.image_handler()
        self.curr_img_name = self.images[0]
        self.curr_img_org = Image.open(os.path.join(location, self.curr_img_name))
        self.curr_img_org = self.curr_img_org.convert('RGB')
        self.curr_img_qt = ImageQt.ImageQt(self.curr_img_org)
        self.curr_img_pixmap = qtg.QPixmap.fromImage(self.curr_img_qt)
        self.image_label.setPixmap(self.curr_img_pixmap)

    def resize_image(self):
        self.curr_img = self.curr_img_org.copy()
        self.curr_img_qt = ImageQt.ImageQt(self.curr_img)
        self.curr_img_pixmap = qtg.QPixmap.fromImage(self.curr_img_qt)
        if self.resized < 0:
            self.curr_img_pixmap = self.curr_img_pixmap.scaled(
                int(self.curr_img_org.width - (abs(self.resized)/100 * self.curr_img_org.width))
                , int(self.curr_img_org.height - (abs(self.resized)/100 * self.curr_img_org.height))
                , qtc.Qt.KeepAspectRatio, qtc.Qt.SmoothTransformation)
            # self.curr_img_qt = ImageQt.ImageQt(self.curr_img)
            # self.curr_img_pixmap = qtg.QPixmap.fromImage(self.curr_img_qt)
        elif self.resized > 0:
            self.curr_img = self.curr_img_org.copy()
            self.curr_img_pixmap = self.curr_img_pixmap.scaled(
                int((abs(self.resized)/100 * self.curr_img_org.width) + self.curr_img_org.width)
                , int((abs(self.resized)/100 * self.curr_img_org.height) + self.curr_img_org.height)
                , qtc.Qt.KeepAspectRatio, qtc.Qt.SmoothTransformation)
            # self.curr_img_qt = ImageQt.ImageQt(self.curr_img)
            # self.curr_img_pixmap = qtg.QPixmap.fromImage(self.curr_img_qt)

    def change_image(self, direction):
        current_index = self.images.index(self.curr_img_name)
        if direction == qtc.Qt.Key_Left:
            if current_index == 0:
                return
            self.curr_img_name = self.images[current_index-1]
            self.curr_img_org = Image.open(os.path.join(self.location, self.curr_img_name))
            self.curr_img_org = self.curr_img_org.convert('RGB')
            self.curr_img_qt = ImageQt.ImageQt(self.curr_img_org)
            self.curr_img_pixmap = qtg.QPixmap.fromImage(self.curr_img_qt)
            if self.resized != 0:
                self.resize_image()
            self.image_label.setPixmap(self.curr_img_pixmap)
            self.scroll_value = 0
            self.verticalScrollBar().setValue(self.scroll_value)
        if direction == qtc.Qt.Key_Right:
            if current_index == len(self.images)-1:
                return
            self.curr_img_name = self.images[current_index+1]
            self.curr_img_org = Image.open(os.path.join(self.location, self.curr_img_name))
            self.curr_img_org = self.curr_img_org.convert('RGB')
            self.curr_img_qt = ImageQt.ImageQt(self.curr_img_org)
            self.curr_img_pixmap = qtg.QPixmap.fromImage(self.curr_img_qt)
            if self.resized != 0:
                self.resize_image()
            self.image_label.setPixmap(self.curr_img_pixmap)
            self.scroll_value = 0
            self.verticalScrollBar().setValue(self.scroll_value)