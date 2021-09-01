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
        self.change_viewer()
        self.image_label = qtw.QLabel(
            alignment=qtc.Qt.AlignCenter, objectName="MW_Label"
        )
        self.setWidget(self.image_label)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)

        self.setFocusPolicy(qtc.Qt.NoFocus)

    def image_handler(self):
        self.images = sorted(
            [
                image
                for image in os.listdir(self.location)
                if os.path.isfile(os.path.join(self.location, image))
                and not image.endswith(".csv")
            ],
            key=lambda image: int(image.split(os.extsep)[0]),
        )

    def set_viewer(self, location, image_name):
        self.location = location
        self.current_image_name = image_name
        self.image_handler()
        self.current_image_original = Image.open(
            os.path.join(self.location, self.current_image_name)
        )
        self.current_image_original = self.current_image_original.convert("RGB")
        self.current_image_qt = ImageQt.ImageQt(self.current_image_original)
        self.current_image_pixmap = qtg.QPixmap.fromImage(self.current_image_qt)
        self.image_label.setPixmap(self.current_image_pixmap)

    def change_viewer(self, location=None):
        if location == None or location == self.main_window.location:
            return
        self.location = location
        self.image_handler()
        self.current_image_name = self.images[0]
        self.current_image_original = Image.open(
            os.path.join(self.location, self.current_image_name)
        )
        self.current_image_original = self.current_image_original.convert("RGB")
        self.current_image_qt = ImageQt.ImageQt(self.current_image_original)
        self.current_image_pixmap = qtg.QPixmap.fromImage(self.current_image_qt)
        self.image_label.setPixmap(self.current_image_pixmap)

    def resize_image(self):
        self.current_image = self.current_image_original.copy()
        self.current_image_qt = ImageQt.ImageQt(self.current_image)
        self.current_image_pixmap = qtg.QPixmap.fromImage(self.current_image_qt)
        if self.resized < 0:
            self.current_image_pixmap = self.current_image_pixmap.scaled(
                int(
                    self.current_image_original.width
                    - (abs(self.resized) / 100 * self.current_image_original.width)
                ),
                int(
                    self.current_image_original.height
                    - (abs(self.resized) / 100 * self.current_image_original.height)
                ),
                qtc.Qt.KeepAspectRatio,
                qtc.Qt.SmoothTransformation,
            )
            # self.current_image_qt = ImageQt.ImageQt(self.current_image)
            # self.current_image_pixmap = qtg.QPixmap.fromImage(self.current_image_qt)
        elif self.resized > 0:
            self.current_image = self.current_image_original.copy()
            self.current_image_pixmap = self.current_image_pixmap.scaled(
                int(
                    (abs(self.resized) / 100 * self.current_image_original.width)
                    + self.current_image_original.width
                ),
                int(
                    (abs(self.resized) / 100 * self.current_image_original.height)
                    + self.current_image_original.height
                ),
                qtc.Qt.KeepAspectRatio,
                qtc.Qt.SmoothTransformation,
            )
            # self.current_image_qt = ImageQt.ImageQt(self.current_image)
            # self.current_image_pixmap = qtg.QPixmap.fromImage(self.current_image_qt)

    def change_image(self, direction):
        current_index = self.images.index(self.current_image_name)
        if direction == qtc.Qt.Key_Left:
            if current_index == 0:
                return
            self.current_image_name = self.images[current_index - 1]
            self.current_image_original = Image.open(
                os.path.join(self.location, self.current_image_name)
            )
            self.current_image_original = self.current_image_original.convert("RGB")
            self.current_image_qt = ImageQt.ImageQt(self.current_image_original)
            self.current_image_pixmap = qtg.QPixmap.fromImage(self.current_image_qt)
            if self.resized != 0:
                self.resize_image()
            self.image_label.setPixmap(self.current_image_pixmap)
            self.scroll_value = 0
            self.verticalScrollBar().setValue(self.scroll_value)
        if direction == qtc.Qt.Key_Right:
            if current_index == len(self.images) - 1:
                return
            self.current_image_name = self.images[current_index + 1]
            self.current_image_original = Image.open(
                os.path.join(self.location, self.current_image_name)
            )
            self.current_image_original = self.current_image_original.convert("RGB")
            self.current_image_qt = ImageQt.ImageQt(self.current_image_original)
            self.current_image_pixmap = qtg.QPixmap.fromImage(self.current_image_qt)
            if self.resized != 0:
                self.resize_image()
            self.image_label.setPixmap(self.current_image_pixmap)
            self.scroll_value = 0
            self.verticalScrollBar().setValue(self.scroll_value)
