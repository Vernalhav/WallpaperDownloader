import sys
import os
import random
import re

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from requests import get
from bs4 import BeautifulSoup

'''
    Code that displays Windows Screensaver images and downloads
    the ones the user requests.

    Victor Giovannoni   ICMC/USP
    github.com/vernalhav
'''

class WallpaperGUI(QDialog):

    def __init__(self):
        super().__init__()
        self.TempFolderName = "temp"
        self.title = "Wallpaper Downloader"
        self.left = 0
        self.top = 0
        self.width = 900
        self.height = 600

        self.downloadPath = ""
        self.lastImageName = None

        self.siteDomain = "http://www.bingwallpaperhd.com"

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

        if not os.path.exists(self.TempFolderName):
            os.mkdir(self.TempFolderName)
        else:
            self.clearTempFolder()

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

        self.mainLayout = QGridLayout()

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
        self.deletePreviousImage()
        self.clearTempFolder()
        os.rmdir(self.TempFolderName)
        event.accept()

    def download(self):
        if (self.lastImageName == None):
            self.showMessage("No image selected")
            return

        if (self.downloadPath == ""):
            self.selectNewDirectory()

        # User cancelled directory select, so don't download the image
        if (self.downloadPath == ""):
            print("Download cancelled")
            return

        if (os.path.isfile( os.path.join(self.TempFolderName, self.lastImageName ))):
            os.rename( os.path.join(self.TempFolderName, self.lastImageName), os.path.join(self.downloadPath, self.lastImageName) )

    def showMessage(self, msg):
        QMessageBox.information(self, "Wallpaper Downloader", msg)

    def selectNewDirectory(self):
        dirPath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        self.downloadPath = dirPath

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
        self.pixmap = QPixmap( os.path.join(self.TempFolderName, self.lastImageName) )
        self.mainScene.addPixmap(self.pixmap)
        self.mainImageView.show()
        self.mainImageView.fitInView(self.mainScene.sceneRect(), Qt.KeepAspectRatio)

    def search(self):
        self.deletePreviousImage()

        mainCategory = self.mainStyleDropdown.currentText().lower()
        subCategory = self.subStyleDropdown.currentText().lower()

        url = self.siteDomain + "/" + mainCategory + ["/" + subCategory, ""][mainCategory == subCategory]
        response = get(url)
        if (response.status_code != 200):
            self.showMessage("Error loading page")
            return

        maxPages = self.getMaxPages(response)
        randomPage = random.randint(1, maxPages)
        imagePageUrl = url + "/page/" + str(randomPage)     # gets random image page URL

        response = get(imagePageUrl)
        if (response.status_code != 200):
            self.showMessage("Error loading page")
            return

        imageUrl = self.getRandomImageURL(response)
        imageName = re.sub(r".*/", "", imageUrl)   # removes the rest of the url

        with open(os.path.join(self.TempFolderName, imageName), "wb") as f:
            f.write(get(imageUrl).content)
            self.lastImageName = imageName
            self.updateGraphicsView()

    def deletePreviousImage(self):
        if (self.lastImageName == None):
            return

        if (os.path.isfile( os.path.join(self.TempFolderName, self.lastImageName ))):
            os.remove(os.path.join(self.TempFolderName, self.lastImageName))

    def getRandomImageURL(self, response):
        ''' Returns the URL of a random image in the page '''
        soup = BeautifulSoup(response.text, "html.parser")
        container = soup.find_all("div", class_ = "grid_8 post")[0]
        imageDivs = container.find_all("div", class_ = "view view-first")

        imageNumber = random.randint(0, len(imageDivs) - 1)
        smallImageLink = imageDivs[imageNumber].a.img.attrs["src"]

        # removes the dimensions of the small icon, linking to the original image
        return re.sub(r"-\d*x\d*\.", ".", smallImageLink)

    def getMaxPages(self, response):
        ''' Returns the number of pages with results from the specified categories '''
        soup = BeautifulSoup(response.text, "html.parser")
        container = soup.find_all("div", class_ = "wp-pagenavi")[0]    # since there is only one page nav, we get the first (and only) result

        maxPages = int(container.find_all("a")[-2].text)
        return maxPages

    def randomizeSearch(self):
        self.mainStyleDropdown.setCurrentIndex( random.randint(0, len(self.labels) - 1) )

        currentCategory = self.mainStyleDropdown.currentText()

        self.subStyleDropdown.setCurrentIndex( random.randint(0, len(self.labels[currentCategory]) - 1) )
        self.search()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def clearTempFolder(self):
        for fileName in os.listdir(os.path.join(self.TempFolderName)):
            fileName = os.path.join(self.TempFolderName, fileName)
            if (os.path.isfile(fileName)):
                os.remove(fileName)
            elif (os.path.isdir(fileName)):
                os.rmdir(fileName)
            else:
                print("Please delete contents of temp folder")


def main():
    app = QApplication(sys.argv)
    ex = WallpaperGUI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
