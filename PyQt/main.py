import sys
import time

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
import cv2
import imutils

class StitchingThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.frames = []
        self.stitching_complete = False

    def run(self):
        try:
            capture = cv2.VideoCapture(0)
            while True:
                ret, frame = capture.read()
                if ret:
                    time.sleep(1)
                    self.frames.append(frame)
                    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_image.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgb_image.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)
        except Exception as e:
            print(e)

    def stitch_images(self):
        imageStitcher = cv2.Stitcher_create() if imutils.is_cv3() else cv2.Stitcher_create()
        error, stitched_img = imageStitcher.stitch(self.frames)
        if not error:
            cv2.imwrite("stitchedOutput.png", stitched_img)


class StitchingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.stitching_thread = StitchingThread(self)
        self.stitching_thread.changePixmap.connect(self.setImage)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_capture)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_capture)
        self.stitch_button = QPushButton("Stitch")
        self.stitch_button.clicked.connect(self.stitching_thread.stitch_images)
        self.stitch_button.setEnabled(False)

        self.image_label = QLabel()
        self.image_label.setFixedSize(640, 480)

        layout = QVBoxLayout(self)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.stitch_button)
        layout.addWidget(self.image_label)
        self.setLayout(layout)

    def start_capture(self):
        self.stitching_thread.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.stitch_button.setEnabled(False)

    def stop_capture(self):
        self.stitching_thread.terminate()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.stitch_button.setEnabled(True)

    def setImage(self, image):
        self.image_label.setPixmap(QPixmap.fromImage(image))
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StitchingApp()
    window.show()
    sys.exit(app.exec_())
    