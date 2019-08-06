import sys
import os
import random

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from Scraper import Scraper

'''
    Code that displays Windows Screensaver images and downloads
    the ones the user requests.

    Victor Giovannoni   ICMC/USP
    github.com/vernalhav
'''

class WallpaperGUI(QDialog):

    def __init__(self):
        super().__init__()
        self.title = "Wallpaper Downloader"
        self.left = 0
        self.top = 0
        self.width = 900
        self.height = 600

        self.scraper = Scraper()

        # Labels for the image categories of bingwallpaperhd.com
        self.labels = {
            "Nature" : ["Nature", "Forest", "Mountain", "Cave", "Island", "Sea", "Coast", "River", "Lake", "Waterfall", "Sky", "Park", "Snow"],
            "Animal" : ["Animal"],
            "Plant"  : ["Plant"],
            "People" : ["People"],
            "Modern" : ["Modern", "Art", "Bridge", "Road", "Building", "Lighthouse", "Festival", "Fireworks", "Fields", "Town", "City", "History"],
            "Space"  : ["Space"],
            "Other"  : ["Other"]
        }

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, self.width, self.height)
        self.center()

        self.mainLayout = QGridLayout()
        self.topHorizontalLayout = QGridLayout()
        self.bottomHorizontalLayout = QGridLayout()

        self.mainScene = QGraphicsScene()
        self.mainImageView = QGraphicsView()
        self.pixmap = None
        self.mainImageView.setScene(self.mainScene)

        self.mainStyleDropdown = QComboBox()
        self.subStyleDropdown = QComboBox()

        self.randomBtn = QPushButton("Random")
        self.downloadBtn = QPushButton("Download")
        self.searchBtn = QPushButton("Search")

        self.searchBtn.setToolTip("Search images using these categories")
        self.downloadBtn.setToolTip("Download the current picture to the selected directory")
        self.randomBtn.setToolTip("Search a picture using random categories\n(please don't spam this, be nice to the server)")

        self.randomBtn.clicked.connect(self.randomizeSearch)
        self.searchBtn.clicked.connect(self.search)
        self.downloadBtn.clicked.connect(self.download)

        self.mainLayout.addLayout(self.topHorizontalLayout, 0, 0)
        self.mainLayout.addWidget(self.mainImageView, 1, 0)
        self.mainLayout.addLayout(self.bottomHorizontalLayout, 2, 0)

        self.bottomHorizontalLayout.addWidget(self.randomBtn, 0, 0)
        self.bottomHorizontalLayout.addWidget(self.downloadBtn, 0, 1)

        self.topHorizontalLayout.addWidget(self.mainStyleDropdown, 0, 0)
        self.topHorizontalLayout.addWidget(self.subStyleDropdown, 0, 1)
        self.topHorizontalLayout.addWidget(self.searchBtn, 0, 2)

        self.setUpDropdowns()

        self.setLayout(self.mainLayout)

        self.show()

    def closeEvent(self, event):
        self.scraper.deletePreviousImage()
        self.scraper.clearTempFolder()
        self.scraper.deleteTempFolder()
        event.accept()

    def showMessage(self, msg):
        QMessageBox.information(self, "Wallpaper Downloader", msg)

    def setUpDropdowns(self):
        self.mainStyleDropdown.addItem("Nature")
        self.mainStyleDropdown.addItem("Animal")
        self.mainStyleDropdown.addItem("Plant")
        self.mainStyleDropdown.addItem("People")
        self.mainStyleDropdown.addItem("Modern")
        self.mainStyleDropdown.addItem("Space")
        self.mainStyleDropdown.addItem("Other")

        self.mainStyleDropdown.setToolTip("Main category")
        self.subStyleDropdown.setToolTip("Secondary category")

        self.mainStyleDropdown.currentTextChanged.connect(self.updateSecondDropdown)
        self.updateSecondDropdown()

    def updateSecondDropdown(self):
        self.subStyleDropdown.clear()
        currentCategory = self.mainStyleDropdown.currentText()

        # labels map declared in the constructor method
        for label in self.labels[currentCategory]:
            self.subStyleDropdown.addItem(label)

    def updateGraphicsView(self):
        self.pixmap = QPixmap( self.scraper.getImagePath() )
        self.mainScene.addPixmap(self.pixmap)
        self.mainImageView.show()
        self.mainImageView.fitInView(self.mainScene.sceneRect(), Qt.KeepAspectRatio)

    def search(self):
        self.scraper.deletePreviousImage()

        mainCategory = self.mainStyleDropdown.currentText().lower()
        subCategory = self.subStyleDropdown.currentText().lower()

        self.scraper.search(mainCategory, subCategory)

        self.updateGraphicsView()

    def randomizeSearch(self):
        self.mainStyleDropdown.setCurrentIndex( random.randint(0, len(self.labels) - 1) )
        currentCategory = self.mainStyleDropdown.currentText()
        self.subStyleDropdown.setCurrentIndex( random.randint(0, len(self.labels[currentCategory]) - 1) )

        self.search()

    def download(self):
        status = self.scraper.download()

        if (status == "No directory chosen"):
            self.selectNewDirectory()
            self.scraper.download()

        elif (status != "Success"):
            self.showMessage(status)

    def selectNewDirectory(self):
        dirPath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.scraper.setNewDirectory(dirPath)

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

# Still not being used. Plan to do so in the near future
class ProgressBarWindow(QDialog):

    def __init__(self):
        QDialog.__init__(self)

        self.title = "Searching..."
        self.left = 0
        self.top = 0
        self.width = 300
        self.height = 100

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, self.width, self.height)

        self.progressBar = QProgressBar()
        self.progressBar.setValue(100)

        self.mainLayout = QHBoxLayout()
        self.mainLayout.addWidget(self.progressBar)
        self.setLayout(self.mainLayout)

        self.center()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())


def main():
    app = QApplication(sys.argv)
    ex = WallpaperGUI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
