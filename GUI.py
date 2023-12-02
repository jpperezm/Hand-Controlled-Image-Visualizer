from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QDir

class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def dragImage(self, newPos):
        if self.hasPhoto():
            self._photo.setPos(self._photo.pos() + newPos)

    def changeZoom(self, delta):
        if self.hasPhoto():
            if delta < -4 or delta > 0:
                if delta > 0:
                    factor = 1.25
                    self._zoom += 1
                else:
                    factor = 0.8
                    self._zoom -= 1
                
                if self._zoom > 0:
                    self.scale(factor, factor)
                elif self._zoom == 0:
                    self.fitInView()
                else:
                    self._zoom = 0

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
        super(PhotoViewer, self).mousePressEvent(event)


class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.viewer = PhotoViewer(self)
        # 'Load images' button
        self.btnLoad = QtWidgets.QToolButton(self)
        self.btnLoad.setText('Load images')
        self.btnLoad.clicked.connect(self.loadImages)

        # 'Next' button
        self.btnNext = QtWidgets.QToolButton(self)
        self.btnNext.setText('Next')
        self.btnNext.clicked.connect(self.showNextImage)

        # 'Previous' button
        self.btnPrev = QtWidgets.QToolButton(self)
        self.btnPrev.setText('Previous')
        self.btnPrev.clicked.connect(self.showPreviousImage)

        # Arrange layout
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.addWidget(self.viewer)
        HBlayout = QtWidgets.QHBoxLayout()
        HBlayout.setAlignment(QtCore.Qt.AlignLeft)
        HBlayout.addWidget(self.btnLoad)
        HBlayout.addWidget(self.btnPrev)
        HBlayout.addWidget(self.btnNext)

        VBlayout.addLayout(HBlayout)

        self.imageList = []
        self.currentImageIndex = 0

    def loadImages(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        folder_path = QFileDialog.getExistingDirectory(self, "Select a folder with images", options=options)
        if folder_path:
            image_files = QDir(folder_path).entryList(['*.png', '*.xpm', '*.jpg', '*.bmp', '*.gif'], QDir.Files)
            if image_files:
                self.imageList = [folder_path + '/' + file for file in image_files]
                self.currentImageIndex = 0
                self.viewer.setPhoto(QtGui.QPixmap(self.imageList[self.currentImageIndex]))

    def showNextImage(self):
        if self.imageList and len(self.imageList) > 1:
            self.currentImageIndex = (self.currentImageIndex + 1) % len(self.imageList)
            self.viewer.setPhoto(QtGui.QPixmap(self.imageList[self.currentImageIndex]))

    def showPreviousImage(self):
        if self.imageList and len(self.imageList) > 1:
            self.currentImageIndex = (self.currentImageIndex - 1) % len(self.imageList)
            self.viewer.setPhoto(QtGui.QPixmap(self.imageList[self.currentImageIndex]))

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setGeometry(500, 300, 800, 600)
    window.show()
    sys.exit(app.exec_())

