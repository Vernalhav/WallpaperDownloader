import random
import re
import sys
import os

from requests import get
from bs4 import BeautifulSoup

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread

# Perhaps not all of these funcions should be in this class,
# such as the directory-altering ones. Might refactor later
class Scraper(QThread):

    updateSignal = pyqtSignal(int, name="updateProgBar")
    doneSignal = pyqtSignal(name="finished")

    def __init__(self, gui):
        super().__init__()

        self.downloadPath = ""
        self.lastImageName = None
        self.TempFolderName = "temp"

        self.siteDomain = "http://www.bingwallpaperhd.com"

        self.gui = gui
        self.updateSignal.connect(self.gui.update)
        self.doneSignal.connect(self.gui.updateGraphicsView)

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

        self.mainCategory = ""
        self.subCategory = ""

        if not os.path.exists(self.TempFolderName):
            os.mkdir(self.TempFolderName)
        else:
            self.clearTempFolder()

    def download(self):
        if (self.lastImageName == None):
            return "No image selected"

        if (self.downloadPath == ""):
            return "No directory chosen"

        # User cancelled directory select, so don't download the image
        if (self.downloadPath == ""):
            return "Download cancelled"

        if (os.path.isfile( os.path.join(self.TempFolderName, self.lastImageName ))):
            os.rename( os.path.join(self.TempFolderName, self.lastImageName), os.path.join(self.downloadPath, self.lastImageName) )
            return "Success"

        return "Image changed directory"

    def setNewDirectory(self, dirPath):
        self.downloadPath = dirPath

    def getImagePath(self):
        return os.path.join(self.TempFolderName, self.lastImageName)

    def setUpSearch(self, mainCategory, subCategory):
        self.mainCategory = mainCategory
        self.subCategory = subCategory

    def search(self):
        self.updateSignal.emit(0)

        url = self.siteDomain + "/" + self.mainCategory + ["/" + self.subCategory, ""][self.mainCategory == self.subCategory]
        response = get(url)
        if (response.status_code != 200):
            self.showMessage("Error loading page")
            return

        self.updateSignal.emit(33)

        maxPages = self.getMaxPages(response)
        randomPage = random.randint(1, maxPages)
        imagePageUrl = url + "/page/" + str(randomPage)     # gets random image page URL

        response = get(imagePageUrl)
        if (response.status_code != 200):
            self.showMessage("Error loading page")
            return

        self.updateSignal.emit(66)

        imageUrl = self.getRandomImageURL(response)
        imageName = re.sub(r".*/", "", imageUrl)   # removes the rest of the url

        with open(os.path.join(self.TempFolderName, imageName), "wb") as f:
            f.write(get(imageUrl).content)
            self.lastImageName = imageName

        self.updateSignal.emit(100)
        self.doneSignal.emit()

    def run(self):
        self.search()
        return

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

    def clearTempFolder(self):
        for fileName in os.listdir(os.path.join(self.TempFolderName)):
            fileName = os.path.join(self.TempFolderName, fileName)
            if (os.path.isfile(fileName)):
                os.remove(fileName)
            elif (os.path.isdir(fileName)):
                os.rmdir(fileName)
            else:
                print("Please delete contents of temp folder")

    def deleteTempFolder(self):
        os.rmdir(self.TempFolderName)
