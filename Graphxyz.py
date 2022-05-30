"""
Created on Wed Nov 25 17:37:03 2020

@author: d. seyitliyev
"""
#from funs_fit import *
import numpy as np
import sys
import pathlib
import platform
import csv
import pickle
import ast
from PyQt5.QtWidgets import QShortcut,QAction,QSpacerItem, QAbstractItemView, QGraphicsOpacityEffect, QDesktopWidget, QWidget, QActionGroup, QMainWindow, QMenu, QMenuBar, QTableView, QMessageBox, QDialog, QApplication,QFileDialog, QPushButton, QSlider, QFrame, QLabel, QLineEdit, QCheckBox, QComboBox, QListWidget, QRadioButton, QTabWidget, QListView,QAbstractItemView,QTreeView, QColorDialog, QListWidgetItem
from PyQt5 import QtWidgets
import matplotlib
import pandas as pd
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, uic
from PyQt5.QtCore import QEasingCurve, pyqtSignal, QMimeData, QUrl, Qt, QAbstractTableModel, QPoint, QObject, QSettings, QTimer,QPropertyAnimation
from PyQt5.QtGui import QFont, QColor, QScreen, QPixmap, QIcon, QKeySequence
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
import matplotlib.backends.backend_svg
from matplotlib.figure import Figure
import matplotlib.cm as cm
import os #Used in Testing Script
import time
import matplotlib.pyplot as plt
import matplotlib.colors as clrs
import matplotlib.legend as lgd
from datetime import datetime
from numpy import exp #Wil be used during user function input
from numpy import log #Wil be used during user function input
from numpy import cos #Wil be used during user function input
from numpy import sin #Wil be used during user function input
from numpy import tan #Wil be used during user function input
from numpy import mod
from numpy import linspace
from scipy.optimize import curve_fit
import math
import requests # Used when app version is checked and to check if new version is available
from inspect import getmembers, isfunction #This is used to get the list of the functions inside python module
import importlib.util #This helps to import external python files
import sys
#import resources for windows this resources function needed to be defined in a file, could not find a way to import local modules

# Run these to build for each platforms (cd to src folder)
# Note: File icon can be added using --icon=icon.icns for mac, icon.png for linux and icon.png for windows

# For Windows:
# pyinstaller --onefile --windowed --add-data "uis/*.ui;uis" --add-data "prs/*.txt;prs" --add-data "icns/*.png;icns" --add-data "funs/*.py;funs" --add-data "funs/*.txt;funs" Graphxyz.py
# pyinstaller --noconsole --add-data "uis/*.ui;uis" --add-data "prs/*.txt;prs" --add-data "icns/*.png;icns" --add-data "funs/*.py;funs" --add-data "funs/*.txt;funs" Graphxyz.py

# For Mac:
# /opt/homebrew/bin/python3 -m PyInstaller --onefile --windowed --add-data "uis/*.ui:uis" --add-data "prs/*.txt:prs" --add-data "icns/*.png:icns" --add-data "funs/*.py:funs" --add-data "funs/*.txt:funs" Graphxyz.py

# exception shortcut:
# except Exception as Argument:
#     self.genLogforException(Argument)

#This is the way to import external python functions to fit:
# import importlib.util
# import sys
# spec = importlib.util.spec_from_file_location("customPyFuns", "/Users/seyitliyev/Documents/Graphxyz/Python functions/funs_fit.py")
# pyFuns = importlib.util.module_from_spec(spec)
# sys.modules["customPyFuns"] = pyFuns
# spec.loader.exec_module(pyFuns)
# print(''.join([getmembers(pyFuns, isfunction)[0][0],'(x,p)']))
# pyFuns.testfun()

appVersion = '0.5'
appVersionText = ''.join(['Version ',appVersion])


response = requests.get("https://api.github.com/repos/dseyit/Graphxyz/releases/latest")
latestVersion = response.json()["name"]

def getResourcePath(relative_path):
    rel_path = pathlib.Path(relative_path)
    dev_base_path = pathlib.Path(__file__).resolve().parent
    base_path = getattr(sys,"_MEIPASS",dev_base_path)
    return base_path / rel_path

class AppWindow(QDialog):
    screenSizeChanged = QtCore.pyqtSignal(QtCore.QRect)
    def __init__(self, app):
        super().__init__()
        self.exceptionLogLocation = self.makeFolderinDocuments('.logs')
        DataDir = getResourcePath("uis")
        icnDir = getResourcePath("icns")
        uiPath = DataDir / 'graphxyz.ui'
        self.ui = uic.loadUi(uiPath,self)
        self.app = app
        self.currWindowSize = self.app.desktop().geometry()
        
        self.ui.plotLimits.setMaximumWidth(int(self.currWindowSize.width()*0.10)) #this is fix for high res displays for plotlimits
        
        # This will add menubar to each tab of the application
        self.mbar = self.menuAdder()
        #self.mbar.setObjectName("tabMenuBar")
        self.mbar.setMaximumHeight(50)
        self.mbar.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.Maximum)
        
        #Initializing external ui windows that will be bound to main UI:
        self.impw=impOptionsWindow()
        self.funw = funOptionsWindow()
        self.xyzmaker=xyzMakerWindow()
        self.fitw=fitWindow(app = self.app, mainDialog=self)
        self.pyFunsDlg = pyFunWindow()
        
        #Add icons to buttons:
        loadBtnIcon = icnDir/'refresh.png'
        loadBtnIcon = str (loadBtnIcon)
        refIcon =QIcon(QPixmap(loadBtnIcon))
        # self.refreshButton.setStyleSheet(''.join(["color: Blue;\n","qproperty-icon: url(",loadBtnIcon,");\n","qproperty-iconSize: 18px"]))
        self.refreshButton.setIcon(refIcon)
        
        loadBtnIcon = icnDir/'refresh.png'
        loadBtnIcon = str (loadBtnIcon)
        refIcon =QIcon(QPixmap(loadBtnIcon))
        # self.refreshButton.setStyleSheet(''.join(["color: Blue;\n","qproperty-icon: url(",loadBtnIcon,");\n","qproperty-iconSize: 18px"]))
        self.refreshAllButton.setIcon(refIcon)
        
        self.ui.menuLayout.addWidget(self.mbar)
        #Initializing color panel parameters:
        self.leftcolor='#ffffff'
        self.leftclist=[]
        self.rightcolor='#ffffff'
        self.rightclist=[]
        
        #These are used for resize purposes of matplotlib plot font, see below:
        self.newDPI=QApplication.screens()[0].physicalDotsPerInch()
        self.refDPI=125 #This is the reference DPI that the app was originally built for, helps when resizing
        screenRect = QApplication.desktop().screenGeometry()
        self.height = screenRect.height()
        self.width = screenRect.width()
        self.k_vert=self.height/900
        self.k_hor=self.width/1440
        self.k_font=min(self.k_vert*self.newDPI/self.refDPI,self.k_hor*self.newDPI/self.refDPI)
        if platform.system().lower()=='windows':
            self.fontOrRed = 0.95
        else:
            self.fontOrRed = 1
        
        self.apptemp=[] #Necessary when closing temporary application during copying the figure
        
        #Plot initializers, labels
        self.xleftlb='X'
        self.yleftlb='Z'
        self.xrightlb='Y'
        self.yrightlb='Z'
        self.ytoplb='Y'
        self.xtoplb='X'
        self.ztoplb='Z'
        #self.defPreset = 'XY-column' #This is the default mode to be initialized, control can be given to a user
        self.cb2D='' #colorbar does not exist until I plot, if this is not empty string, colorbar will be added
        self.l2Dxrem=0 #This will track if lines in contour graph is removed or added for X axis
        self.l2Dyrem=0 #This will track if lines in contour graph is removed or added for Y axis
        self.legendtext_dyn=[] #List of legends of left plot
        self.legendtext_spec=[] #List of legends of right plot
        self.minmax_xy=[] #this will be used to track maximum value of x and y in xy mode
        
        #Data Preview dialog before importing 
        self.dfPrevDlg=QDialog() #Dialog for showing data previews
        self.view=QTableView(self.dfPrevDlg) #To view dataframe preview
        
        self.d=dict()
        self.dGr=dict()
        self.dGrnames=[]
        self.grdatanames=dict()
        self.dGrtemp=dict()
        self.xlistGr=[]
        
        #Disable certain items until data is loaded or plotting is ready, to avoid app crash:
        #self.ui.fitBtn.setEnabled(False)
        self.fitter.setEnabled(True)
        self.ui.addButton.setEnabled(False)
        self.addoneAction.setEnabled(False)
        self.ui.addallButton.setEnabled(False)
        self.addallAction.setEnabled(False)
        self.ui.refreshButton.setEnabled(False)
        self.ui.refreshAllButton.setEnabled(False)
        self.loadAction.setEnabled(False)
        
        
        #self.copyInternalPreset()
        
        #Load internal presets if default does not exist
        try:
            self.loadDefimpBtn()
            ind=self.ui.listprefs_main.findText(self.defPreset); self.ui.listprefs_main.setCurrentIndex(ind)
            self.prefimp_main() #Loads default presets file to main menu
        except:
            self.loadIntimpBtn()
            ind=self.ui.listprefs_main.findText(self.defPreset); self.ui.listprefs_main.setCurrentIndex(ind)
            self.prefimp_main() #Loads default presets file to main menu
        try:
            self.loadDeffunBtn()
            ind=self.fitw.ui.listfuns_main.findText(self.defFunction); self.fitw.ui.listfuns_main.setCurrentIndex(ind)
            self.funimp_main() #Loads default presets file to main menu
        except:
            self.loadIntfunBtn()
            ind=self.fitw.ui.listfuns_main.findText(self.defFunction); self.fitw.ui.listfuns_main.setCurrentIndex(ind)
            self.funimp_main() #Loads default presets file to main menu
        
        # #Time check for auto dark mode, I think this can be implemented, but I prefer to give control over to the user, Problematic, needs fix
        # # self.timestamp = float(time.strftime('%H:%M:%S')[0:2])
        # # if self.timestamp>=20.5 or self.timestamp<6: #After 8:30pm or before 6 am
        # #     self.ui.darkCheck.setChecked(True)
        # #     self.contStyleToUse = 'dark_background'
        # #     #plt.style.use('dark_background')
        # #     self.axcolor2D='w'
        # # else:
        # #     self.ui.darkCheck.setChecked(False)
        # #     self.contStyleToUse = 'default'
        # #     #plt.style.use('default')
        # #     self.axcolor2D='k'
        # #plt.style.use('default')
        self.contStyleToUse = 'default'
        self.axcolor2D='k'
        
        #Extra UI elements programatically added:
        self.addPlotCanvas(self.contStyleToUse,self.axcolor2D)
        
        self.ui.sliderx = QSlider(self)
        self.ui.sliderx.setOrientation(QtCore.Qt.Horizontal)
        self.ui.layout2D.addWidget(self.ui.sliderx,2, 1, 1, 2)
        
        self.ui.slidery = QSlider(self)
        self.ui.layout2D.addWidget(self.ui.slidery,1, 0, 1, 1)
        
        self.addMenuToPlots()
        
        #Below are all signal connections:
        self.screenSizeChanged.connect(lambda newSize: self.resizeUI2(newSize))
        self.ui.refreshButton.clicked.connect(self.refreshBtn)
        self.ui.refreshAllButton.clicked.connect(self.loadallBtn)
        self.ui.addButton.clicked.connect(self.addBtn)
        self.ui.addallButton.clicked.connect(self.addallBtn)
        self.ui.submitButton.clicked.connect(self.submitButtonPushed)
        self.ui.fontsizeval.valueChanged.connect(lambda newSize: self.fontBtn(newSize))
        self.ui.refinecb.stateChanged.connect(self.refineBtn)
        self.clrBtndyn.clicked.connect(self.clrDlgOpendyn)
        self.clrBtnspec.clicked.connect(self.clrDlgOpenspec)
        self.ui.sliderx.valueChanged.connect(self.sliderxvaluechange)
        self.ui.sliderx.sliderReleased.connect(self.sliderxvaluereleased)
        self.ui.slidery.valueChanged.connect(self.slideryvaluechange)
        self.ui.slidery.sliderReleased.connect(self.slideryvaluereleased)
        self.ui.legcb.stateChanged.connect(self.submitButtonPushed)
        #self.ui.dataBox.activated.connect(self.plot2D)
        self.ui.darkCheck.stateChanged.connect(self.darkChanged) #Problematic needs to be fixed
        self.ui.impOptionsBtn.clicked.connect(self.impOptBtnClicked)
        self.fitw.ui.funOptionsBtn.clicked.connect(self.funOptBtnClicked)
        self.ui.xbgaddButton.clicked.connect(self.xbgaddBtn)
        self.ui.dataBox.activated.connect(self.dataBoxActivated)
        self.getxminButton.clicked.connect(lambda params: self.adjustlimits([self.ui.xminValue,'t','x','min']))
        self.getxmaxButton.clicked.connect(lambda params: self.adjustlimits([self.ui.xmaxValue,'t','x','max']))
        self.getyminButton.clicked.connect(lambda params: self.adjustlimits([self.ui.yminValue,'w','y','min']))
        self.getymaxButton.clicked.connect(lambda params: self.adjustlimits([self.ui.ymaxValue,'w','y','max']))
        self.dataButton.clicked.connect(self.multDataBtn)
        self.sourceButton.clicked.connect(self.multSourceBtn)
        
        # if self.impw.ui.xyz.isChecked() and not self.d=={}:
        #     self.ui.xminValue.setText("{0:.1e}".format(np.nanmin(self.d[self.dataBox.currentText()]['t'])))
        #     self.ui.xmaxValue.setText("{0:.1e}".format(np.nanmax(self.d[self.dataBox.currentText()]['t'])))
        #     self.ui.yminValue.setText("{0:.1e}".format(np.nanmin(self.d[self.dataBox.currentText()]['w'])))
        #     self.ui.ymaxValue.setText("{0:.1e}".format(np.nanmax(self.d[self.dataBox.currentText()]['w'])))
        # elif not self.impw.ui.xyz.isChecked() and not self.d=={}:
        #     self.ui.xminValue.setText("{0:.2e}".format(np.nanmin(self.d[self.dataBox.currentText()]['x'])))
        #     self.ui.xmaxValue.setText("{0:.2e}".format(np.nanmax(self.d[self.dataBox.currentText()]['x'])))
        #     self.ui.yminValue.setText("{0:.2e}".format(np.nanmin(self.d[self.dataBox.currentText()]['y'])))
        #     self.ui.ymaxValue.setText("{0:.2e}".format(np.nanmax(self.d[self.dataBox.currentText()]['y'])))
        
        #Below is for multiple mode connects:
        self.ui.yaddButton.clicked.connect(self.yaddBtn)
        self.ui.yremButton.clicked.connect(self.yremBtn)
        self.ui.xaddButton.clicked.connect(self.xaddBtn)
        self.ui.xremButton.clicked.connect(self.xremBtn)
        
        self.ui.yraddButton.clicked.connect(self.yraddBtn)
        self.ui.yrremButton.clicked.connect(self.yrremBtn)
        self.ui.xraddButton.clicked.connect(self.xraddBtn)
        self.ui.xrremButton.clicked.connect(self.xrremBtn)
        
        self.ui.fxaddButton.clicked.connect(self.fxaddBtn)
        self.ui.fxremButton.clicked.connect(self.fxremBtn)
        self.ui.fyaddButton.clicked.connect(self.fyaddBtn)
        self.ui.fyremButton.clicked.connect(self.fyremBtn)
        self.ui.flzaddButton.clicked.connect(self.flzaddBtn)
        self.ui.flzremButton.clicked.connect(self.flzremBtn)
        self.ui.frzaddButton.clicked.connect(self.frzaddBtn)
        self.ui.frzremButton.clicked.connect(self.frzremBtn)
        
        self.ui.dataAddButton.clicked.connect(self.dataaddBtn)
        self.ui.dataRemButton.clicked.connect(self.dataremBtn)
        self.ui.bgdataAddButton.clicked.connect(self.bgdataaddBtn)
        self.ui.bgdataRemButton.clicked.connect(self.bgdataremBtn)
        
        #self.ui.clearButton.clicked.connect(self.clearLists)
        self.ui.bgnumAddButton.clicked.connect(self.bgdataaddBtn0)
        
        #fit window events:
        self.fitw.ui.xdatabox.currentTextChanged.connect(self.xdataboxchanged)
        self.fitw.ui.ydatabox.currentTextChanged.connect(self.ydataboxchanged)
        self.fitw.ui.fitSubmitBtn.clicked.connect(self.fitSubmitButtonPushed)
        self.fitw.ui.faddButton.clicked.connect(self.faddBtn)
        self.fitw.ui.fremButton.clicked.connect(self.fremBtn)
        self.fitw.ui.parsValue.editingFinished.connect(self.addremparam)
        self.fitw.ui.addSliders.clicked.connect(self.addremparam)
        self.fitw.psliders=[]
        #self.fitw.ui.savefitButton.clicked.connect(self.savefitBtn)
        #self.fitw.ui.loadfitButton.clicked.connect(self.loadfitBtn)
        self.fitw.cpfitbtn.clicked.connect(lambda fromcanvas: self.copyfig(fromcanvas=self.fitw.fitfigcanvas))
        self.fitw.cpeqbtn.clicked.connect(lambda fromcanvas: self.copyfig(fromcanvas=self.fitw.eqcanvas))
        self.fitw.ui.quickaddParam.clicked.connect(self.quickparamaddBtn)
        self.fitw.addModelAs.clicked.connect(self.modelsUpdate)
        self.fitw.modelsW.compareModels.clicked.connect(self.modelsCompare)
        self.fitw.modelsW.clearModels.clicked.connect(self.modelsClear)
        self.fitw.modelsW.addInfo.clicked.connect(self.comparisonInfoAdd)
        self.fitw.modelsW.remInfo.clicked.connect(self.comparisonInfoRem)
        
        #Imp and functions window button connects
        self.impw.ui.xyz.toggled.connect(self.modechanged)
        self.impw.ui.selectimpButton.clicked.connect(self.selectimpBtn)
        self.funw.ui.selectfunButton.clicked.connect(self.selectfunBtn)
        self.impw.ui.loadimpButton.clicked.connect(self.loadimpBtn)
        self.funw.ui.loadfunButton.clicked.connect(self.loadfunBtn)
        self.impw.ui.listprefs.activated.connect(self.prefimp)
        self.ui.listprefs_main.activated.connect(self.prefimp_main)
        self.funw.ui.listfuns.activated.connect(self.funimp)
        self.fitw.ui.listfuns_main.activated.connect(self.funimp_main)
        self.impw.ui.addpresetButton.clicked.connect(self.addpresetBtn)
        self.funw.ui.addfunButton.clicked.connect(self.addfunBtn)
        self.impw.ui.rempresetButton.clicked.connect(self.rempresetBtn)
        self.funw.ui.remfunButton.clicked.connect(self.remfunBtn)
        self.impw.ui.selectPrefSample.clicked.connect(self.selectPrefSampleBtn)
        self.funw.ui.selectFunSample.clicked.connect(self.selectPyBtn)
        self.impw.ui.previewButton.clicked.connect(self.showPreviewDf)
        self.funw.ui.viewPyButton.clicked.connect(self.viewPyFuns)
        self.impw.ui.savepresetsButton.clicked.connect(self.savePresBtn)
        self.funw.ui.savefunsButton.clicked.connect(self.saveFunBtn)
        self.impw.ui.defpresetButton.clicked.connect(self.saveDefPresetBtn)
        self.funw.ui.deffunButton.clicked.connect(self.saveDefFunBtn)
        self.pyFunsDlg.addFuns.clicked.connect(self.addPyFuns)
        
        #Graph options, copy button connects
        self.lbleft.clicked.connect(lambda fromcanvas: self.copyfig(fromcanvas=self.mdyn))
        self.lbright.clicked.connect(lambda fromcanvas: self.copyfig(fromcanvas=self.mspec))
        self.optleft.clicked.connect(self.optsDyn)
        self.optright.clicked.connect(self.optsSpec)
        self.opt2D.clicked.connect(self.opts2D)
        
        #3dmaker Window button connects
        #self.ui.xyzmakerButton.clicked.connect(self.xyzmakerClicked)
        self.xyzmaker.ui.findGrButton.clicked.connect(self.getGrFolderLoc)
        self.xyzmaker.ui.impGrOptionsBtn.clicked.connect(self.impOptBtnClicked)
        self.xyzmaker.ui.addGrButton.clicked.connect(self.addGrBtn)
        self.xyzmaker.ui.dataGrAddButton.clicked.connect(self.dataGraddBtn)
        self.xyzmaker.ui.dataGrRemButton.clicked.connect(self.dataGrremBtn)
        self.xyzmaker.ui.xAutoButton.clicked.connect(self.autogenX)
        self.xyzmaker.ui.addtoGrButton.clicked.connect(self.addtoGroup)
        self.xyzmaker.ui.GrtoMainButton.clicked.connect(self.grtomain)
        self.xyzmaker.ui.cleanGrButton.clicked.connect(self.cleanGrBtn)
        self.xyzmaker.ui.xGraddButton.clicked.connect(self.xGraddBtn)
        self.xyzmaker.ui.xGrremButton.clicked.connect(self.xGrremBtn)
        self.xyzmaker.ui.remFromGr.clicked.connect(self.remfrGr)
        
        # Below are the run of the menu actions to prepare initial state of the app accordingly (e.g. show/hide menus from graphxyz.ui)
        self.widgetHiderShower(self.ui.dataListFrame, mAction = self.dataListAction)
        self.widgetHiderShower(self.ui.dataLinkFrame, mAction = self.dataLinkListAction)
        self.widgetHiderShower(self.ui.ysliceFrame, mAction = self.ySliceAction)
        self.widgetHiderShower(self.ui.xsliceFrame, mAction = self.xSliceAction)
        self.widgetHiderShower(self.ui.ylimFrame, mAction = self.yLimsAction)
        self.widgetHiderShower(self.ui.xlimFrame, mAction = self.xLimsAction)
        self.widgetHiderShower(self.ui.fxyFrame, mAction = self.fxyAction)
        self.widgetHiderShower(self.ui.fzzFrame, mAction = self.fzAction)
        self.widgetHiderShower(self.ui.controlsframe, mAction = self.graphAction)
        self.widgetHiderShower(self.ui.plotLimits, mAction = self.plotAction)
        self.widgetHiderShower([self.ui.frame2D, self.mdynTlb, self.mspecTlb, self.m2DTlb, self.controlsFrame2D, self.controlsFrameSpec,self.controlsFrameDyn], mAction = self.plotControlsAction)
        #self.widgetHiderShower(self.ui.frameSpec, mAction = self.figureSpec)
        #self.widgetHiderShower(self.ui.frameDyn, mAction = self.figureDyn)
        
        
        #Initial run for default mode:
        self.modechangedMain()
        self.modechanged()
        
        self.optsDynW=optsWindow(leftright='Left Figure',xyzmode=self.impw.ui.xyz.isChecked())
        self.optsSpecW=optsWindow(leftright='Right Figure',xyzmode=self.impw.ui.xyz.isChecked())
        self.opts2DW=optsWindow(leftright='Top Figure',xyzmode=self.impw.ui.xyz.isChecked())
        
        self.multDataChooser = multWindow(sourceLabels=[' data','Add'])
        self.multSourceChooser = multWindow(sourceLabels=[' sources','Remove'])
        self.multDataChooser.button.clicked.connect(self.multDataAddBtn)
        self.multSourceChooser.button.clicked.connect(self.multSourceRemBtn)
        #self.fontBtn()
        
        #Enable sliders:
        self.ui.sliderx.setEnabled(False)
        self.ui.slidery.setEnabled(False)
        
        #Save original fonts to use as a reference
        self.orFonts = self.getOrFontsPosts()[0]
        self.orPosts = self.getOrFontsPosts()[1]
        self.resizeUI(QApplication.screens()[0],QApplication.screens()[0]) #Resize UI to fit to the current window
        
        # self.loadDefBtn()
        # try:
        #     self.submitButtonPushed(noMessage=True)
        # except Exception as Argument:
        #     self.genLogforException(Argument)
        
        #print(self.findChild(QMenuBar,"mbar"))
        
        self.show()
        
        npyDir = self.makeFolderinDocuments ('Saved Tabs')
        npyPath = npyDir / 'reset'
        self.saveBtn(npyPath, showPopInfo= False,fitneedsaved=False)#Renews reset file everytime it launches so reset becomes as intended, otherwise software update will require new reset file everytime
    # def addWidgetToLoadList(self, widget, key):
    #     widget.setObjectName(key)
    #     self.listOfWidgetKeys.
    def makeFolderinDocuments(self, foldName): 
        foldDir = getResourcePath(os.path.expanduser('~'))/'Documents'/'Graphxyz'
        os.makedirs(foldDir, exist_ok = True)
        foldDir = foldDir / foldName
        os.makedirs(foldDir, exist_ok = True)
        return foldDir
    def genLogforException(self, Argument):
        logLoc = self.exceptionLogLocation
        logLoc = logLoc / 'Exception logs.txt'
        f = open(logLoc, "a")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f.write(''.join(['\n',str([exc_tb.tb_lineno,Argument]),datetime.now(). strftime("%m/%d/%Y, %H:%M:%S")]))
        f.close()
    def menuAdder(self, alreadyExist = False):
        if alreadyExist:
            self.mbar.parent(None)
        mbar=QMenuBar(self)
        mbar.setNativeMenuBar(False)
        #file=mbar.addMenu("File")
        dataMenu = mbar.addMenu("Data")
        tabs = mbar.addMenu("Tab")
        tools = mbar.addMenu("Tools")
        modes = mbar.addMenu("Plot modes")
        self.views = mbar.addMenu("View")
        
        #file.addAction("Open...")
        #file.addSeparator()
        self.importTypes = QActionGroup(mbar)
        self.importTypes.setExclusive(True)
        load=dataMenu.addMenu("Find")
        findFolder = load.addAction("Folder")
        findFolder.setCheckable(True)
        findFolders = load.addAction("Folders")
        findFolders.setCheckable(True)
        findFiles = load.addAction("Files")
        findFiles.setCheckable(True)
        self.importTypes.addAction(findFolder)
        self.importTypes.addAction(findFolders)
        self.importTypes.addAction(findFiles)
        findFolder.triggered.connect(self.getFolderLoc)
        findFolders.triggered.connect(self.getFolderLoc)
        findFiles.triggered.connect(self.getFolderLoc)
        dataMenu.addSeparator()
        
        
        self.loadAction = dataMenu.addAction("Load")
        self.loadAction.triggered.connect(self.refreshBtn)
        self.addoneAction = dataMenu.addAction("Add")
        self.addoneAction.triggered.connect(self.addBtn)
        self.addallAction = dataMenu.addAction("Add all")
        self.addallAction.triggered.connect(self.addallBtn)
        dataMenu.addSeparator()
        cleanAction = dataMenu.addAction("Clear source")
        cleanAction.triggered.connect(self.cleanBtn)
        clearList = dataMenu.addAction("Clear list")
        clearList.triggered.connect(self.clearLists)
        dataMenu.addSeparator()
        self.dataExporterAction = dataMenu.addAction("Export data")
        self.dataExporterAction.setChecked(True)
        self.dataExporterAction.triggered.connect(self.dataExporter)
        
        self.addTab=tabs.addAction("New Tab")
        #self.addTab.triggered.connect(self.newBtn)
        tabs.addSeparator()
        self.addTab.setShortcut(QKeySequence("Ctrl+T"))
        resetTab=tabs.addAction("Reset")
        resetTab.triggered.connect(self.resetBtn)
        resetTab.setShortcut(QKeySequence("Ctrl+R"))
        
        tabs.addSeparator()
        loadDef = tabs.addAction("Load default")
        loadDef.triggered.connect(self.loadDefBtn)
        loadDef.setShortcut(QKeySequence("Ctrl+L"))
        saveDef = tabs.addAction("Save default")
        saveDef.triggered.connect(self.saveDefBtn)
        saveDef.setShortcut(QKeySequence("Ctrl+S"))
        loadas = tabs.addAction("Load...")
        loadas.triggered.connect(self.loadasBtn)
        loadas.setShortcut(QKeySequence("Ctrl+Shift+L"))
        saveas = tabs.addAction("Save as...")
        saveas.triggered.connect(self.saveasBtn)
        #saveas.setShortcut(QKeySequence("Ctrl+Shift+S"))
        
        # impPref=tools.addAction("Preset options...")
        # impPref.triggered.connect(self.impOptBtnClicked)
        self.fitter = tools.addAction("Fit...")
        self.fitter.setShortcut(QKeySequence("Ctrl+F"))
        maker3D=tools.addAction("3D maker: XY+Z...")
        maker3D.triggered.connect(self.xyzmakerClicked)
        
        
        #parsMenu = modes.addMenu("Parameters")
        
        # self.parModes = QActionGroup(mbar)
        # self.parModes.setExclusive(True)
        # self.XYaction = modes.addAction ("XY")
        # self.XYaction.setCheckable(True)
        # self.XYaction.setDisabled(True)
        # self.XYaction.setChecked(False)
        # self.parModes.addAction(self.XYaction)
        # self.XYZaction = modes.addAction ("XYZ")
        # self.XYZaction.setCheckable(True)
        # self.XYZaction.setDisabled(True)
        # self.XYZaction.setChecked(True)
        # self.parModes.addAction(self.XYZaction)
        # self.XYZaction.toggled.connect(self.modechangedMain)
        # modes.addSeparator()
        
        self.plotModes = QActionGroup(mbar)
        self.plotModes.setExclusive(True)
        self.singleMode = modes.addAction("Selected")
        self.singleMode.setCheckable(True)
        self.singleMode.setChecked(True)
        self.plotModes.addAction(self.singleMode)
        self.multD = modes.addAction("Multiple at single x and y")
        self.multD.setCheckable(True)
        self.plotModes.addAction(self.multD)
        self.multXY = modes.addAction("Single at multiple x and y")
        self.multXY.setCheckable(True)
        self.plotModes.addAction(self.multXY)
        self.matchD = modes.addAction("Matched with x and y")
        self.matchD.setCheckable(True)
        self.plotModes.addAction(self.matchD)
        
        #View Menu action items:
        self.hideShowAllAction = self.views.addAction("All")
        self.hideShowAllAction.setCheckable(True)
        self.hideShowAllAction.setChecked(False)
        self.hideShowAllAction.toggled.connect(self.hideShowAll)
        self.hideShowAllAction.setShortcut(QKeySequence("Ctrl+V"))
        #showAll = self.views.addAction("Show all")
        #showAll.triggered.connect(self.showAllViews)
        
        self.views.addSeparator()
        self.figure2D = self.views.addAction("Top figure")
        self.figure2D.setCheckable(True)
        self.figure2D.setChecked(False)
        self.figure2D.toggled.connect(lambda widgetFrame: self.figHiderShower(self.ui.frame2D, mAction = self.figure2D))
        
        self.figureDyn = self.views.addAction("Left figure")
        self.figureDyn.setCheckable(True)
        self.figureDyn.setChecked(True)
        self.figureDyn.toggled.connect(lambda widgetFrame: self.figHiderShower(self.ui.frameDyn, mAction = self.figureDyn))
        
        self.figureSpec = self.views.addAction("Right figure")
        self.figureSpec.setCheckable(True)
        self.figureSpec.setChecked(True)
        self.figureSpec.toggled.connect(lambda widgetFrame: self.figHiderShower(self.ui.frameSpec, mAction = self.figureSpec))
        
        self.views.addSeparator()
        self.graphAction = self.views.addAction("Refine settings")
        self.graphAction.setCheckable(True)
        self.graphAction.setChecked(False)
        self.graphAction.toggled.connect(lambda widgetFrame: self.widgetHiderShower(self.ui.controlsframe, mAction = self.graphAction))
        
        self.plotControlsAction = self.views.addAction("Plot controls")
        self.plotControlsAction.setCheckable(True)
        self.plotControlsAction.setChecked(False)
        self.plotControlsAction.toggled.connect(lambda widgetFrame: self.widgetHiderShower([self.mdynTlb, self.mspecTlb, self.m2DTlb, self.controlsFrame2D, self.controlsFrameSpec,self.controlsFrameDyn], mAction = self.plotControlsAction))
        
        self.plotAction = self.views.addAction("Plot limits")
        self.plotAction.setCheckable(True)
        self.plotAction.setChecked(False)
        self.plotAction.toggled.connect(lambda widgetFrame: self.widgetHiderShower(self.ui.plotLimits, mAction = self.plotAction))
        
        self.views.addSeparator()
        self.dataListAction = self.views.addAction("Data list")
        self.dataListAction.setCheckable(True)
        self.dataListAction.setChecked(False)
        self.dataListAction.toggled.connect(lambda widgetFrame: self.widgetHiderShower(self.ui.dataListFrame, mAction = self.dataListAction))
        
        self.dataLinkListAction = self.views.addAction("Data link")
        self.dataLinkListAction.setCheckable(True)
        self.dataLinkListAction.setChecked(False)
        self.dataLinkListAction.toggled.connect(lambda widgetFrame: self.widgetHiderShower(self.ui.dataLinkFrame, mAction = self.dataLinkListAction))
        
        self.ySliceAction = self.views.addAction("y-slices")
        self.ySliceAction.setCheckable(True)
        self.ySliceAction.setChecked(False)
        self.ySliceAction.toggled.connect(lambda widgetFrame: self.widgetHiderShower(self.ui.ysliceFrame, mAction = self.ySliceAction))
        
        self.xSliceAction = self.views.addAction("x-slices")
        self.xSliceAction.setCheckable(True)
        self.xSliceAction.setChecked(False)
        self.xSliceAction.toggled.connect(lambda widgetFrame: self.widgetHiderShower(self.ui.xsliceFrame, mAction = self.xSliceAction))
        
        self.yLimsAction = self.views.addAction("y-limits")
        self.yLimsAction.setCheckable(True)
        self.yLimsAction.setChecked(False)
        self.yLimsAction.toggled.connect(lambda widgetFrame: self.widgetHiderShower(self.ui.ylimFrame, mAction = self.yLimsAction))
        
        self.xLimsAction = self.views.addAction("x-limits")
        self.xLimsAction.setCheckable(True)
        self.xLimsAction.setChecked(False)
        self.xLimsAction.toggled.connect(lambda widgetFrame: self.widgetHiderShower(self.ui.xlimFrame, mAction = self.xLimsAction))
        
        self.fxyAction = self.views.addAction("f(x) and f(y)")
        self.fxyAction.setCheckable(True)
        self.fxyAction.setChecked(False)
        self.fxyAction.toggled.connect(lambda widgetFrame: self.widgetHiderShower(self.ui.fxyFrame, mAction = self.fxyAction))
        
        self.fzAction = self.views.addAction("f(z)")
        self.fzAction.setCheckable(True)
        self.fzAction.setChecked(False)
        self.fzAction.toggled.connect(lambda widgetFrame: self.widgetHiderShower(self.ui.fzzFrame, mAction = self.fzAction))
        
        return mbar
    def widgetHiderShower(self, widgetFrame, mAction = None):
        if not type(widgetFrame) is list:
            if not mAction.isChecked():
                widgetFrame.setVisible(False)
            else:
                widgetFrame.setVisible(True)
        else:
            if not mAction.isChecked():
                for frames in widgetFrame:
                    frames.setVisible(False)
            else:
                for frames in widgetFrame:
                    frames.setVisible(True)
    def figHiderShower(self,widgetFrame, mAction = None):
        mainWindowToResize = self.app.activeWindow()
        #mainWindowToResize=self.app.topLevelWidgets()[0]
        #self.currWindowSize
        if not mAction.isChecked():
            # if widgetFrame==self.ui.frame2D:
            #     self.app.focusWidget().resize(int(self.app.focusWidget().geometry().width()/2),self.app.focusWidget().geometry().height())
            # if widgetFrame==self.ui.frameSpec and not self.figureDyn.isChecked():
            #     self.app.focusWidget().resize(self.app.focusWidget().geometry().height(),min(int(self.app.focusWidget().geometry().height()/2),int(QApplication.desktop().geometry().height())))
            try:
                #Width adjustments:
                if mAction==self.figure2D and not self.figureDyn.isChecked() and not self.figureSpec.isChecked():
                    resizeTo=int(mainWindowToResize.geometry().width()/2)
                    mainWindowToResize.resize(resizeTo, mainWindowToResize.geometry().height())
                elif mAction==self.figure2D and not self.figureDyn.isChecked() and self.figureSpec.isChecked():
                    resizeTo=int(mainWindowToResize.geometry().width()/2)
                    mainWindowToResize.resize(resizeTo, mainWindowToResize.geometry().height())
                elif mAction==self.figure2D and self.figureDyn.isChecked() and not self.figureSpec.isChecked():
                    resizeTo=int(mainWindowToResize.geometry().width()/2)
                    mainWindowToResize.resize(resizeTo, mainWindowToResize.geometry().height())
                elif mAction==self.figureDyn and not self.figure2D.isChecked() and self.figureSpec.isChecked():
                    resizeTo=int(mainWindowToResize.geometry().width()/2)
                    mainWindowToResize.resize(resizeTo, mainWindowToResize.geometry().height())
                elif mAction==self.figureSpec and not self.figure2D.isChecked() and self.figureDyn.isChecked():
                    resizeTo=int(mainWindowToResize.geometry().width()/2)
                    mainWindowToResize.resize(resizeTo, mainWindowToResize.geometry().height())
                
                #Height adjustments:
                elif mAction==self.figureDyn and not self.figure2D.isChecked() and not self.figureSpec.isChecked():
                    resizeTo=int(mainWindowToResize.geometry().height()/2)
                    mainWindowToResize.resize(mainWindowToResize.geometry().width(),resizeTo)
                elif mAction==self.figureDyn and self.figure2D.isChecked() and not self.figureSpec.isChecked():
                    resizeTo=int(mainWindowToResize.geometry().height()/2)
                    mainWindowToResize.resize(mainWindowToResize.geometry().width(),resizeTo)
                elif mAction==self.figureSpec and not self.figure2D.isChecked() and not self.figureDyn.isChecked():
                    resizeTo=int(mainWindowToResize.geometry().height()/2)
                    mainWindowToResize.resize(mainWindowToResize.geometry().width(),resizeTo)
                elif mAction==self.figureSpec and self.figure2D.isChecked() and not self.figureDyn.isChecked():
                    resizeTo=int(mainWindowToResize.geometry().height()/2)
                    mainWindowToResize.resize(mainWindowToResize.geometry().width(),resizeTo)
            except Exception as Argument:
                self.genLogforException(Argument)
            widgetFrame.setVisible(False)
        else:
            try:
                #Width Adjustments
                if mAction==self.figure2D and self.figureDyn.isChecked() and not self.figureSpec.isChecked():
                    resizeTo=min( int(mainWindowToResize.geometry().width()*2), int(self.currWindowSize.width()*1) )
                    mainWindowToResize.resize(resizeTo,mainWindowToResize.geometry().height())
                elif mAction==self.figure2D and not self.figureDyn.isChecked() and self.figureSpec.isChecked():
                    resizeTo=min( int(mainWindowToResize.geometry().width()*2), int(self.currWindowSize.width()*1) )
                    mainWindowToResize.resize(resizeTo,mainWindowToResize.geometry().height())
                elif mAction==self.figure2D and not self.figureDyn.isChecked() and not self.figureSpec.isChecked():
                    resizeTo=min( int(mainWindowToResize.geometry().width()*2), int(self.currWindowSize.width()*1) )
                    mainWindowToResize.resize(resizeTo,mainWindowToResize.geometry().height())
                    
                elif mAction==self.figureDyn and not self.figure2D.isChecked() and self.figureSpec.isChecked():
                    resizeTo=min( int(mainWindowToResize.geometry().width()*2), int(self.currWindowSize.width()*1) )
                    mainWindowToResize.resize(resizeTo,mainWindowToResize.geometry().height())
                elif mAction==self.figureSpec and not self.figure2D.isChecked() and self.figureDyn.isChecked():
                    resizeTo=min( int(mainWindowToResize.geometry().width()*2), int(self.currWindowSize.width()*1) )
                    mainWindowToResize.resize(resizeTo,mainWindowToResize.geometry().height())
                
                #Height adjustments:
                elif mAction==self.figureDyn and not self.figure2D.isChecked() and not self.figureSpec.isChecked():
                    resizeTo=min( int(mainWindowToResize.geometry().height()*2), int(self.currWindowSize.height()*1) )
                    mainWindowToResize.resize(mainWindowToResize.geometry().width(),resizeTo)
                elif mAction==self.figureDyn and self.figure2D.isChecked() and not self.figureSpec.isChecked():
                    resizeTo=min( int(mainWindowToResize.geometry().height()*2), int(self.currWindowSize.height()*1) )
                    mainWindowToResize.resize(mainWindowToResize.geometry().width(),resizeTo)
                elif mAction==self.figureSpec and not self.figure2D.isChecked() and not self.figureDyn.isChecked():
                    resizeTo=min( int(mainWindowToResize.geometry().height()*2), int(self.currWindowSize.height()*1) )
                    mainWindowToResize.resize(mainWindowToResize.geometry().width(),resizeTo)
                elif mAction==self.figureSpec and self.figure2D.isChecked() and not self.figureDyn.isChecked():
                    resizeTo=min( int(mainWindowToResize.geometry().height()*2), int(self.currWindowSize.height()*1) )
                    mainWindowToResize.resize(mainWindowToResize.geometry().width(),resizeTo)
            except Exception as Argument:
                self.genLogforException(Argument)
            widgetFrame.setVisible(True)
    def resizewhenTabChanged(self): #Adjust width when tab changed, #To change size when tab changed, experimental
        mainWindowToResize = self.app.activeWindow()
        if self.impw.ui.xyz.isChecked() or self.figureSpec.isChecked():
            resizeTo=min(mainWindowToResize.geometry().width()*2, self.currWindowSize.width()*1 )
            mainWindowToResize.resize(resizeTo,mainWindowToResize.geometry().height())
        elif not self.impw.ui.xyz.isChecked():
            resizeTo=int(mainWindowToResize.geometry().width()/2)
            mainWindowToResize.resize(resizeTo, mainWindowToResize.geometry().height())
    def hideShowAll(self):
        if not self.hideShowAllAction.isChecked():
            for action in self.views.actions():
                if not action==self.hideShowAllAction and not action==self.figureDyn and not action==self.figureSpec and not action==self.figure2D:
                    action.setChecked(False)
        else:
            for action in self.views.actions():
                if not action==self.hideShowAllAction and not action==self.figureDyn and not action==self.figureSpec and not action==self.figure2D:
                    action.setChecked(True)
    # def hideAllViews(self):
    #     for action in self.views.actions():
    #         action.setChecked(False)
    # def showAllViews(self):
    #     for action in self.views.actions():
    #         action.setChecked(True)
        
    def addPlotCanvas(self,contourStyleToUse,contourLabelColor):
        plt.style.use(contourStyleToUse)
        # plt.rcParams['font.size']=str(int(10*self.k_font))
        self.ui.layout2D.addWidget(PlotCanvas(self, width=7.41, height=4.61,dpi=100, left=0, bottom=0, right=1, top=1),1, 1, 1, 2)
        self.ui.layoutDyn.addWidget(PlotCanvas(self, width=7.41, height=4.61,dpi=100),1, 0, 1, 2)
        self.ui.layoutSpec.addWidget(PlotCanvas(self, width=7.41, height=4.61,dpi=100),1, 0, 1, 2)
        
        index2D=self.ui.layout2D.count()-1; self.m2D=self.ui.layout2D.itemAt(index2D).widget()
        #Matplotlib Connects:
        self.m2D.mpl_connect('button_press_event', self.onClick2D)
        self.fig2D=self.m2D.figure #This mgiht be unused, might remove later
        self.ax2D=self.m2D.axes
        
        indexspec=self.ui.layoutSpec.count()-1; self.mspec=self.ui.layoutSpec.itemAt(indexspec).widget()
        self.figspec =self.mspec.axes #This mgiht be unused, might remove later
        self.axspec=self.mspec.axes
        
        indexdyn=self.ui.layoutDyn.count()-1; self.mdyn=self.ui.layoutDyn.itemAt(indexdyn).widget()
        self.figdyn=self.mdyn.axes #This mgiht be unused, might remove later
        self.axdyn=self.mdyn.axes
        
        self.ax2D.clear(); self.ax2D.tick_params(direction='in',pad=-25,labelcolor=contourLabelColor)
        self.axdyn.clear()
        self.axspec.clear()
        
        self.ui.layout2D.addWidget(NavigationToolbar_new(self.m2D,self.ax2D,self),0, 1, 1, 1)
        index=self.ui.layout2D.count()-1
        self.m2DTlb=self.ui.layout2D.itemAt(index).widget()
        self.m2DTlb.setMaximumSize(QtCore.QSize(1250, int(25*self.k_vert)))
    
        self.navDyn = NavigationToolbar_new(self.mdyn, self.axdyn, self)
        self.ui.layoutDyn.addWidget(self.navDyn,0, 0, 1, 1)
        index=self.ui.layoutDyn.count()-1
        self.mdynTlb=self.ui.layoutDyn.itemAt(index).widget()
        self.mdynTlb.setMaximumSize(QtCore.QSize(1250, int(25*self.k_vert)))
        #self.mdynTlb.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.Ignored)
        
        self.ui.layoutSpec.addWidget(NavigationToolbar_new(self.mspec, self.axspec, self),0, 0, 1, 1)
        index=self.ui.layoutSpec.count()-1
        self.mspecTlb=self.ui.layoutSpec.itemAt(index).widget()
        self.mspecTlb.setMaximumSize(QtCore.QSize(1250, int(25*self.k_vert)))
        #self.mspecTlb.setSizePolicy(QtWidgets.QSizePolicy.Ignored,QtWidgets.QSizePolicy.Ignored)
        
        self.c_map_ax = self.m2D.figure.add_axes([0.96, 0.3, 0.01, 0.5])
        self.c_map_ax.set_ylabel(self.ztoplb,rotation=0)
        self.axspec.set_xlabel(self.xrightlb)
        self.axspec.set_ylabel(self.yrightlb)
        self.axdyn.set_xlabel(self.xleftlb)
        self.axdyn.set_ylabel(self.yleftlb)
        self.ax2D.set_ylabel(self.ytoplb)
        self.ax2D.set_xlabel(self.xtoplb)
        self.ax2D.yaxis.set_label_coords(0.075,0.5)
        self.ax2D.xaxis.set_label_coords(0.5,0.125)
        self.mdyn.figure.tight_layout()
        self.mspec.figure.tight_layout()
    
    def addMenuToPlots(self):
        #Addding extra menu to left figure
        self.controlsFrameDyn=QtWidgets.QFrame(self)
        self.ui.layoutDyn.addWidget(self.controlsFrameDyn, 0, 1, 1, 1)
        self.clrlaydyn = QtWidgets.QGridLayout(self.controlsFrameDyn)
        self.clrlaydyn.setContentsMargins(0, 0, 0, 0)
        self.clrlaydyn.setVerticalSpacing(0)
        self.clrlaydyn.setHorizontalSpacing(10)
        self.clrCbdyn=QtWidgets.QCheckBox(self.controlsFrameDyn)
        self.clrCbdyn.setMaximumSize(QtCore.QSize(21, 30))
        self.clrCbdyn.setToolTip('Check this to use custom colors')
        self.clrBtndyn=QtWidgets.QPushButton(self.controlsFrameDyn)
        self.clrBtndyn.setMaximumSize(QtCore.QSize(75, 32))
        self.clrBtndyn.setText('Colors')
        self.clrBtndyn.setStyleSheet("border :1.5px solid ;"
                                   "border-top-color : red; "
                                   "border-left-color :pink;"
                                   "border-right-color :yellow;"
                                   "border-bottom-color : green")
        self.lbleft=QtWidgets.QPushButton(self)
        self.lbleft.setMaximumSize(QtCore.QSize(32, 32))
        self.lbleft.setText('C')
        self.lbleft.setToolTip('Press to Copy to Clipboard')
        
        self.optleft=QtWidgets.QPushButton(self)
        self.optleft.setMaximumSize(QtCore.QSize(40, 32))
        self.optleft.setText('...')
        self.optleft.setToolTip('Press for more Options')
        
        self.clrlaydyn.addWidget(self.optleft,0,0,1,1)
        self.clrlaydyn.addWidget(self.lbleft,0,1,1,1)
        self.clrlaydyn.addWidget(self.clrCbdyn,0,2,1,1)
        self.clrlaydyn.addWidget(self.clrBtndyn,0,3,1,1)
        
        #Adding extra menu to rigth figure:
        self.controlsFrameSpec=QtWidgets.QFrame(self)
        self.ui.layoutSpec.addWidget(self.controlsFrameSpec,0, 1, 1, 1)
        self.clrlayspec = QtWidgets.QGridLayout(self.controlsFrameSpec)
        self.clrlayspec.setContentsMargins(0, 0, 0, 0)
        self.clrlayspec.setVerticalSpacing(0)
        self.clrlayspec.setHorizontalSpacing(10)
        self.clrCbspec=QtWidgets.QCheckBox(self.controlsFrameSpec)
        self.clrCbspec.setMaximumSize(QtCore.QSize(21, 30))
        self.clrCbspec.setToolTip('Check this to use custom colors')
        self.clrBtnspec=QtWidgets.QPushButton(self.controlsFrameSpec)
        self.clrBtnspec.setMaximumSize(QtCore.QSize(75, 32))
        self.clrBtnspec.setText('Colors')
        self.clrBtnspec.setStyleSheet("border :1.5px solid ;"
                                   "border-top-color : red; "
                                   "border-left-color :pink;"
                                   "border-right-color :yellow;"
                                   "border-bottom-color : green")
        self.lbright=QtWidgets.QPushButton(self)
        self.lbright.setMaximumSize(QtCore.QSize(32, 32))
        self.lbright.setText('C')
        self.lbright.setToolTip('Press to Copy to Clipboard')
        
        self.optright=QtWidgets.QPushButton(self)
        self.optright.setMaximumSize(QtCore.QSize(40, 32))
        self.optright.setText('...')
        self.optright.setToolTip('Press for more Options')
        
        self.clrlayspec.addWidget(self.optright,0,0,1,1)
        self.clrlayspec.addWidget(self.lbright,0,1,1,1)
        self.clrlayspec.addWidget(self.clrCbspec,0, 2, 1, 1)
        self.clrlayspec.addWidget(self.clrBtnspec,0, 3, 1, 1)
        
        self.controlsFrame2D=QtWidgets.QFrame(self)
        self.ui.layout2D.addWidget(self.controlsFrame2D,0, 2, 1, 1)
        self.clrlay2D = QtWidgets.QGridLayout(self.controlsFrame2D)
        
        self.opt2D=QtWidgets.QPushButton(self)
        self.opt2D.setMaximumSize(QtCore.QSize(40, 32))
        self.opt2D.setText('...')
        self.opt2D.setToolTip('Press for more Options')
        
        self.clrlay2D.addWidget(self.opt2D,0,0,1,1)
    def getOrFontsPosts(self):
        comp1=self.ui.findChildren(QPushButton)
        comp2=self.ui.findChildren(QLabel)
        comp3=self.ui.findChildren(QLineEdit)
        comp4=self.ui.findChildren(QRadioButton)
        comp5=self.ui.findChildren(QCheckBox)
        comp6=self.ui.findChildren(QComboBox)
        comp7=self.ui.findChildren(QListWidget)
        comp=comp1+comp2+comp3+comp4+comp5+comp6+comp7
        orFonts = []
        orPosts = []
        for compi in comp:
            try:
                pos=compi.geometry()
                orPosts.append(pos)
            except Exception as Argument:
                self.genLogforException(Argument)
            try:
                fonti=compi.font().pointSize()*self.fontOrRed
                orFonts.append(fonti)
            except Exception as Argument:
                self.genLogforException(Argument)
        return orFonts, orPosts
    def resizeUI(self,oldScreen,newScreen):
        try:
            self.currWindowSize = self.currWindowSize
            #print(self.currWindowSize)
            screenRect = newScreen.geometry()
            self.height = screenRect.height()
            self.width = screenRect.width()
            self.heightold = QApplication.screens()[0].geometry().height()
            self.widthold = QApplication.screens()[0].geometry().width()
            self.k_vert=self.height/self.heightold
            self.k_hor=self.width/self.widthold
            uisize=self.geometry()
            screenWidth = uisize.width();
            screenHeight = uisize.height();
            left = uisize.left();
            bottom = uisize.bottom();
            width = screenWidth*self.k_hor;
            screenHeight = screenHeight*self.k_vert;
            self.k_font = (self.k_vert + self.k_hor)/2
            self.setGeometry(int(round(left,0)),int(round(bottom,0)),int(round(width,0)),int(round(screenHeight,0)));
            
            comp1=self.ui.findChildren(QPushButton)
            comp2=self.ui.findChildren(QLabel)
            comp3=self.ui.findChildren(QLineEdit)
            comp4=self.ui.findChildren(QRadioButton)
            comp5=self.ui.findChildren(QCheckBox)
            comp6=self.ui.findChildren(QComboBox)
            comp7=self.ui.findChildren(QListWidget)
            
            # comp8=self.impw.ui.findChildren(QLineEdit)
            # comp9=self.impw.ui.findChildren(QLabel)
            # comp10=self.impw.ui.findChildren(QLineEdit)
            # comp11=self.impw.ui.findChildren(QRadioButton)
            # comp12=self.impw.ui.findChildren(QCheckBox)
            # comp13=self.impw.ui.findChildren(QComboBox)
            # comp14=self.impw.ui.findChildren(QListWidget)
            
            comp=comp1+comp2+comp3+comp4+comp5+comp6+comp7#+comp8++comp9+comp10+comp11+comp12+comp13+comp14
            for ci in range(len(comp)):
                compi=comp[ci]
                try:
                    pos=compi.geometry()
                    compi.setGeometry(QtCore.QRect(int(round(pos.left()*self.k_hor,0)),int(round(pos.top()*self.k_vert,0)),int(round(pos.width()*self.k_hor,0)),int(round(pos.height()*self.k_hor,0))))
                except Exception as Argument:
                    self.genLogforException(Argument)
                try:
                    fonttemp=compi.font()
                    fontitype=fonttemp.family()
                    if platform.system().lower()=='windows':
                        compi.setFont(QFont(fontitype,int(self.orFonts[ci]*0.8*self.k_font)))
                    else:
                        compi.setFont(QFont(fontitype,int(self.orFonts[ci]*1.1*self.k_font)))
                except Exception as Argument:
                    self.genLogforException(Argument)
            if platform.system().lower()=='windows':
                self.mdynTlb.setMaximumSize(QtCore.QSize(1250, int(0.025*self.height*self.k_vert)))
                self.mspecTlb.setMaximumSize(QtCore.QSize(1250, int(0.025*self.height*self.k_vert)))
                self.m2DTlb.setMaximumSize(QtCore.QSize(1250, int(0.025*self.height*self.k_vert)))
            else:
                #print(int(self.height*self.k_vert))
                self.mdynTlb.setMaximumSize(QtCore.QSize(1250, int(0.03*self.height*self.k_vert)))
                self.mspecTlb.setMaximumSize(QtCore.QSize(1250, int(0.03*self.height*self.k_vert)))
                self.m2DTlb.setMaximumSize(QtCore.QSize(1250, int(0.03*self.height*self.k_vert)))
        except Exception as Argument:
            self.genLogforException(Argument)
    def resizeUI2(self,newSize):
        refDPI = 120
        newDPI=QApplication.screens()[0].physicalDotsPerInch()
        #print(newDPI)
        self.height = newSize.height()
        self.width = newSize.width()
        self.heightold = 900
        self.widthold = 1440
        font_coef = (np.sqrt(self.heightold**2+self.widthold**2) / np.sqrt(self.height**2+self.width**2))
        self.k_vert=self.height/self.heightold
        self.k_hor=self.width/self.widthold
        self.k_font = (self.k_vert + self.k_hor)/2
        #self.k_font = max(self.k_vert*newDPI/refDPI,self.k_hor*newDPI/refDPI)
        self.k_font2=max(self.k_vert,self.k_hor)*newDPI/refDPI
        
        #self.ui.controlwindowframe.resize(self.ui.frameDyn.width(),self.ui.controlwindowframe.height())
        
        comp1=self.ui.findChildren(QPushButton)
        comp2=self.ui.findChildren(QLabel)
        comp3=self.ui.findChildren(QLineEdit)
        comp4=self.ui.findChildren(QRadioButton)
        comp5=self.ui.findChildren(QCheckBox)
        comp6=self.ui.findChildren(QComboBox)
        comp7=self.ui.findChildren(QListWidget)
        
        comp=comp1+comp2+comp3+comp4+comp5+comp6+comp7
        for ci in range(len(comp)):
            compi=comp[ci]
            try:
                fonttemp=compi.font()
                fontitype=fonttemp.family()
                if platform.system().lower()=='windows':
                    #print(font_coef*1*self.k_font)
                    compi.setFont(QFont(fontitype,int(self.orFonts[ci]*1))) #This needs to be refined, right now it kinda does the job
                else:
                    compi.setFont(QFont(fontitype,max(int(self.orFonts[ci]*0.9*self.k_font2),10)))
            except Exception as Argument:
                self.genLogforException(Argument)
        try:
            minToolbarWidth_win = int(self.app.activeWindow().geometry().height()*0.03)
            minToolbarWidth_mac = int(self.app.activeWindow().geometry().height()*0.03)
            #print(minToolbarWidth_mac)
            # if platform.system().lower()=='windows':
            #     self.mdynTlb.setMaximumSize(QtCore.QSize(1250, max(int(25*self.k_vert),minToolbarWidth_win) ))
            #     self.mspecTlb.setMaximumSize(QtCore.QSize(1250, max(int(25*self.k_vert),minToolbarWidth_win) ))
            #     self.m2DTlb.setMaximumSize(QtCore.QSize(1250, max(int(25*self.k_vert),minToolbarWidth_win) ))
            # else:
            #     self.mdynTlb.setMaximumSize(QtCore.QSize(1250, max(int(25*self.k_vert),minToolbarWidth_mac) ))
            #     self.mspecTlb.setMaximumSize(QtCore.QSize(1250, max(int(25*self.k_vert),minToolbarWidth_mac) ))
            #     self.m2DTlb.setMaximumSize(QtCore.QSize(1250, max(int(25*self.k_vert),minToolbarWidth_mac) ))
            if platform.system().lower()=='windows':
                self.mdynTlb.setMaximumSize(QtCore.QSize(1250, minToolbarWidth_win ))
                self.mspecTlb.setMaximumSize(QtCore.QSize(1250, minToolbarWidth_win ))
                self.m2DTlb.setMaximumSize(QtCore.QSize(1250, minToolbarWidth_win ))
                self.fitw.fitTlb.setMaximumSize(QtCore.QSize(1250, minToolbarWidth_win ))
                self.fitw.eqTlb.setMaximumSize(QtCore.QSize(1250, minToolbarWidth_win ))
            else:
                self.mdynTlb.setMaximumSize(QtCore.QSize(1250, minToolbarWidth_mac ))
                self.mspecTlb.setMaximumSize(QtCore.QSize(1250, minToolbarWidth_mac ))
                self.m2DTlb.setMaximumSize(QtCore.QSize(1250, minToolbarWidth_mac ))
                self.fitw.fitTlb.setMaximumSize(QtCore.QSize(1250, minToolbarWidth_win ))
                self.fitw.eqTlb.setMaximumSize(QtCore.QSize(1250, minToolbarWidth_win ))
        except Exception as Argument:
            self.genLogforException(Argument)
        self.fontBtn(str(int(9*self.k_font)))
    def getFolderLoc(self):
        try:
            file_dialog = QFileDialog()
            if self.importTypes.checkedAction().text()=='Folders':
                file_dialog.setFileMode(QFileDialog.DirectoryOnly)
                file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
                file_view = file_dialog.findChild(QListView, 'listView')
                if file_view:
                    file_view.setSelectionMode(QAbstractItemView.MultiSelection)
                f_tree_view = file_dialog.findChild(QTreeView)
                if f_tree_view:
                    f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)
                if file_dialog.exec():
                    folderLoc = file_dialog.selectedFiles()
            elif self.importTypes.checkedAction().text()=='Folder':
                options = file_dialog.Options()
                folderLoc = file_dialog.getExistingDirectory(self, "Select Directory",options=options)
            elif self.importTypes.checkedAction().text()=='Files':
                filter=''.join([self.impw.ui.dendwith.currentText(),'(*',self.impw.ui.dendwith.currentText(),')'])
    
                file_dialog.setNameFilters([filter])
                file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
                file_view = file_dialog.findChild(QListView, 'listView')
                if file_view:
                    file_view.setSelectionMode(QAbstractItemView.MultiSelection)
                f_tree_view = file_dialog.findChild(QTreeView)
                if f_tree_view:
                    f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)
                if file_dialog.exec():
                    folderLoc = file_dialog.selectedFiles()
            if not folderLoc=='' and self.importTypes.checkedAction().text()=='Folders':
                for i in range(len(folderLoc)):
                    folderLoc[i]='   -Import preset:'.join([folderLoc[i],self.impw.listprefs.currentText()])
                self.ui.filesLoc.addItems(folderLoc)
                self.ui.filesLoc.setCurrentIndex(self.ui.filesLoc.count()-1)
                
                self.ui.addButton.setEnabled(True)
                self.ui.addallButton.setEnabled(True)
                self.ui.refreshButton.setEnabled(True)
                self.ui.refreshAllButton.setEnabled(True)
                
                self.addoneAction.setEnabled(True)
                self.addallAction.setEnabled(True)
                self.loadAction.setEnabled(True)
            if not folderLoc=='' and self.importTypes.checkedAction().text()=='Files':
                for i in range(len(folderLoc)):
                    folderLoc[i]='   -Import preset:'.join([folderLoc[i],self.impw.listprefs.currentText()])
                self.ui.filesLoc.addItems(folderLoc)
                self.ui.filesLoc.setCurrentIndex(self.ui.filesLoc.count()-1)
                self.ui.addButton.setEnabled(True)
                self.ui.addallButton.setEnabled(True)
                self.ui.refreshButton.setEnabled(True)
                self.ui.refreshAllButton.setEnabled(True)
                
                self.addoneAction.setEnabled(True)
                self.addallAction.setEnabled(True)
                self.loadAction.setEnabled(True)
            elif not folderLoc=='' and self.importTypes.checkedAction().text()=='Folder':
                self.ui.filesLoc.addItem('   -Import preset:'.join([folderLoc,self.impw.listprefs.currentText()]))
                self.ui.filesLoc.setCurrentIndex(self.ui.filesLoc.count()-1)
                self.ui.addButton.setEnabled(True)
                self.ui.addallButton.setEnabled(True)
                self.ui.refreshButton.setEnabled(True)
                self.ui.refreshAllButton.setEnabled(True)
                
                self.addoneAction.setEnabled(True)
                self.ui.addallButton.setEnabled(True)
                self.addallAction.setEnabled(True)
                self.loadAction.setEnabled(True)
            elif self.ui.filesLoc.count()==0:
                self.ui.addButton.setEnabled(False)
                self.addoneAction.setEnabled(False)
                self.ui.addallButton.setEnabled(False)
                self.addallAction.setEnabled(False)
                self.ui.refreshButton.setEnabled(False)
                self.ui.refreshAllButton.setEnabled(False)
                self.loadAction.setEnabled(False)
        except Exception as Argument:
            self.genLogforException(Argument)
    def getGrFolderLoc(self):        
        try:
            file_dialog = QFileDialog()
            folderLoc=''
            if self.ui.addmode.currentText()=='Folders':
                file_dialog.setFileMode(QFileDialog.DirectoryOnly)
                file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
                file_view = file_dialog.findChild(QListView, 'listView')
                if file_view:
                    file_view.setSelectionMode(QAbstractItemView.MultiSelection)
                f_tree_view = file_dialog.findChild(QTreeView)
                if f_tree_view:
                    f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)
                if file_dialog.exec():
                    folderLoc = file_dialog.selectedFiles()
            elif self.ui.addmode.currentText()=='Folder':
                options = file_dialog.Options()
                folderLoc = file_dialog.getExistingDirectory(self, "Select Directory",options=options)
            if not folderLoc=='' and self.ui.addmode.currentText()=='Folders':
                for i in range(len(folderLoc)):
                    folderLoc[i]='   -Import preset:'.join([folderLoc[i],self.impw.listprefs.currentText()])
                self.xyzmaker.ui.GrLoc.addItems(folderLoc)
                self.xyzmaker.ui.GrLoc.setCurrentIndex(self.xyzmaker.ui.GrLoc.count()-1)
                self.xyzmaker.ui.addGrButton.setEnabled(True)
            elif not folderLoc=='' and self.ui.addmode.currentText()=='Folder':
                self.xyzmaker.ui.GrLoc.addItem('   -Import preset:'.join([folderLoc,self.impw.listprefs.currentText()]))
                self.xyzmaker.ui.GrLoc.setCurrentIndex(self.xyzmaker.ui.GrLoc.count()-1)
                self.xyzmaker.ui.addGrButton.setEnabled(True)
            else:
                self.xyzmaker.ui.addGrButton.setEnabled(False)
        except Exception as Argument:
            self.genLogforException(Argument)
    def cleanBtn(self):
        self.ui.dataBox.clear()
        self.ui.filesLoc.clear()
        self.d=dict()
        self.ui.addButton.setEnabled(False)
        self.ui.addallButton.setEnabled(False)
        self.ui.refreshButton.setEnabled(False)
        self.ui.refreshAllButton.setEnabled(False)
        
        self.addoneAction.setEnabled(False)
        self.addallAction.setEnabled(False)
        self.loadAction.setEnabled(False)
        self.plotControlsAction.setChecked(False)
    def cleanGrBtn(self):
        self.xyzmaker.ui.dataGrBox.clear()
        self.xyzmaker.ui.GrLoc.clear()
        self.xyzmaker.ui.xGrList.clear()
        self.xyzmaker.ui.dataGrList.clear()
        self.xyzmaker.ui.dataGenList.clear()
        self.dGr=dict()
        self.dGrtemp=dict()
    def adjustlimits(self,params):
        try:
            if self.impw.ui.xyz.isChecked() and not self.d=={}:
                if params[3]=='min':
                    params[0].setText("{0:.1e}".format(np.nanmin(self.d[self.dataBox.currentText()][params[1]])))
                elif params[3]=='max':
                    params[0].setText("{0:.1e}".format(np.nanmax(self.d[self.dataBox.currentText()][params[1]])))
                #self.ui.xmaxValue.setText("{0:.1e}".format(np.nanmax(self.d[self.dataBox.currentText()]['t'])))
                #self.ui.yminValue.setText("{0:.1e}".format(np.nanmin(self.d[self.dataBox.currentText()]['w'])))
                #self.ui.ymaxValue.setText("{0:.1e}".format(np.nanmax(self.d[self.dataBox.currentText()]['w'])))
            elif not self.impw.ui.xyz.isChecked() and not self.d=={}:
                if params[3]=='min':
                    params[0].setText("{0:.2e}".format(np.nanmin(self.d[self.dataBox.currentText()][params[2]])))
                elif params[3]=='max':
                    params[0].setText("{0:.2e}".format(np.nanmax(self.d[self.dataBox.currentText()][params[2]])))
                #self.ui.xmaxValue.setText("{0:.2e}".format(np.nanmax(self.d[self.dataBox.currentText()]['x'])))
                #self.ui.yminValue.setText("{0:.2e}".format(np.nanmin(self.d[self.dataBox.currentText()]['y'])))
                #self.ui.ymaxValue.setText("{0:.2e}".format(np.nanmax(self.d[self.dataBox.currentText()]['y'])))
        except Exception as Argument:
            self.genLogforException(Argument)
    def refreshBtn(self):
        try:
            self.showPopInfo("Loading files...", durationToShow = 0.5,widgetToShowOn=self.mbar)
            filesloc=self.ui.filesLoc.currentText().split('   -Import preset:')[0]
            filesloc = getResourcePath(filesloc)
            datfoldnames=self.xyzdatagenerator(filesloc)
            data_names=datfoldnames[1]
            fold_names=datfoldnames[2]
            fold_data_names=[]
            if not data_names == []:
                for fi in range(len(data_names)):
                    fold_data_names.append('     /'.join([data_names[fi],fold_names[fi],self.ui.listprefs_main.currentText()]))
                fold_data_names.sort()
                self.ui.dataBox.clear()
                self.ui.dataBox.addItems(fold_data_names)
                if self.importTypes.checkedAction().text()=='Folder' or self.importTypes.checkedAction().text()=='Folders':
                    self.d=datfoldnames[0]
                elif self.importTypes.checkedAction().text()=='Files':
                    self.d=self.xyzdatagenerator(filesloc,addmode='single')[0]
                if self.impw.ui.xyz.isChecked() and not self.d=={}:
                    self.ui.xminValue.setText("{0:.1e}".format(np.nanmin(self.d[self.dataBox.currentText()]['t'])))
                    self.ui.xmaxValue.setText("{0:.1e}".format(np.nanmax(self.d[self.dataBox.currentText()]['t'])))
                    self.ui.yminValue.setText("{0:.1e}".format(np.nanmin(self.d[self.dataBox.currentText()]['w'])))
                    self.ui.ymaxValue.setText("{0:.1e}".format(np.nanmax(self.d[self.dataBox.currentText()]['w'])))
                elif not self.impw.ui.xyz.isChecked() and not self.d=={}:
                    self.ui.xminValue.setText("{0:.2e}".format(np.nanmin(self.d[self.dataBox.currentText()]['x'])))
                    self.ui.xmaxValue.setText("{0:.2e}".format(np.nanmax(self.d[self.dataBox.currentText()]['x'])))
                    self.ui.yminValue.setText("{0:.2e}".format(np.nanmin(self.d[self.dataBox.currentText()]['y'])))
                    self.ui.ymaxValue.setText("{0:.2e}".format(np.nanmax(self.d[self.dataBox.currentText()]['y'])))
                self.plotControlsAction.setChecked(True)
                #self.figHiderShower(self.ui.frame2D, mAction = self.figure2D)
                #self.figHiderShower(self.ui.frameDyn, mAction = self.figureDyn)
                #self.figHiderShower(self.ui.frameSpec, mAction = self.figureSpec)
                # if self.impw.ui.xyz.isChecked():
                #     self.figure2D.setChecked(True)
                #     self.figureDyn.setChecked(True)
                #     self.figureSpec.setChecked(True)
                # else:
                #     self.figureDyn.setChecked(True)
        except Exception as Argument:
            self.genLogforException(Argument)
            self.showPopInfo('Make sure that the data loaded with correct preset! Folder might be empty!',durationToShow=3, color = 'red',widgetToShowOn=self.mbar)
    def addBtn(self):
        try:
            self.showPopInfo("Adding folder...", durationToShow = 0.5,widgetToShowOn=self.mbar)
            # if self.impw.ui.xyz.isChecked():
            #     self.figure2D.setChecked(True)
            #     self.figureDyn.setChecked(True)
            #     self.figureSpec.setChecked(True)
            # else:
            #     self.figureDyn.setChecked(True)
            filesloc=self.ui.filesLoc.currentText().split('   -Import preset:')[0]
            filesloc = getResourcePath(filesloc)
            datfoldnames=self.xyzdatagenerator(filesloc)
            data_names=datfoldnames[1]
            fold_names=datfoldnames[2]
            fold_data_names_temp=[]
            if not data_names == []:
                for fi in range(len(data_names)):
                    fold_data_names_temp.append('     /'.join([data_names[fi],fold_names[fi],self.ui.listprefs_main.currentText()]))
                fold_data_names_temp.sort()
                self.ui.dataBox.addItems(fold_data_names_temp)
                ind=self.ui.dataBox.findText(fold_data_names_temp[0])
                self.ui.dataBox.setCurrentIndex(ind)
                dtemp=datfoldnames[0]
                #self.d=self.d|dtemp this needs newer python version 3.9 or above, use next method instead
                self.d={**self.d, **dtemp}
                # if self.impw.ui.xyz.isChecked() and not self.d=={}:
                #     self.ui.xminValue.setText("{0:.1e}".format(np.nanmin(self.d[self.dataBox.currentText()]['t'])))
                #     self.ui.xmaxValue.setText("{0:.1e}".format(np.nanmax(self.d[self.dataBox.currentText()]['t'])))
                #     self.ui.yminValue.setText("{0:.1e}".format(np.nanmin(self.d[self.dataBox.currentText()]['w'])))
                #     self.ui.ymaxValue.setText("{0:.1e}".format(np.nanmax(self.d[self.dataBox.currentText()]['w'])))
                # elif not self.impw.ui.xyz.isChecked() and not self.d=={}:
                #     self.ui.xminValue.setText("{0:.2e}".format(np.nanmin(self.d[self.dataBox.currentText()]['x'])))
                #     self.ui.xmaxValue.setText("{0:.2e}".format(np.nanmax(self.d[self.dataBox.currentText()]['x'])))
                #     self.ui.yminValue.setText("{0:.2e}".format(np.nanmin(self.d[self.dataBox.currentText()]['y'])))
                #     self.ui.ymaxValue.setText("{0:.2e}".format(np.nanmax(self.d[self.dataBox.currentText()]['y'])))
                self.plotControlsAction.setChecked(True)
        except Exception as Argument:
            self.genLogforException(Argument)
            self.showPopInfo('Make sure that the data added with correct preset!',durationToShow=3, color = 'red',widgetToShowOn=self.mbar)
    def loadallBtn(self):
        self.addallBtn(loadMode = True)
        if self.impw.ui.xyz.isChecked() and not self.d=={}:
            self.ui.xminValue.setText("{0:.1e}".format(np.nanmin(self.d[self.dataBox.currentText()]['t'])))
            self.ui.xmaxValue.setText("{0:.1e}".format(np.nanmax(self.d[self.dataBox.currentText()]['t'])))
            self.ui.yminValue.setText("{0:.1e}".format(np.nanmin(self.d[self.dataBox.currentText()]['w'])))
            self.ui.ymaxValue.setText("{0:.1e}".format(np.nanmax(self.d[self.dataBox.currentText()]['w'])))
        elif not self.impw.ui.xyz.isChecked() and not self.d=={}:
            self.ui.xminValue.setText("{0:.2e}".format(np.nanmin(self.d[self.dataBox.currentText()]['x'])))
            self.ui.xmaxValue.setText("{0:.2e}".format(np.nanmax(self.d[self.dataBox.currentText()]['x'])))
            self.ui.yminValue.setText("{0:.2e}".format(np.nanmin(self.d[self.dataBox.currentText()]['y'])))
            self.ui.ymaxValue.setText("{0:.2e}".format(np.nanmax(self.d[self.dataBox.currentText()]['y'])))
    def addallBtn(self, loadMode=False):
        self.showPopInfo("Adding all folders...", durationToShow = 0.5,widgetToShowOn=self.mbar)
        try:
            # if self.impw.ui.xyz.isChecked():
            #     self.figure2D.setChecked(True)
            #     self.figureDyn.setChecked(True)
            #     self.figureSpec.setChecked(True)
            # else:
            #     self.figureDyn.setChecked(True)
            if loadMode:
                self.ui.dataBox.clear()
                self.d=dict()
            for i in range (self.filesLoc.count()):
                filesloc=self.ui.filesLoc.itemText(i).split('   -Import preset:')[0]
                filesloc = getResourcePath(filesloc)
                datfoldnames=self.xyzdatagenerator(filesloc)
                data_names=datfoldnames[1]
                fold_names=datfoldnames[2]
                fold_data_names_temp=[]
                if not data_names == []:
                    for fi in range(len(data_names)):
                        fold_data_names_temp.append('     /'.join([data_names[fi],fold_names[fi],self.ui.listprefs_main.currentText()]))
                    fold_data_names_temp.sort()
                    self.ui.dataBox.addItems(fold_data_names_temp)
                    dtemp=datfoldnames[0]
                    #self.d=self.d|dtemp this needs newer python version 3.9 or above, use next method instead
                    self.d={**self.d, **dtemp}
            if not fold_data_names_temp == []:
                ind=self.ui.dataBox.findText(fold_data_names_temp[0])
            else:
                ind = 0
            self.ui.dataBox.setCurrentIndex(ind)
            
            # if self.impw.ui.xyz.isChecked() and not self.d=={}:
            #     self.ui.xminValue.setText("{0:.1e}".format(np.nanmin(self.d[self.dataBox.currentText()]['t'])))
            #     self.ui.xmaxValue.setText("{0:.1e}".format(np.nanmax(self.d[self.dataBox.currentText()]['t'])))
            #     self.ui.yminValue.setText("{0:.1e}".format(np.nanmin(self.d[self.dataBox.currentText()]['w'])))
            #     self.ui.ymaxValue.setText("{0:.1e}".format(np.nanmax(self.d[self.dataBox.currentText()]['w'])))
            # elif not self.impw.ui.xyz.isChecked() and not self.d=={}:
            #     self.ui.xminValue.setText("{0:.2e}".format(np.nanmin(self.d[self.dataBox.currentText()]['x'])))
            #     self.ui.xmaxValue.setText("{0:.2e}".format(np.nanmax(self.d[self.dataBox.currentText()]['x'])))
            #     self.ui.yminValue.setText("{0:.2e}".format(np.nanmin(self.d[self.dataBox.currentText()]['y'])))
            #     self.ui.ymaxValue.setText("{0:.2e}".format(np.nanmax(self.d[self.dataBox.currentText()]['y'])))
            self.plotControlsAction.setChecked(True)
        except Exception as Argument:
            self.genLogforException(Argument)
            self.showPopInfo('Make sure that the data added with correct preset!',durationToShow=3, color = 'red',widgetToShowOn=self.mbar)
    def addGrBtn(self):
        try:
            filesloc=self.xyzmaker.ui.GrLoc.currentText().split('   -Import preset:')[0]
            data_names=self.xyzdatagenerator(filesloc)[1]
            fold_names=self.xyzdatagenerator(filesloc)[2]
            fold_data_names_temp=[]
            for fi in range(len(data_names)):
                fold_data_names_temp.append('     /'.join([data_names[fi],fold_names[fi],self.ui.listprefs_main.currentText()]))
            fold_data_names_temp.sort()
            self.xyzmaker.ui.dataGrBox.addItems(fold_data_names_temp)
            self.dGrtemp=self.xyzdatagenerator(filesloc)[0]
            #self.d=self.d|dtemp this needs newer python version 3.9 or above, use next method instead
            self.xyzmaker.ui.dataGrList.addItems(fold_data_names_temp)
            self.dGrtemp={**self.dGrtemp, **self.dGrtemp}
            self.autogenX()
        except Exception as Argument:
            self.genLogforException(Argument)
    def xGraddBtn(self):
        try:
            items = [0]*self.xyzmaker.ui.xGrList.count()
            listy=self.xyzmaker.ui.xGrList
            if not items:
                listy.addItem(self.xyzmaker.ui.xGrValue.text())
                self.xlistGr.insert(0,self.xyzmaker.ui.xGrValue.text())
            elif listy.selectedItems():
                for listitems in listy.selectedItems():
                    listy.insertItem(listy.row(listitems)+1,self.xyzmaker.ui.xGrValue.text())
                    self.xlistGr.insert(listy.row(listitems)+1,self.xyzmaker.ui.xGrValue.text())
            else:
                listy.insertItem(0,self.xyzmaker.ui.xGrValue.text())
                self.xlistGr.insert(0,self.xyzmaker.ui.xGrValue.text())
            self.autogenX()
        except Exception as Argument:
            self.genLogforException(Argument)
    def xGrremBtn(self):
        try:
            listy=self.xyzmaker.ui.xGrList
            if listy.selectedItems():
                for listitems in listy.selectedItems():
                    listy.takeItem(listy.row(listitems))
                    self.xlistGr.pop(listy.row(listitems))
            else:
                listy.takeItem(listy.row(listy.item(0)))
                self.xlistGr.pop(0)
            self.autogenX()
        except Exception as Argument:
            self.genLogforException(Argument)
    def dataExporter(self):
        if self.impw.ui.xyz.isChecked():
            try:
                #Dyn
                noofddyn=(len(self.axdyn.lines)-1)
                lenofx_lines=[]
                for i in range(noofddyn):
                    lenofx_lines.append(len(self.axdyn.lines[i].get_xdata()))
                self.lenofx=max([max(lenofx_lines),100])
                self.csvarray=np.zeros((self.lenofx+2,noofddyn*2),dtype=object)
                self.csvarray[:][:] = np.nan
                for i in range(noofddyn):
                   try:
                       self.csvarray[0][0+2*(i)]=self.legendtext_dyn[i]
                   except Exception as Argument:
                       self.genLogforException(Argument)
                       
                   self.csvarray[0][1+2*(i)]=''
                   self.csvarray[1][0+2*(i)]= self.impw.ui.xlabel.text()
                   self.csvarray[1][1+2*(i)]= self.impw.ui.zlabel.text()
                   self.csvarray[2:len(self.axdyn.lines[i].get_xdata())+2,0+2*(i)]=self.axdyn.lines[i].get_xdata()
                   self.csvarray[2:len(self.axdyn.lines[i].get_ydata())+2,1+2*(i)]=self.axdyn.lines[i].get_ydata()
                presetsDir = self.makeFolderinDocuments('Data')
                dataPath = presetsDir / 'dataxz.csv'
                np.savetxt(dataPath, self.csvarray, delimiter = ",",fmt="%s")
                
                #Spec
                noofdspec=(len(self.axspec.lines)-2)
                lenofx_lines=[]
                for i in range(noofddyn):
                    lenofx_lines.append(len(self.axspec.lines[i].get_xdata()))
                #print(lenofx_lines)
                self.lenofx=max([max(lenofx_lines),100])
                
                #For column data:
                self.csvarray=np.zeros((self.lenofx+2,noofdspec*2),dtype=object)
                self.csvarray[:][:] = np.nan
                for i in range(noofdspec):
                   try:
                       self.csvarray[0][0+2*(i)]=self.legendtext_dyn[i]
                   except Exception as Argument:
                       self.genLogforException(Argument)
                   self.csvarray[0][1+2*(i)]=''
                   self.csvarray[1][0+2*(i)]= self.impw.ui.ylabel.text()
                   self.csvarray[1][1+2*(i)]= self.impw.ui.zlabel.text()
                   self.csvarray[2:len(self.axspec.lines[i].get_xdata())+2,0+2*(i)]=self.axspec.lines[i].get_xdata()
                   self.csvarray[2:len(self.axspec.lines[i].get_ydata())+2,1+2*(i)]=self.axspec.lines[i].get_ydata()
                presetsDir = self.makeFolderinDocuments('Data')
                dataPath = presetsDir / 'datayz.csv'
                self.showPopInfo('Raw data (dataxz.csv and datayz.csv) is succesfully saved in Username/Documents/Graphxyz',widgetToShowOn=self.mbar)
            except Exception as Argument:
                self.genLogforException(Argument)
                self.showPopInfo('Data export failed! Make sure to Submit and Plot first!',durationToShow=3, color = 'red',widgetToShowOn=self.mbar)
        elif not self.impw.ui.xyz.isChecked():
            try:
                if self.ui.graphsel.currentText()=='plot left':
                    noofddyn=(len(self.axdyn.lines)-0)
                    lenofx_lines=[]
                    for i in range(noofddyn):
                        lenofx_lines.append(len(self.axdyn.lines[i].get_xdata()))
                    self.lenofx=max([max(lenofx_lines),100])
                    
                    # For column by column data:
                    self.csvarray=np.zeros((self.lenofx+2,noofddyn*2),dtype=object)
                    self.csvarray[:][:] = np.nan
                    for i in range(noofddyn):
                       self.csvarray[0][0+2*(i)]=self.legendtext_dyn[i]
                       self.csvarray[0][1+2*(i)]=''
                       self.csvarray[1][0+2*(i)]= self.impw.ui.xlabel.text()
                       self.csvarray[1][1+2*(i)]= self.impw.ui.ylabel.text()
                       self.csvarray[2:len(self.axdyn.lines[i].get_xdata())+2,0+2*(i)]=self.axdyn.lines[i].get_xdata()
                       self.csvarray[2:len(self.axdyn.lines[i].get_ydata())+2,1+2*(i)]=self.axdyn.lines[i].get_ydata()
                    presetsDir = self.makeFolderinDocuments('Data')
                    dataPath = presetsDir / 'dataleft.csv'
                    np.savetxt(dataPath, self.csvarray, delimiter = ",",fmt="%s")
                    self.showPopInfo('Raw data (dataleft.csv) is succesfully saved in Username/Documents/Graphxyz',widgetToShowOn=self.mbar)
                if self.ui.graphsel.currentText()=='plot right':
                    noofdspec=(len(self.axspec.lines)-0)
                    lenofx_lines=[]
                    for i in range(noofdspec):
                        lenofx_lines.append(len(self.axspec.lines[i].get_xdata()))
                    self.lenofx=max([max(lenofx_lines),100])
                    self.csvarray=np.zeros((self.lenofx+2,noofdspec*2),dtype=object)
                    self.csvarray[:][:] = np.nan
                    for i in range(noofdspec):
                       self.csvarray[0][0+2*(i)]=self.legendtext_spec[i]
                       self.csvarray[0][1+2*(i)]=''
                       self.csvarray[1][0+2*(i)]= self.impw.ui.xlabel.text()
                       self.csvarray[1][1+2*(i)]= self.impw.ui.ylabel.text()
                       self.csvarray[2:len(self.axspec.lines[i].get_xdata())+2,0+2*(i)]=self.axspec.lines[i].get_xdata()
                       self.csvarray[2:len(self.axspec.lines[i].get_ydata())+2,1+2*(i)]=self.axspec.lines[i].get_ydata()
                    presetsDir = self.makeFolderinDocuments('Data')
                    dataPath = presetsDir / 'dataright.csv'
                    np.savetxt(dataPath, self.csvarray, delimiter = ",",fmt="%s")
                    self.showPopInfo('Raw data (dataright.csv) is succesfully saved in Username/Documents/Graphxyz')
            except Exception as Argument:
                self.genLogforException(Argument)
                self.showPopInfo('Data export failed! Make sure to Submit and Plot first!',durationToShow=3, color = 'red',widgetToShowOn=self.mbar)
    def submitButtonPushed(self, noMessage = False):
        self.legendtext_dyn=[]
        self.legendtext_spec=[]
        self.linespec_all=[]
        self.linedyn_all=[]
        #print(self.app.activeWindow().geometry().width())
        if self.impw.ui.xyz.isChecked():
            self.ui.sliderx.setEnabled(True)
            self.ui.slidery.setEnabled(True)
            self.figure2D.setChecked(True)
            self.figureDyn.setChecked(True)
            self.figureSpec.setChecked(True)
        if self.ui.dataBox.count()==0 and not noMessage:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("Please <FONT COLOR='#800000'>Find</FONT> and <FONT COLOR='#800000'>Load/Add</FONT> the <FONT COLOR='Green'>Data</FONT> before plotting! <br> Make sure you have preset of the correct instrument is set")
            msgBox.setWindowTitle("Warning!")
            msgBox.exec()
        elif self.ui.dataBox.count()!=0:
            if self.impw.ui.xyz.isChecked():
                if self.plotModes.checkedAction().text()=="Selected":
                    try:
                        self.nd=[self.ui.dataBox.currentText()]
                        self.w=[float(self.ui.yValue.text())]
                        self.tr=[float(self.ui.xminValue.text()),float(self.ui.xmaxValue.text())] 
                
                        self.t=[float(self.ui.xValue.text())]
                        self.wr=[float(self.ui.yminValue.text()),float(self.ui.ymaxValue.text())]
                        self.twr=self.tr+self.wr
                        if self.ui.xbgValue.text()!='0':
                            self.tsc=[float(i) for i in self.ui.xbgValue.text().split(',')]
                        else:
                            self.tsc=[0]
                        
                        yold=float(self.ui.yValue.text())
                        xold=float(self.ui.xValue.text())
                        self.ui.sliderx.setMinimum(int(float(self.ui.xminValue.text()))*10)
                        self.ui.sliderx.setMaximum(int(float(self.ui.xmaxValue.text()))*10)
                        self.ui.sliderx.setSingleStep(int(1))
                        
                        if int(float(self.ui.yminValue.text()))*2>int(float(self.ui.ymaxValue.text()))*2:
                            self.ui.slidery.setMinimum(int(float(self.ui.ymaxValue.text()))*2)
                            self.ui.slidery.setMaximum(int(float(self.ui.yminValue.text()))*2)
                        else:
                            self.ui.slidery.setMinimum(int(float(self.ui.yminValue.text()))*2)
                            self.ui.slidery.setMaximum(int(float(self.ui.ymaxValue.text()))*2)
                        self.ui.slidery.setSingleStep(int(1))
                        
                        self.ax2D.clear()
                        self.ax2D.tick_params(direction='in',pad=-25,labelcolor=self.axcolor2D)
                        if not self.optsDynW.holdcb.isChecked():
                            self.axdyn.set_prop_cycle(None)
                            if not self.axdyn.get_legend()==None:
                                self.axdyn.get_legend().remove()
                            if not self.axdyn.get_title()=='':
                                self.axdyn.set_title('')
                            for artist in self.axdyn.lines + self.axdyn.collections:
                                artist.remove()
                        if not self.optsSpecW.holdcb.isChecked():
                            self.axspec.set_prop_cycle(None)
                            if not self.axspec.get_legend()==None:
                                self.axspec.get_legend().remove()
                            if not self.axspec.get_title()=='':
                                self.axspec.set_title('')
                            for artist in self.axspec.lines + self.axspec.collections:
                                artist.remove()
                        
                        #Plot
                        self.sliderx.setValue(int(float(xold*10)))
                        self.slidery.setValue(int(float(yold*2)))
                        self.lineplotdyn=self.plotdyn(multmodex=False,tsc=self.tsc)
                        self.lineplotspec=self.plotspec(multmodex=False,tsc=self.tsc)
                        if not self.ui.darkCheck.isChecked():
                            color3Dtemp='jet'
                        else:
                            color3Dtemp='twilight'
                        self.plotxyz(self.d,0,self.nd,self.t,self.twr,self.fig2D,self.ax2D,color3D=color3Dtemp,tscatter=self.tsc)
                        
                        #Draw to copy background only, will be used to update line position
                        self.line2Dy=self.ax2D.axhline(self.w,ls=':',color='w',alpha=0.35)
                        self.l2Dyrem+=1
                        self.m2D.draw()
                        self.axbackground2Dx=self.m2D.copy_from_bbox(self.ax2D.bbox)
                        self.line2Dy.remove()
                        self.l2Dyrem-=1
                        self.line2Dx=self.ax2D.axvline(self.t,ls=':',color='w',alpha=0.35)
                        self.l2Dxrem+=1
                        self.m2D.draw()
                        self.axbackground2Dy=self.m2D.copy_from_bbox(self.ax2D.bbox)
                        self.line2Dy=self.ax2D.axhline(self.w,ls=':',color='w',alpha=0.35)
                        self.l2Dyrem+=1
                        #Cosmetics
                        self.linedyn=self.axdyn.axvline(self.t,ls=':',color='r',alpha=0.25)
                        self.linespec=self.axspec.axvline(self.w,ls=':',color='r',alpha=0.25)
                        self.linespec0=self.axspec.axhline(0,ls=':',color='orange',alpha=0.5)
                        self.ax2D.margins(x=0)
                        self.axspec.ticklabel_format(axis='y',style='scientific',scilimits=(-2,2))
                        self.axdyn.ticklabel_format(axis='y',style='scientific',scilimits=(-2,2))
                        self.m2D.draw()
                        self.mdyn.draw()
                        self.mspec.draw()
                    except Exception as Argument:
                        self.genLogforException(Argument)
                        self.showPopInfo('Make sure that the data loaded with correct preset!',durationToShow=3, color = 'red',widgetToShowOn=self.mbar)
                #multiple xy mode
                elif self.plotModes.checkedAction().text()=="Single at multiple x and y":
                    if self.ui.dataList.count()==0:
                        msgBox = QMessageBox()
                        msgBox.setIcon(QMessageBox.Information)
                        msgBox.setText("Multiple x and y mode: make sure to add at least one parameter to <FONT COLOR='#800000'> Data List </FONT>. Also add x and y slices")
                        msgBox.setWindowTitle("Warning!")
                        msgBox.exec()
                    try:
                        self.nd=self.getitems(self.ui.dataList)
                        self.w=[float(i) for i in self.getitems(self.ui.yList)]
                        self.tr=[float(self.ui.xminValue.text()),float(self.ui.xmaxValue.text())]
                
                        self.t=[float(i) for i in self.getitems(self.ui.xList)]
                        self.wr=[float(self.ui.yminValue.text()),float(self.ui.ymaxValue.text())]
                        self.twr=np.concatenate((self.tr,self.wr))
                        if self.ui.xbgValue.text()!='0':
                            self.tsc=[float(i) for i in self.ui.xbgValue.text().split(',')]
                        else:
                            self.tsc=[0]
                        
                        self.ui.sliderx.setMinimum(int(float(self.ui.xminValue.text()))*10)
                        self.ui.sliderx.setMaximum(int(float(self.ui.xmaxValue.text()))*10)
                        self.ui.sliderx.setSingleStep(int(1))
                        
                        self.ui.slidery.setMinimum(int(float(self.ui.yminValue.text())*2))
                        self.ui.slidery.setMaximum(int(float(self.ui.ymaxValue.text())*2))
                        self.ui.slidery.setSingleStep(int(1))
                        
                        #Plots
                        if not self.optsDynW.holdcb.isChecked():
                            self.axdyn.set_prop_cycle(None)
                            if not self.axdyn.get_legend()==None:
                                self.axdyn.get_legend().remove()
                            if not self.axdyn.get_title()=='':
                                self.axdyn.set_title('')
                            for artist in self.axdyn.lines + self.axdyn.collections:
                                artist.remove()
                        if not self.optsSpecW.holdcb.isChecked():
                            self.axspec.set_prop_cycle(None)
                            if not self.axspec.get_legend()==None:
                                self.axspec.get_legend().remove()
                            if not self.axspec.get_title()=='':
                                self.axspec.set_title('')
                            for artist in self.axspec.lines + self.axspec.collections:
                                artist.remove()
                        self.lineplotdyn=self.plotdyn(plmd=2.2,tsc=self.tsc)
                        self.lineplotspec=self.plotspec(plmd=1.2,tsc=self.tsc)
                        
                        if not self.ui.darkCheck.isChecked():
                            color3Dtemp='jet'
                        else:
                            color3Dtemp='twilight'
                        self.ax2D.clear()
                        self.plotxyz(self.d,0,[self.ui.dataBox.currentText()],self.t,self.twr,self.fig2D,self.ax2D,color3D=color3Dtemp,tscatter=self.tsc)
                        
                        #Draw to copy background only, will be used to update line position
                        self.line2Dy=self.ax2D.axhline([float(self.ui.yValue.text())],ls=':',color='w',alpha=0.35)
                        self.l2Dyrem+=1
                        self.m2D.draw()
                        self.axbackground2Dx=self.m2D.copy_from_bbox(self.ax2D.bbox)
                        self.line2Dy.remove()
                        self.l2Dyrem-=1
                        self.line2Dx=self.ax2D.axvline([float(self.ui.xValue.text())],ls=':',color='w',alpha=0.35)
                        self.l2Dxrem+=1
                        self.m2D.draw()
                        self.axbackground2Dy=self.m2D.copy_from_bbox(self.ax2D.bbox)
                        self.line2Dy=self.ax2D.axhline([float(self.ui.yValue.text())],ls=':',color='w',alpha=0.35)
                        self.l2Dyrem+=1
                        
                        #Cosmetics
                        try:
                            self.axspec.ticklabel_format(axis='y',style='scientific',scilimits=(-2,2))
                            self.axdyn.ticklabel_format(axis='y',style='scientific',scilimits=(-2,2))
                        except Exception as Argument:
                            self.genLogforException(Argument)
                        self.linedyn=self.axdyn.axvline([float(self.ui.xValue.text())],ls=':',color='r',alpha=0.25)
                        self.linespec=self.axspec.axvline([float(self.ui.yValue.text())],ls=':',color='r',alpha=0.25)
                        self.linespec0=self.axspec.axhline(0,ls=':',color='orange',alpha=0.5)
                        self.m2D.draw()
                        self.mdyn.draw()
                        self.mspec.draw()
                    except Exception as Argument:
                        self.genLogforException(Argument)
                        self.showPopInfo('Make sure that the data loaded with correct preset!',durationToShow=3, color = 'red',widgetToShowOn=self.mbar)
                #multiple d mode
                elif self.plotModes.checkedAction().text()=="Multiple at single x and y":
                    if self.ui.dataList.count()==0:
                        msgBox = QMessageBox()
                        msgBox.setIcon(QMessageBox.Information)
                        msgBox.setText("Multiple data mode: make sure to add at least one parameter to <FONT COLOR='#800000'> Data List </FONT>. Also add x and y slice")
                        msgBox.setWindowTitle("Warning!")
                        msgBox.exec()
                    try:
                        self.nd=self.getitems(self.ui.dataList)
                        self.w=[float(i) for i in self.getitems(self.ui.yList)]
                        self.tr=[float(self.ui.xminValue.text()),float(self.ui.xmaxValue.text())]
                
                        self.t=[float(i) for i in self.getitems(self.ui.xList)]
                        self.wr=[float(self.ui.yminValue.text()),float(self.ui.ymaxValue.text())]
                        self.twr=np.concatenate((self.tr,self.wr))
                        if self.ui.xbgValue.text()!='0':
                            self.tsc=[float(i) for i in self.ui.xbgValue.text().split(',')]
                        else:
                            self.tsc=[0]
                        
                        self.ui.sliderx.setMinimum(int(float(self.ui.xminValue.text())*10))
                        self.ui.sliderx.setMaximum(int(float(self.ui.xmaxValue.text())*10))
                        self.ui.sliderx.setSingleStep(int(1))
                        
                        self.ui.slidery.setMinimum(int(float(self.ui.yminValue.text())*2))
                        self.ui.slidery.setMaximum(int(float(self.ui.ymaxValue.text())*2))
                        self.ui.slidery.setSingleStep(int(1))
                        
                        #Plot
                        if not self.optsDynW.holdcb.isChecked():
                            self.axdyn.set_prop_cycle(None)
                            if not self.axdyn.get_legend()==None:
                                self.axdyn.get_legend().remove()
                            if not self.axdyn.get_title()=='':
                                self.axdyn.set_title('')
                            for artist in self.axdyn.lines + self.axdyn.collections:
                                artist.remove()
                        if not self.optsSpecW.holdcb.isChecked():
                            self.axspec.set_prop_cycle(None)
                            if not self.axspec.get_legend()==None:
                                self.axspec.get_legend().remove()
                            if not self.axspec.get_title()=='':
                                self.axspec.set_title('')
                            for artist in self.axspec.lines + self.axspec.collections:
                                artist.remove()
                        self.lineplotdyn=self.plotdyn(plmd=2,tsc=self.tsc)
                        self.lineplotspec=self.plotspec(plmd=1,tsc=self.tsc)
                        
                        if not self.ui.darkCheck.isChecked():
                            color3Dtemp='jet'
                        else:
                            color3Dtemp='twilight'
                        self.ax2D.clear()
                        self.plotxyz(self.d,0,[self.ui.dataBox.currentText()],self.t,self.twr,self.fig2D,self.ax2D,color3D=color3Dtemp,tscatter=self.tsc)
                        
                        #Draw to copy background only, will be used to update line position
                        self.line2Dy=self.ax2D.axhline([float(self.ui.yValue.text())],ls=':',color='w',alpha=0.35)
                        self.l2Dyrem+=1
                        self.m2D.draw()
                        self.axbackground2Dx=self.m2D.copy_from_bbox(self.ax2D.bbox)
                        self.line2Dy.remove()
                        self.l2Dyrem-=1
                        self.line2Dx=self.ax2D.axvline([float(self.ui.xValue.text())],ls=':',color='w',alpha=0.35)
                        self.l2Dxrem+=1
                        self.m2D.draw()
                        self.axbackground2Dy=self.m2D.copy_from_bbox(self.ax2D.bbox)
                        self.line2Dy=self.ax2D.axhline([float(self.ui.yValue.text())],ls=':',color='w',alpha=0.35)
                        self.l2Dyrem+=1
                        
                        #Cosmetics
                        self.axspec.ticklabel_format(axis='y',style='scientific',scilimits=(-2,2))
                        self.axdyn.ticklabel_format(axis='y',style='scientific',scilimits=(-2,2))
                        self.linedyn=self.axdyn.axvline([float(self.ui.xValue.text())],ls=':',color='r',alpha=0.25)
                        self.linespec=self.axspec.axvline([float(self.ui.yValue.text())],ls=':',color='r',alpha=0.25)
                        self.linespec0=self.axspec.axhline(0,ls=':',color='orange',alpha=0.5)
                        self.m2D.draw()
                        self.mdyn.draw()
                        self.mspec.draw()
                    except Exception as Argument:
                        self.genLogforException(Argument)
                        self.showPopInfo('Make sure that the data loaded with correct preset!',durationToShow=3, color = 'red',widgetToShowOn=self.mbar)
                #multiple xy and d matched mode
                elif self.plotModes.checkedAction().text()=="Matched with x and y":
                    if self.ui.dataList.count()==0:
                        msgBox = QMessageBox()
                        msgBox.setIcon(QMessageBox.Information)
                        msgBox.setText("Match mode: Make sure equal number of <FONT COLOR='#800000'> Data List </FONT> with x and y slices are added")
                        msgBox.setWindowTitle("Warning!")
                        msgBox.exec()
                    try:
                        self.nd=self.getitems(self.ui.dataList)
                        self.w=[float(i) for i in self.getitems(self.ui.yList)]
                        self.tr=[float(self.ui.xminValue.text()),float(self.ui.xmaxValue.text())] 
                
                        self.t=[float(i) for i in self.getitems(self.ui.xList)]
                        self.wr=[float(self.ui.yminValue.text()),float(self.ui.ymaxValue.text())]
                        self.twr=np.concatenate((self.tr,self.wr))
                        if self.ui.xbgValue.text()!='0':
                            self.tsc=[float(i) for i in self.ui.xbgValue.text().split(',')]
                        else:
                            self.tsc=[0]
                        
                        self.ui.sliderx.setMinimum(int(float(self.ui.xminValue.text()))*10)
                        self.ui.sliderx.setMaximum(int(float(self.ui.xmaxValue.text()))*10)
                        self.ui.sliderx.setSingleStep(int(1))
                        
                        self.ui.slidery.setMinimum(int(float(self.ui.yminValue.text()))*2)
                        self.ui.slidery.setMaximum(int(float(self.ui.ymaxValue.text()))*2)
                        self.ui.slidery.setSingleStep(int(1))
                        #Plot
                        if not self.optsDynW.holdcb.isChecked():
                            self.axdyn.set_prop_cycle(None)
                            if not self.axdyn.get_legend()==None:
                                self.axdyn.get_legend().remove()
                            if not self.axdyn.get_title()=='':
                                self.axdyn.set_title('')
                            for artist in self.axdyn.lines + self.axdyn.collections:
                                artist.remove()
                        if not self.optsSpecW.holdcb.isChecked():
                            self.axspec.set_prop_cycle(None)
                            if not self.axspec.get_legend()==None:
                                self.axspec.get_legend().remove()
                            if not self.axspec.get_title()=='':
                                self.axspec.set_title('')
                            for artist in self.axspec.lines + self.axspec.collections:
                                artist.remove()
                        self.lineplotdyn=self.plotdyn(plmd=2.5,tsc=self.tsc)
                        self.lineplotspec=self.plotspec(plmd=1.5,tsc=self.tsc)
                        
                        if not self.ui.darkCheck.isChecked():
                            color3Dtemp='jet'
                        else:
                            color3Dtemp='twilight'
                        self.ax2D.clear()
                        self.plotxyz(self.d,0,[self.ui.dataBox.currentText()],self.t,self.twr,self.fig2D,self.ax2D,color3D=color3Dtemp,tscatter=self.tsc)
                        
                        self.line2Dy=self.ax2D.axhline([float(self.ui.yValue.text())],ls=':',color='w',alpha=0.35)
                        self.l2Dyrem+=1
                        self.m2D.draw()
                        self.axbackground2Dx=self.m2D.copy_from_bbox(self.ax2D.bbox)
                        self.line2Dy.remove()
                        self.l2Dyrem-=1
                        self.line2Dx=self.ax2D.axvline([float(self.ui.xValue.text())],ls=':',color='w',alpha=0.35)
                        self.l2Dxrem+=1
                        self.m2D.draw()
                        self.axbackground2Dy=self.m2D.copy_from_bbox(self.ax2D.bbox)
                        self.line2Dy=self.ax2D.axhline([float(self.ui.yValue.text())],ls=':',color='w',alpha=0.35)
                        self.l2Dyrem+=1
                        
                        #Cosmetics
                        self.axspec.ticklabel_format(axis='y',style='scientific',scilimits=(-2,2))
                        self.axdyn.ticklabel_format(axis='y',style='scientific',scilimits=(-2,2))
                        self.linedyn=self.axdyn.axvline([float(self.ui.xValue.text())],ls=':',color='r',alpha=0.25)
                        self.linespec=self.axspec.axvline([float(self.ui.yValue.text())],ls=':',color='r',alpha=0.25)
                        self.linespec0=self.axspec.axhline(0,ls=':',color='orange',alpha=0.25)
                        self.mdyn.draw()
                        self.mspec.draw()
                    except Exception as Argument:
                        self.genLogforException(Argument)
                        self.showPopInfo('Make sure that the data loaded with correct preset!',durationToShow=3, color = 'red',widgetToShowOn=self.mbar)
                # try:
                #     #Dyn
                #     noofddyn=(len(self.axdyn.lines)-1)
                #     lenofx_lines=[]
                #     for i in range(noofddyn):
                #         lenofx_lines.append(len(self.axdyn.lines[i].get_xdata()))
                #     self.lenofx=max([max(lenofx_lines),100])
                #     self.csvarray=np.zeros((self.lenofx+2,noofddyn*2),dtype=object)
                #     self.csvarray[:][:] = np.nan
                #     for i in range(noofddyn):
                #        try:
                #            self.csvarray[0][0+2*(i)]=self.legendtext_dyn[i]
                #        except Exception as Argument:
                #            self.genLogforException(Argument)
                           
                #        self.csvarray[0][1+2*(i)]=''
                #        self.csvarray[1][0+2*(i)]= self.impw.ui.xlabel.text()
                #        self.csvarray[1][1+2*(i)]= self.impw.ui.zlabel.text()
                #        self.csvarray[2:len(self.axdyn.lines[i].get_xdata())+2,0+2*(i)]=self.axdyn.lines[i].get_xdata()
                #        self.csvarray[2:len(self.axdyn.lines[i].get_ydata())+2,1+2*(i)]=self.axdyn.lines[i].get_ydata()
                #     presetsDir = self.makeFolderinDocuments('Data')
                #     dataPath = presetsDir / 'dataxz.csv'
                #     np.savetxt(dataPath, self.csvarray, delimiter = ",",fmt="%s")
                    
                #     #Spec
                #     noofdspec=(len(self.axspec.lines)-2)
                #     lenofx_lines=[]
                #     for i in range(noofddyn):
                #         lenofx_lines.append(len(self.axspec.lines[i].get_xdata()))
                #     #print(lenofx_lines)
                #     self.lenofx=max([max(lenofx_lines),100])
                    
                #     #For column data:
                #     self.csvarray=np.zeros((self.lenofx+2,noofdspec*2),dtype=object)
                #     self.csvarray[:][:] = np.nan
                #     for i in range(noofdspec):
                #        try:
                #            self.csvarray[0][0+2*(i)]=self.legendtext_dyn[i]
                #        except Exception as Argument:
                #            self.genLogforException(Argument)
                #        self.csvarray[0][1+2*(i)]=''
                #        self.csvarray[1][0+2*(i)]= self.impw.ui.ylabel.text()
                #        self.csvarray[1][1+2*(i)]= self.impw.ui.zlabel.text()
                #        self.csvarray[2:len(self.axspec.lines[i].get_xdata())+2,0+2*(i)]=self.axspec.lines[i].get_xdata()
                #        self.csvarray[2:len(self.axspec.lines[i].get_ydata())+2,1+2*(i)]=self.axspec.lines[i].get_ydata()
                #     presetsDir = self.makeFolderinDocuments('Data')
                #     dataPath = presetsDir / 'datayz.csv'
                #     np.savetxt(dataPath, self.csvarray, delimiter = ",",fmt="%s")
                #     # msgBox = QMessageBox()
                #     # msgBox.setIcon(QMessageBox.Information)
                #     # msgBox.setText("Data is succesfully saved in Username/Documents/Graphxyz")
                #     # msgBox.setWindowTitle("Warning!")
                #     # msgBox.exec()
                #     #print(uisize)
                #     self.showPopInfo('Raw data (.csv) is succesfully saved in Username/Documents/Graphxyz')
                # except Exception as Argument:
                #     self.genLogforException(Argument)
                #     self.showPopInfo('Make sure that the data loaded with correct preset!',durationToShow=3, color = 'red')
            elif not self.impw.ui.xyz.isChecked():
                if self.plotModes.checkedAction().text()=="Multiple":
                    if self.ui.dataList.count == 0:
                        msgBox = QMessageBox()
                        msgBox.setIcon(QMessageBox.Information)
                        msgBox.setText("Multiple mode: Add files to <FONT COLOR='#800000'> Data List </FONT>")
                        msgBox.setWindowTitle("Warning!")
                        msgBox.exec()
                    self.nd=self.getitems(self.ui.dataList)
                else:
                    self.nd=[self.ui.dataBox.currentText()]
                self.xr=[float(self.ui.xminValue.text()),float(self.ui.xmaxValue.text())] 
        
                self.yr=[float(self.ui.yminValue.text()),float(self.ui.ymaxValue.text())]
                self.xyr=self.xr+self.yr
                try:
                    if self.ui.xbgValue.text()!=0:
                        self.tsc=[float(i) for i in self.ui.xbgValue.text().split(',')]
                    else:
                        self.tsc=[0]
                    if self.ui.graphsel.currentText()=='plot left':
                        if not self.optsDynW.holdcb.isChecked():
                            #This is used to clear axis in order not change the limits, instead of axdyn.clear()
                            self.axdyn.set_prop_cycle(None)
                            if not self.axdyn.get_legend()==None:
                                self.axdyn.get_legend().remove()
                            if not self.axdyn.get_title()=='':
                                self.axdyn.set_title('')
                            for artist in self.axdyn.lines + self.axdyn.collections:
                                artist.remove()
                        self.plotxymode(self.figdyn,self.axdyn,tsc=self.tsc,absmode=self.optsDynW.absz.isChecked())
                        self.mdyn.draw()
                        
                        # #Below line output line by line data:
                        # noofddyn=(len(self.axdyn.lines)-0)
                        # lenofx_lines=[]
                        # for i in range(noofddyn):
                        #     lenofx_lines.append(len(self.axdyn.lines[i].get_xdata()))
                        # self.lenofx=max([max(lenofx_lines),100])
                        
                        # # For column by column data:
                        # self.csvarray=np.zeros((self.lenofx+2,noofddyn*2),dtype=object)
                        # self.csvarray[:][:] = np.nan
                        # for i in range(noofddyn):
                        #    self.csvarray[0][0+2*(i)]=self.legendtext_dyn[i]
                        #    self.csvarray[0][1+2*(i)]=''
                        #    self.csvarray[1][0+2*(i)]= self.impw.ui.xlabel.text()
                        #    self.csvarray[1][1+2*(i)]= self.impw.ui.ylabel.text()
                        #    self.csvarray[2:len(self.axdyn.lines[i].get_xdata())+2,0+2*(i)]=self.axdyn.lines[i].get_xdata()
                        #    self.csvarray[2:len(self.axdyn.lines[i].get_ydata())+2,1+2*(i)]=self.axdyn.lines[i].get_ydata()
                        # presetsDir = self.makeFolderinDocuments('Data')
                        # dataPath = presetsDir / 'dataleft.csv'
                        # np.savetxt(dataPath, self.csvarray, delimiter = ",",fmt="%s")
                        # self.showPopInfo('Raw data (.csv) is succesfully saved in Username/Documents/Graphxyz')
                    if self.ui.graphsel.currentText()=='plot right':
                        if not self.optsSpecW.holdcb.isChecked():
                            self.axspec.set_prop_cycle(None)
                            if not self.axspec.get_legend()==None:
                                self.axspec.get_legend().remove()
                            if not self.axspec.get_title()=='':
                                self.axspec.set_title('')
                            for artist in self.axspec.lines + self.axspec.collections:
                                artist.remove()
                        self.plotxymode(self.figspec,self.axspec,tsc=self.tsc,absmode=self.optsSpecW.absz.isChecked())
                        self.mspec.draw()
                        
                        # #Below code is used to save data afterwards:
                        # noofdspec=(len(self.axspec.lines)-0)
                        # lenofx_lines=[]
                        # for i in range(noofdspec):
                        #     lenofx_lines.append(len(self.axspec.lines[i].get_xdata()))
                        # self.lenofx=max([max(lenofx_lines),100])
                        
                        # #For column data:
                        # self.csvarray=np.zeros((self.lenofx+2,noofdspec*2),dtype=object)
                        # self.csvarray[:][:] = np.nan
                        # for i in range(noofdspec):
                        #    self.csvarray[0][0+2*(i)]=self.legendtext_dyn[i]
                        #    self.csvarray[0][1+2*(i)]=''
                        #    self.csvarray[1][0+2*(i)]= self.impw.ui.xlabel.text()
                        #    self.csvarray[1][1+2*(i)]= self.impw.ui.ylabel.text()
                        #    self.csvarray[2:len(self.axspec.lines[i].get_xdata())+2,0+2*(i)]=self.axspec.lines[i].get_xdata()
                        #    self.csvarray[2:len(self.axspec.lines[i].get_ydata())+2,1+2*(i)]=self.axspec.lines[i].get_ydata()
                        # presetsDir = self.makeFolderinDocuments('Data')
                        # dataPath = presetsDir / 'dataright.csv'
                        # np.savetxt(dataPath, self.csvarray, delimiter = ",",fmt="%s")
                        # self.showPopInfo('Raw data (.csv) is succesfully saved in Username/Documents/Graphxyz')
                except Exception as Argument:
                    self.genLogforException(Argument)
                    self.showPopInfo('Make sure that the data loaded with correct preset!',durationToShow=3, color = 'red',widgetToShowOn=self.mbar)
            if self.ui.refinecb.isChecked():
                self.refineBtn()
            else:
                self.xleftlb='X'
                self.ytoplb='Y'
                self.xtoplb='X'
                self.ztoplb='Z'
                if self.impw.ui.xyz.isChecked():
                    self.yleftlb='Z'
                    self.yrightlb='Z'
                    self.xrightlb='Y'
                else:
                    self.yleftlb='Y'
                    self.yrightlb='Y'
                    self.xrightlb='X'
            self.fitter.setEnabled(True)
      
    def customAxisClear(self, ax):
        ax.set_prop_cycle(None)
        if not ax.get_legend()==None:
            ax.get_legend().remove()
        if not ax.get_title()=='':
            ax.set_title('')
        for artist in ax.lines + ax.collections:
            artist.remove()
    def getarray(self,fromlines):
        noofddyn=(len(fromlines)-0)
        xlenarr=[]
        for lines in fromlines:
            xlenarr.append(len(lines.get_xdata()))
        xlen_dyn=max(xlenarr)
        toarray=np.zeros((noofddyn*2,xlen_dyn))
        toarray[:][:] = np.nan
        for i in range(noofddyn):
            toarray[0+2*(i)][0:len(fromlines[i].get_xdata())]=fromlines[i].get_xdata()
            toarray[1+2*(i)][0:len(fromlines[i].get_ydata())]=fromlines[i].get_ydata()
        return toarray
    def plotdyn(self,plmd=2, multmodex=True,tsc=[0]):
        self.minmaxtd=[]
        line=self.plotxyz(self.d,plmd,self.nd,self.w,self.twr,self.figdyn,self.axdyn,self.ui.markerx.currentText(),multmode=multmodex,tscatter=tsc,showleg=self.ui.legcb.isChecked(),normatx=self.ui.xnormcb.isChecked(),xnorm=float(self.ui.xnormValue.text()),absmode=self.optsDynW.absz.isChecked())
        if self.ui.bgdataCb.isChecked():
            self.plotxyz(self.d,plmd,self.getitems(self.ui.bgdataList),self.w,self.twr,self.figdyn,self.axdyn,self.ui.markerx.currentText(),multmode=multmodex,tscatter=tsc,showleg=self.ui.legcb.isChecked(),normatx=self.ui.xnormcb.isChecked(),xnorm=float(self.ui.xnormValue.text()),absmode=self.optsSpecW.absz.isChecked())
        self.mdyn.figure.tight_layout()
        return line
    def plotspec(self,plmd=1,multmodex=True,tsc=[0]):
        self.minmax=[]
        self.minmaxt=[]
        line=self.plotxyz(self.d,plmd,self.nd,self.t,self.twr,self.figspec,self.axspec,self.ui.markery.currentText(),multmode=multmodex,tscatter=tsc,showleg=self.ui.legcb.isChecked(),normaty=self.ui.ynormcb.isChecked(),ynorm=float(self.ui.ynormValue.text()),absmode=self.optsSpecW.flipz.isChecked())
        if self.ui.bgdataCb.isChecked():
            self.plotxyz(self.d,plmd,self.getitems(self.ui.bgdataList),self.t,self.twr,self.figspec,self.axspec,self.ui.markery.currentText(),multmode=multmodex,tscatter=tsc,showleg=self.ui.legcb.isChecked(),normaty=self.ui.ynormcb.isChecked(),ynorm=float(self.ui.ynormValue.text()),absmode=self.optsSpecW.flipz.isChecked())
        self.mspec.figure.tight_layout()
        return line
    def plotxymode(self,figxy,axxy,absmode,tsc=[0]):
        self.minmax_xy=[]
        line=self.plotxy(self.d,self.nd,self.xyr,figxy,axxy,absmode,self.ui.markerx.currentText(),tscatter=tsc,showleg=self.ui.legcb.isChecked(),normatx=self.ui.xnormcb.isChecked(),xnorm=float(self.ui.xnormValue.text()))
        return line
    def plot2D(self):
        if self.impw.ui.xyz.isChecked():
            self.ax2D.clear()
            self.nd=[self.ui.dataBox.currentText()]
            if not self.ui.darkCheck.isChecked():
                color3Dtemp='jet'
            else:
                color3Dtemp='twilight'
            if hasattr(self, 't'):
                self.plotxyz(self.d,0,self.nd,self.t,self.twr,self.fig2D,self.ax2D,color3D=color3Dtemp,tscatter=self.tsc)
            self.m2D.draw()
        elif not self.impw.ui.xyz.isChecked():
            self.nd=[self.ui.dataBox.currentText()]
    def sliderxvaluechange(self):
        try:
            if self.plotModes.checkedAction().text()=="Selected":
                self.ui.xValue.setText(str(self.ui.sliderx.value()/10))
                tt=[self.ui.sliderx.value()/10]
                
                temp=self.tslice(self.d[self.nd[0]],tt[0])
                wtemp=self.d[self.nd[0]]['w']
                if self.tsc[0]!=0:
                    tempsc=0
                    for ts in self.tsc:
                        tempsc=tempsc+self.tslice(self.d[self.nd[0]],ts)
                    tempsc=tempsc/len(self.tsc)
                    temp=temp-tempsc
                temp=temp[self.v2in(wtemp,self.wr[0]):(self.v2in(wtemp,self.wr[1])+1)]
                if self.optsSpecW.flipz.isChecked():
                    temp=-temp
                ynorm=float(self.ui.ynormValue.text())
                if self.ui.ynormcb.isChecked() and ynorm==0:
                    temp=temp/max(abs(temp))
                elif self.ui.xnormcb.isChecked() and not ynorm==0:
                    temp=temp/temp[self.v2in(tt,ynorm)]
                #298fps but unresponsive:
                
                #self.mspec.draw()
                #self.lineplotspec.set_ydata(temp)
                #plt.pause(0.01)
                #self.axspec.draw_artist(self.axspec.patch)
                #self.axspec.draw_artist(self.lineplotspec)
                #self.mspec.update()
                #self.mspec.flush_events()
                #self.mspec.draw()
                
                self.lineplotspec.set_ydata(temp)
                #self.axspec.set_ylim(min(temp),max(temp)) #you can remove this if you want and adjust ylim with submit
                #15fps:
                #self.axspec.clear()
                #self.plotspec()
                self.linedyn.remove()
                self.linedyn=self.axdyn.axvline(tt,ls=':',color='r')
                self.line2Dx.remove()
                self.l2Dxrem-=1
                self.line2Dx=self.ax2D.axvline(tt,ls=':',color='w')
                self.l2Dxrem+=1
                self.mdyn.draw()
                self.mspec.draw()
                self.draw_blit(self.m2D,self.ax2D,self.line2Dx,self.axbackground2Dx)
            else:
                
                self.ui.xValue.setText(str(self.ui.sliderx.value()/10))
                if 'linedyn' in self.__dict__:
                    self.linedyn.remove()
                self.linedyn=self.axdyn.axvline([self.ui.sliderx.value()/10],ls=':',color='r')
                self.line2Dx.remove()
                self.l2Dxrem-=1
                self.line2Dx=self.ax2D.axvline([self.ui.sliderx.value()/10],ls=':',color='w')
                self.l2Dxrem+=1
                self.mdyn.draw()
                self.mspec.draw()
                self.draw_blit(self.m2D,self.ax2D,self.line2Dx,self.axbackground2Dx)
        except Exception as Argument:
            self.genLogforException(Argument)
    def slideryvaluechange(self):
        try:
            if self.plotModes.checkedAction().text()=="Selected":
                self.ui.yValue.setText(str(self.ui.slidery.value()/2))
                wt=[self.ui.slidery.value()/2]
                
                temp=self.wslice(self.d[self.nd[0]],wt[0])
                ttemp=self.d[self.nd[0]]['t']
                if self.tsc[0]!=0:
                    tempsc=0
                    for ts in self.tsc:
                        tempsc=tempsc+temp[self.v2in(ttemp,ts)]
                    tempsc=tempsc/len(self.tsc)
                    temp=temp-tempsc
                temp=temp[self.v2in(ttemp,self.tr[0]):(self.v2in(ttemp,self.tr[1])+1)]
                #temp=10**(-temp)-1
                if self.optsDynW.absz.isChecked():
                    temp=abs(temp)
                xnorm=float(self.ui.xnormValue.text())
                if self.ui.xnormcb.isChecked() and xnorm==0:
                    temp=temp/max(abs(temp))
                elif self.ui.xnormcb.isChecked() and not xnorm==0:
                    temp=temp/temp[self.v2in(ttemp,xnorm)]
                if 'linespec' in self.__dict__ and 'lineplotdyn' in self.__dict__:
                    self.lineplotdyn.set_ydata(temp)
                    self.linespec.remove()
                    self.linespec=self.axspec.axvline(wt,ls=':',color='r')
                    self.line2Dy.remove()
                    self.l2Dyrem-=1
                    self.line2Dy=self.ax2D.axhline(wt,ls=':',color='w')
                    self.l2Dyrem+=1
                    try:
                        self.axdyn.set_ylim(np.nanmin(temp)-0.05*abs(np.nanmin(temp)),np.nanmax(temp)+0.05*abs(np.nanmax(temp)))
                    except Exception as Argument:
                        # creating/opening a file
                        self.genLogforException()
                    self.mspec.draw()
                    self.mdyn.draw()
                    self.draw_blit(self.m2D,self.ax2D,self.line2Dy,self.axbackground2Dy)
            else:
                
                self.ui.yValue.setText(str(self.ui.slidery.value()/2))
                if 'linespec' in self.__dict__:
                    self.linespec.remove()
                    self.line2Dy.remove()
                    self.l2Dyrem-=1
                self.linespec=self.axspec.axvline([self.ui.slidery.value()/2],ls=':',color='r')
                self.line2Dy=self.ax2D.axhline([self.ui.slidery.value()/2],ls=':',color='w')
                self.l2Dyrem+=1
                self.mspec.draw()
                self.mdyn.draw()
                try:
                    self.draw_blit(self.m2D,self.ax2D,self.line2Dy,self.axbackground2Dy)
                except Exception as Argument:
                    self.genLogforException(Argument)
        except Exception as Argument:
            self.genLogforException(Argument)
    def sliderxvaluereleased(self):
        try:
            self.ui.xValue.setText(str(self.ui.sliderx.value()/10))
            self.t=[float(self.ui.xValue.text())]
            self.linedyn.remove()
            self.linedyn=self.axdyn.axvline([float(self.ui.xValue.text())],ls=':',color='r',alpha=0.25)
            
            self.line2Dx.remove()
            self.l2Dxrem-=1
            self.m2D.draw()
            self.axbackground2Dx=self.m2D.copy_from_bbox(self.ax2D.bbox)
            self.line2Dx=self.ax2D.axvline([float(self.ui.xValue.text())],ls=':',color='w',alpha=0.35)
            self.l2Dxrem+=1
            
            self.line2Dy.remove()
            self.l2Dyrem-=1
            self.m2D.draw()
            self.axbackground2Dy=self.m2D.copy_from_bbox(self.ax2D.bbox)
            self.line2Dy=self.ax2D.axhline([float(self.ui.yValue.text())],ls=':',color='w',alpha=0.35)
            self.l2Dyrem+=1
            
            
            self.line2Dx.remove()
            self.l2Dxrem-=1
            self.line2Dx=self.ax2D.axvline([float(self.ui.xValue.text())],ls=':',color='w',alpha=0.35)
            self.l2Dxrem+=1
            self.m2D.draw()
            self.mdyn.draw()
        except Exception as Argument:
            self.genLogforException(Argument)
    def slideryvaluereleased(self):
        try:
            self.ui.yValue.setText(str(self.ui.slidery.value()/2))
            self.w=[float(self.ui.yValue.text())]
            #self.t=[float(self.ui.xValue.text())]
            self.linespec.remove()
            self.linespec=self.axspec.axvline([float(self.ui.yValue.text())],ls=':',color='r',alpha=0.25)
            
            self.line2Dy.remove()
            self.l2Dyrem-=1
            self.m2D.draw()
            self.axbackground2Dy=self.m2D.copy_from_bbox(self.ax2D.bbox)
            self.line2Dy=self.ax2D.axhline([float(self.ui.yValue.text())],ls=':',color='w',alpha=0.35)
            self.l2Dyrem+=1
            
            self.line2Dx.remove()
            self.l2Dxrem-=1
            self.m2D.draw()
            self.axbackground2Dx=self.m2D.copy_from_bbox(self.ax2D.bbox)
            self.line2Dx=self.ax2D.axvline([float(self.ui.xValue.text())],ls=':',color='w',alpha=0.35)
            self.l2Dxrem+=1
            
            self.line2Dy.remove()
            self.l2Dyrem-=1
            self.line2Dy=self.ax2D.axhline([float(self.ui.yValue.text())],ls=':',color='w',alpha=0.35)
            self.l2Dyrem+=1
            self.m2D.draw()
            self.mspec.draw()
        except Exception as Argument:
            self.genLogforException(Argument)
    def darkChanged(self): #Problematic, needs serious fix
        self.ui.sliderx.setEnabled(False)
        self.ui.slidery.setEnabled(False)
        if  self.ui.darkCheck.isChecked():
            self.contStyleToUse = 'dark_background'
            self.axcolor2D = 'w'
            self.m2D.setParent(None)
            self.mspec.setParent(None)
            self.mdyn.setParent(None)
            self.mdynTlb.setParent(None)
            self.mspecTlb.setParent(None)
            self.m2DTlb.setParent(None)
            
            self.addPlotCanvas(self.contStyleToUse,self.axcolor2D)
            
            if self.impw.ui.xy.isChecked():
                self.ax2D.tick_params(direction='in',pad=-25,labelcolor=self.axcolor2D,left=False,labelleft=False,bottom=False,labelbottom=False)
                self.ax2D.set_ylabel('')
                self.ax2D.set_xlabel('')
                self.c_map_ax.tick_params(left=False,labelleft=False,bottom=False,labelbottom=False)
                self.c_map_ax.set(frame_on=False)
                self.c_map_ax.set_ylabel('',rotation=0)
            elif self.impw.ui.xyz.isChecked():
                self.ax2D.tick_params(direction='in',pad=-25,labelcolor=self.axcolor2D,left=True,labelleft=True,bottom=True,labelbottom=True)
                self.ax2D.set_ylabel(self.ytoplb)
                self.ax2D.set_xlabel(self.xtoplb)
                self.c_map_ax.tick_params(left=True,labelleft=True,bottom=True,labelbottom=True)
                self.c_map_ax.set(frame_on=True)
                self.c_map_ax.set_ylabel(self.ztoplb,rotation=0)
            #self.fitw=fitWindow()
        else:
            self.contStyleToUse = 'default'
            self.axcolor2D = 'k'
            self.m2D.setParent(None)
            self.mspec.setParent(None)
            self.mdyn.setParent(None)
            self.mdynTlb.setParent(None)
            self.mspecTlb.setParent(None)
            self.m2DTlb.setParent(None)
            
            self.addPlotCanvas(self.contStyleToUse,self.axcolor2D)
            
            if self.impw.ui.xy.isChecked():
                self.ax2D.tick_params(direction='in',pad=-25,labelcolor=self.axcolor2D,left=False,labelleft=False,bottom=False,labelbottom=False)
                self.ax2D.set_ylabel('')
                self.ax2D.set_xlabel('')
                self.c_map_ax.tick_params(left=False,labelleft=False,bottom=False,labelbottom=False)
                self.c_map_ax.set(frame_on=False)
                self.c_map_ax.set_ylabel('',rotation=0)
            elif self.impw.ui.xyz.isChecked():
                self.ax2D.tick_params(direction='in',pad=-25,labelcolor=self.axcolor2D,left=True,labelleft=True,bottom=True,labelbottom=True)
                self.ax2D.set_ylabel(self.ytoplb)
                self.ax2D.set_xlabel(self.xtoplb)
                self.c_map_ax.tick_params(left=True,labelleft=True,bottom=True,labelbottom=True)
                self.c_map_ax.set(frame_on=True)
                self.c_map_ax.set_ylabel(self.ztoplb,rotation=0)
            #self.fitw=fitWindow()
        self.submitButtonPushed()

    #These are functions for multiple mode:
    def yaddBtn(self):
        items = [0]*self.ui.yList.count()
        listy=self.ui.yList
        if not items:
            listy.addItem(self.ui.yValue.text())
        elif listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.insertItem(listy.row(listitems)+1,self.ui.yValue.text())
        else:
            listy.insertItem(0,self.ui.yValue.text())
    def yremBtn(self):
        listy=self.ui.yList
        if listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.takeItem(listy.row(listitems))
        else:
            listy.takeItem(listy.row(listy.item(0)))
    def yraddBtn(self):
        items = [0]*self.ui.yrList.count()
        listy=self.ui.yrList
        itemtoadd=','.join([self.ui.yminValue.text(),self.ui.ymaxValue.text()])
        if not items:
            listy.addItem(itemtoadd)
        elif listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.insertItem(listy.row(listitems)+1,itemtoadd)
        else:
            listy.insertItem(0,itemtoadd)
    def yrremBtn(self):
        listy=self.ui.yrList
        if listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.takeItem(listy.row(listitems))
        else:
            listy.takeItem(listy.row(listy.item(0)))
            
    def fxaddBtn(self):
        items = [0]*self.ui.fxList.count()
        listy=self.ui.fxList
        if not items:
            listy.addItem(self.ui.fxyValue.text())
        elif listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.insertItem(listy.row(listitems)+1,self.ui.fxyValue.text())
        else:
            listy.insertItem(0,self.ui.fxyValue.text())
    def fxremBtn(self):
        listy=self.ui.fxList
        if listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.takeItem(listy.row(listitems))
        else:
            listy.takeItem(listy.row(listy.item(0)))
    def fyaddBtn(self):
        items = [0]*self.ui.fyList.count()
        listy=self.ui.fyList
        if not items:
            listy.addItem(self.ui.fxyValue.text())
        elif listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.insertItem(listy.row(listitems)+1,self.ui.fxyValue.text())
        else:
            listy.insertItem(0,self.ui.fxyValue.text())
    def fyremBtn(self):
        listy=self.ui.fyList
        if listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.takeItem(listy.row(listitems))
        else:
            listy.takeItem(listy.row(listy.item(0)))
    def flzaddBtn(self):
        items = [0]*self.ui.flzList.count()
        listy=self.ui.flzList
        if not items:
            listy.addItem(self.ui.flrzValue.text())
        elif listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.insertItem(listy.row(listitems)+1,self.ui.flrzValue.text())
        else:
            listy.insertItem(0,self.ui.flrzValue.text())
    def flzremBtn(self):
        listy=self.ui.flzList
        if listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.takeItem(listy.row(listitems))
        else:
            listy.takeItem(listy.row(listy.item(0)))
    def frzaddBtn(self):
        items = [0]*self.ui.frzList.count()
        listy=self.ui.frzList
        if not items:
            listy.addItem(self.ui.flrzValue.text())
        elif listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.insertItem(listy.row(listitems)+1,self.ui.flrzValue.text())
        else:
            listy.insertItem(0,self.ui.flrzValue.text())
    def frzremBtn(self):
        listy=self.ui.frzList
        if listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.takeItem(listy.row(listitems))
        else:
            listy.takeItem(listy.row(listy.item(0)))
            
    def xaddBtn(self):
        items = [0]*self.ui.xList.count()
        listy=self.ui.xList
        if not items:
            listy.addItem(self.ui.xValue.text())
        elif listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.insertItem(listy.row(listitems)+1,self.ui.xValue.text())
        else:
            listy.insertItem(0,self.ui.xValue.text())
    def xremBtn(self):
        listy=self.ui.xList
        if listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.takeItem(listy.row(listitems))
        else:
            listy.takeItem(listy.row(listy.item(0)))
    def xraddBtn(self):
        items = [0]*self.ui.xrList.count()
        listy=self.ui.xrList
        itemtoadd=','.join([self.ui.xminValue.text(),self.ui.xmaxValue.text()])
        if not items:
            listy.addItem(itemtoadd)
        elif listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.insertItem(listy.row(listitems)+1,itemtoadd)
        else:
            listy.insertItem(0,itemtoadd)
    def xrremBtn(self):
        listy=self.ui.xrList
        if listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.takeItem(listy.row(listitems))
        else:
            listy.takeItem(listy.row(listy.item(0)))
    def dataaddBtn(self):
        items = [0]*self.ui.dataList.count()
        listy=self.ui.dataList
        if not items and not self.ui.dataBox.currentText()=='':
            listy.addItem(self.ui.dataBox.currentText())
        elif listy.selectedItems() and not self.ui.dataBox.currentText()=='':
            for listitems in listy.selectedItems():
                listy.insertItem(listy.row(listitems)+1,self.ui.dataBox.currentText())
        elif not self.ui.dataBox.currentText()=='':
            listy.insertItem(0,self.ui.dataBox.currentText())
    def dataGraddBtn(self):
        items = [0]*self.xyzmaker.ui.dataGrList.count()
        listy=self.xyzmaker.ui.dataGrList
        if not items:
            listy.addItem(self.xyzmaker.ui.dataGrBox.currentText())
        elif listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.insertItem(listy.row(listitems)+1,self.xyzmaker.ui.dataGrBox.currentText())
        else:
            listy.insertItem(0,self.xyzmaker.ui.dataGrBox.currentText())
    def dataremBtn(self):
        listy=self.ui.dataList
        if listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.takeItem(listy.row(listitems))
        else:
            listy.takeItem(listy.row(listy.item(0)))
    def dataGrremBtn(self):
        listy=self.xyzmaker.ui.dataGrList
        if listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.takeItem(listy.row(listitems))
        else:
            listy.takeItem(listy.row(listy.item(0)))
    def bgdataaddBtn(self):
        items = [0]*self.ui.bgdataList.count()
        listy=self.ui.bgdataList
        if not items and not self.ui.dataBox.currentText()=='':
            listy.addItem(self.ui.dataBox.currentText())
        elif listy.selectedItems() and not self.ui.dataBox.currentText()=='':
            for listitems in listy.selectedItems():
                listy.insertItem(listy.row(listitems)+1,self.ui.dataBox.currentText())
        elif not self.ui.dataBox.currentText()=='':
            listy.insertItem(0,self.ui.dataBox.currentText())
    def bgdataaddBtn0(self):
        items = [0]*self.ui.bgdataList.count()
        listy=self.ui.bgdataList
        if not items and not self.ui.bgvalue.text()=='':
            listy.addItem(self.ui.bgvalue.text())
        elif listy.selectedItems() and not self.ui.bgvalue.text()=='':
            for listitems in listy.selectedItems():
                listy.insertItem(listy.row(listitems)+1,self.ui.bgvalue.text())
        elif not self.ui.bgvalue.text()=='':
            listy.insertItem(0,self.ui.bgvalue.text())
    def bgdataremBtn(self):
        listy=self.ui.bgdataList
        if listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.takeItem(listy.row(listitems))
        else:
            listy.takeItem(listy.row(listy.item(0)))
    def xbgaddBtn(self):
        xbgcurrent=self.ui.xbgValue.text()
        xcurrent=self.ui.xValue.text()
        xbgnew=','.join([xbgcurrent,xcurrent])
        self.ui.xbgValue.setText(xbgnew)
    def yaveaddBtn(self):
        yavecurrent=self.ui.yaveValue.text()
        ycurrent=self.ui.yValue.text()
        if yavecurrent=='':
            yavenew=ycurrent
        else:
            yavenew=','.join([yavecurrent,ycurrent])
        self.ui.yaveValue.setText(yavenew)
    def clearLists(self):
        listqlist=[self.ui.dataList,self.ui.bgdataList,self.ui.yList,self.ui.xList,self.ui.yrList,self.ui.xrList,self.ui.fyList,self.ui.fxList,self.ui.flzList,self.ui.frzList]
        for eachlist in listqlist:
            eachlist.clear()
    def getitems(self,listname):
        items = [0]*listname.count()
        if items:
            for i in range(len(items)):
                items[i]=listname.item(i).text()
            return items
        else:
            return items
    def getitemsqc(self,listname):
        items = [0]*listname.count()
        if items:
            for i in range(len(items)):
                items[i]=listname.itemText(i)
            return items
        else:
            return items
    def impOptBtnClicked(self):
        uisize = self.ui.impOptionsBtn.mapToGlobal(QPoint(0, 0))
        self.impw.move(int(uisize.x()-uisize_main.width()*0.05),int(uisize.y())) 
        self.impw.show()
    def funOptBtnClicked(self):
        uisize = self.fitw.ui.fitgraph_fr.mapToGlobal(QPoint(0, 0))
        self.funw.move(int(uisize.x()+self.fitw.ui.fitgraph_fr.geometry().width()/6),int(uisize.y()+self.fitw.ui.fitgraph_fr.geometry().height()/6))
        self.funw.show()
        #self.impw.raise_()
    def xyzmakerClicked(self):
        self.xyzmaker.show()
    def fx(self,fxtext,x):
        def xfun(x):
            return eval(fxtext)
        return xfun(x)
    def flx(self,fxtext,x):
        def xfun(x):
            return eval(fxtext)
        return xfun(x)
    def fy(self,fytext,y):
        def yfun(y):
            return eval(fytext)
        return yfun(y)
    def flz(self,flztext,z):
        def zfun(z):
            return eval(flztext)
        return zfun(z)
    def frz(self,frztext,z):
        def zfun(z):
            return eval(frztext)
        return zfun(z)
    def fly(self,flztext,y):
        def zfun(y):
            return eval(flztext)
        return zfun(y)
    def fry(self,frztext,y):
        def zfun(y):
            return eval(frztext)
        return zfun(y)
    def clrDlgOpendyn(self):
        clxdlg=clrDlg(leftright='Left Figure',uisize=uisize_main,defcolor=self.leftcolor,cListItems=self.leftclist)
        uisize = self.optleft.mapToGlobal(QPoint(0, 0))
        clxdlg.move(int(uisize.x()),int(uisize.y()))
        clxdlg.exec()
        self.leftclist=clxdlg.cListItems
        self.leftcolor=clxdlg.defcolor
    def clrDlgOpenspec(self):
        clxdlg=clrDlg(leftright='Right Figure',uisize=uisize_main,defcolor=self.rightcolor,cListItems=self.rightclist)
        uisize = self.optright.mapToGlobal(QPoint(0, 0))
        clxdlg.move(int(uisize.x()-uisize_main.width()*0.05),int(uisize.y()))
        clxdlg.exec()
        self.rightclist=clxdlg.cListItems
        self.rightcolor=clxdlg.defcolor
    def optsDyn(self):
        uisize = self.optleft.mapToGlobal(QPoint(0, 0))
        self.optsDynW.resize(int(self.geometry().width()/12),int(self.geometry().height()/3.5))
        self.optsDynW.move(int(uisize.x()),int(uisize.y()))
        self.optsDynW.show()
    def optsSpec(self):
        uisize = self.optright.mapToGlobal(QPoint(0, 0))
        self.optsSpecW.resize(int(self.geometry().width()/12),int(self.geometry().height()/3.5))
        self.optsSpecW.move(int(uisize.x()-uisize_main.width()*0.05),int(uisize.y())) #Because this is close to the edge of the monitor, I deviated its position by 5%
        self.optsSpecW.show()
    def opts2D(self):
        uisize = self.opt2D.mapToGlobal(QPoint(0, 0))
        self.opts2DW.resize(int(self.geometry().width()/12),int(self.geometry().height()/3.5))
        self.opts2DW.move(int(uisize.x()-uisize_main.width()*0.075),int(uisize.y())) #Because this is close to the edge of the monitor, I deviated its position by 5%
        self.opts2DW.show()
    def multDataBtn(self):
        uisize = self.ui.dataBox.mapToGlobal(QPoint(0, 0))
        self.multDataChooser.resize(int(self.geometry().width()/3),int(self.geometry().height()/3))
        self.multDataChooser.move(int(uisize.x()-uisize_main.width()*0.05),int(uisize.y())) #Because this is close to the edge of the monitor, I deviated its position by 5%
        self.multDataChooser.list.clear()
        
        for i in range(self.ui.dataBox.count()):
            self.multDataChooser.list.addItem(self.ui.dataBox.itemText(i))
        
        self.multDataChooser.show()
        
        # import importlib.util
        # import sys
        # spec = importlib.util.spec_from_file_location("customPyFuns", "/Users/seyitliyev/Documents/Graphxyz/Python functions/funs_fit.py")
        # pyFuns = importlib.util.module_from_spec(spec)
        # sys.modules["customPyFuns"] = pyFuns
        # spec.loader.exec_module(pyFuns)
        # print(''.join([getmembers(pyFuns, isfunction)[0][0],'(x,p)']))
        # pyFuns.testfun(self.multDataChooser.list)
        
    def multDataAddBtn(self):
        listToAdd = self.multDataChooser.list.selectedItems()
        if not listToAdd==[]:
            for item in listToAdd:
                if not self.ui.dataList.findItems(item.text(), Qt.MatchFixedString | Qt.MatchCaseSensitive):
                    self.ui.dataList.addItem(item.text())
    def multSourceBtn(self):
        uisize = self.ui.filesLoc.mapToGlobal(QPoint(0, 0))
        self.multSourceChooser.resize(int(self.geometry().width()/3),int(self.geometry().height()/3))
        self.multSourceChooser.move(int(uisize.x()-uisize_main.width()*0.05),int(uisize.y())) #Because this is close to the edge of the monitor, I deviated its position by 5%
        self.multSourceChooser.list.clear()
        
        for i in range(self.ui.filesLoc.count()):
            self.multSourceChooser.list.addItem(self.ui.filesLoc.itemText(i))
        
        self.multSourceChooser.show()
    def multSourceRemBtn(self):
        listToRem = self.multSourceChooser.list.selectedItems()
        if not listToRem==[]:
            for item in listToRem:
                self.ui.filesLoc.removeItem(self.ui.filesLoc.findText(item.text()))
            self.multSourceChooser.list.clear()
            
            for i in range(self.ui.filesLoc.count()):
                self.multSourceChooser.list.addItem(self.ui.filesLoc.itemText(i))
        
    def fitBtnClicked(self):
        if self.fitw.ui.ydatabox.currentText()=='yright':
            self.fitw.xdata=self.axspec.lines[0].get_xdata()
            self.fitw.ydata=self.axspec.lines[0].get_ydata()
            marker=self.ui.markery.currentText()
            markerls=self.ui.markerlsy.currentText()
        else:
            self.fitw.xdata=self.axdyn.lines[0].get_xdata()
            self.fitw.ydata=self.axdyn.lines[0].get_ydata()
            marker=self.ui.markerx.currentText()
            markerls=self.ui.markerlsx.currentText()
        self.fitw.axFit.plot(self.fitw.xdata, self.fitw.ydata,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=markerls)
                   
    def modechanged(self):
        if self.impw.ui.xy.isChecked():
            self.ax2D.clear()
            self.optsDynW=optsWindow(leftright='Left Figure',xyzmode=self.impw.ui.xyz.isChecked())
            self.optsSpecW=optsWindow(leftright='Right Figure',xyzmode=self.impw.ui.xyz.isChecked())
            if not self.optsDynW.holdcb.isChecked():
                self.axdyn.clear()
            if not self.optsSpecW.holdcb.isChecked():
                self.axspec.clear()
            self.ax2D.tick_params(direction='in',pad=-25,labelcolor=self.axcolor2D,left=False,labelleft=False,bottom=False,labelbottom=False)
            self.xleftlb='X'
            self.yleftlb='Y'
            self.xrightlb='X'
            self.yrightlb='Y'
            self.xtoplb=''
            self.ytoplb=''
            self.ztoplb=''
            self.c_map_ax.tick_params(left=False,labelleft=False,bottom=False,labelbottom=False)
            self.c_map_ax.set(frame_on=False)
            self.c_map_ax.set_ylabel(self.ztoplb,rotation=0)
            if self.cb2D!='':
                self.cb2D.set_alpha(0)
                self.cb2D.draw_all()
            
            self.axspec.set_xlabel(self.xrightlb)
            self.axspec.set_ylabel(self.yrightlb)
            self.axdyn.set_xlabel(self.xleftlb)
            self.axdyn.set_ylabel(self.yleftlb)
            self.m2D.draw()
            self.mdyn.draw()
            self.mspec.draw()
            self.ui.ylb.setEnabled(False)
            self.ui.yValue.setEnabled(False)
            self.ui.xlb.setEnabled(False)
            self.ui.xValue.setEnabled(False)
            self.ui.ynormlb.setEnabled(False)
            self.ui.ynormValue.setEnabled(False)
            self.ui.ynormcb.setEnabled(False)
            self.ui.sliderx.setEnabled(False)
            self.ui.slidery.setEnabled(False)
            self.ui.yavecb.setEnabled(False)
            self.ui.graphsel.setEnabled(True)
            self.multXY.setEnabled(False)
            self.multXY.setVisible(False)
            self.multD.setText("Multiple")
            self.matchD.setText("Multiple with background")
            self.ui.bgdataCb.setText('Bg. data')
            self.fycb.setText('f(x)')
            self.yaddButton.setEnabled(False)
            self.yremButton.setEnabled(False)
            self.xaddButton.setEnabled(False)
            self.xremButton.setEnabled(False)
            self.ui.xavecb.setEnabled(False)
            self.ui.yrCb.setEnabled(False)
            self.ui.yraddButton.setEnabled(False)
            self.ui.yrremButton.setEnabled(False)
            self.flrzValue.setText('1*y')
            self.fxyValue.setText('1240/x')
            self.flzcb.setText('f(y)')
            self.frzcb.setText('f(y)')
            self.fxyAction.setText("f(x)")
            self.fzAction.setText("f(y)")
            self.ySliceAction.setVisible(False)
            self.xSliceAction.setVisible(False)

            self.figure2D.setChecked(False)
            self.frame2D.setVisible(False)
            
            self.figureDyn.setChecked(True)
            self.frameDyn.setVisible(True)
            
            self.figureSpec.setChecked(True)
            self.frameSpec.setVisible(True)
            
            if self.ui.refinecb.isChecked():
                self.refineBtn()
            else:
                self.xleftlb='X'
                self.ytoplb='Y'
                self.xtoplb='X'
                self.ztoplb='Z'
                if self.impw.ui.xyz.isChecked():
                    self.yleftlb='Z'
                    self.yrightlb='Z'
                    self.xrightlb='Y'
                else:
                    self.yleftlb='Y'
                    self.yrightlb='Y'
                    self.xrightlb='X'
            
        elif self.impw.ui.xyz.isChecked():
            self.optsDynW=optsWindow(leftright='Left Figure',xyzmode=self.impw.ui.xyz.isChecked())
            self.optsSpecW=optsWindow(leftright='Right Figure',xyzmode=self.impw.ui.xyz.isChecked())
            if not self.optsDynW.holdcb.isChecked():
                self.axdyn.clear()
            if not self.optsSpecW.holdcb.isChecked():
                self.axspec.clear()
            self.ax2D.tick_params(direction='in',pad=-25,labelcolor=self.axcolor2D,left=True,labelleft=True,bottom=True,labelbottom=True)
            self.xleftlb='X'
            self.yleftlb='Z'
            self.xrightlb='Y'
            self.yrightlb='Z'
            self.xtoplb='X'
            self.ytoplb='Y'
            self.ztoplb='Z'
            self.c_map_ax.tick_params(left=True,labelleft=True,bottom=True,labelbottom=True)
            self.c_map_ax.set(frame_on=True)
            self.c_map_ax.set_ylabel(self.ztoplb,rotation=0)
            
            self.axspec.set_xlabel(self.xrightlb)
            self.axspec.set_ylabel(self.yrightlb)
            self.axdyn.set_xlabel(self.xleftlb)
            self.axdyn.set_ylabel(self.yleftlb)
            self.ax2D.set_ylabel(self.ytoplb)
            self.ax2D.set_xlabel(self.xtoplb)
            self.ax2D.yaxis.set_label_coords(0.075,0.5)
            self.ax2D.xaxis.set_label_coords(0.5,0.125)
            self.m2D.draw()
            self.mdyn.draw()
            self.mspec.draw()
            self.ui.ylb.setEnabled(True)
            self.ui.yValue.setEnabled(True)
            self.ui.xlb.setEnabled(True)
            self.ui.xValue.setEnabled(True)
            self.ui.yavecb.setEnabled(True)
            self.ui.ynormlb.setEnabled(True)
            self.ui.ynormValue.setEnabled(True)
            self.ui.ynormcb.setEnabled(True)
            self.ui.sliderx.setEnabled(True) 
            self.ui.slidery.setEnabled(True)
            self.ui.graphsel.setEnabled(False)
            self.multXY.setEnabled(True)
            self.multXY.setVisible(True)
            self.multD.setText("Multiple at single x and y")
            self.matchD.setText("Matched with x and y")
            self.ui.bgdataCb.setText('Link')
            self.fycb.setText('f(y)')
            self.fycb.setEnabled(True)
            self.fyaddButton.setEnabled(True)
            self.fyremButton.setEnabled(True)
            self.yaddButton.setEnabled(True)
            self.yremButton.setEnabled(True)
            self.xaddButton.setEnabled(True)
            self.xremButton.setEnabled(True)
            self.ui.xavecb.setEnabled(True)
            self.ui.yrCb.setEnabled(True)
            self.ui.yraddButton.setEnabled(True)
            self.ui.yrremButton.setEnabled(True)
            self.flrzValue.setText('1*z')
            self.fxyValue.setText('x-0.1')
            self.flzcb.setText('f(z)')
            self.frzcb.setText('f(z)')
            self.fxyAction.setText("f(x) and f(y)")
            self.fzAction.setText("f(z)")
            self.ySliceAction.setVisible(True)
            self.xSliceAction.setVisible(True)
            
            #self.ySliceAction.setEnabled(True)
            #self.xSliceAction.setEnabled(True)
            
            self.figure2D.setChecked(True)
            self.frame2D.setVisible(True)
            
            self.figureDyn.setChecked(True)
            self.frameDyn.setVisible(True)
            
            self.figureSpec.setChecked(True)
            self.frameSpec.setVisible(True)
            if self.ui.refinecb.isChecked():
                self.refineBtn()
            else:
                self.xleftlb='X'
                self.ytoplb='Y'
                self.xtoplb='X'
                self.ztoplb='Z'
                if self.impw.ui.xyz.isChecked():
                    self.yleftlb='Z'
                    self.yrightlb='Z'
                    self.xrightlb='Y'
                else:
                    self.yleftlb='Y'
                    self.yrightlb='Y'
                    self.xrightlb='X'
    def modeChangeLabels(self):
        if self.impw.ui.xy.isChecked():
            self.optsDynW=optsWindow(leftright='Left Figure',xyzmode=self.impw.ui.xy.isChecked())
            self.optsSpecW=optsWindow(leftright='Right Figure',xyzmode=self.impw.ui.xy.isChecked())
            if not self.optsDynW.holdcb.isChecked():
                self.axdyn.clear()
            if not self.optsSpecW.holdcb.isChecked():
                self.axspec.clear()
            self.ax2D.tick_params(direction='in',pad=-25,labelcolor=self.axcolor2D,left=False,labelleft=False,bottom=False,labelbottom=False)
            self.xleftlb='X'
            self.yleftlb='Y'
            self.xrightlb='X'
            self.yrightlb='Y'
            self.xtoplb=''
            self.ytoplb=''
            self.ztoplb=''
            self.c_map_ax.tick_params(left=False,labelleft=False,bottom=False,labelbottom=False)
            self.c_map_ax.set(frame_on=False)
            self.c_map_ax.set_ylabel(self.ztoplb,rotation=0)
            if self.cb2D!='':
                self.cb2D.set_alpha(0)
                self.cb2D.draw_all()
            
            self.axspec.set_xlabel(self.xrightlb)
            self.axspec.set_ylabel(self.yrightlb)
            self.axdyn.set_xlabel(self.xleftlb)
            self.axdyn.set_ylabel(self.yleftlb)
            self.m2D.draw()
            self.mdyn.draw()
            self.mspec.draw()
            self.ui.ylb.setEnabled(False)
            self.ui.yValue.setEnabled(False)
            self.ui.xlb.setEnabled(False)
            self.ui.xValue.setEnabled(False)
            self.ui.ynormlb.setEnabled(False)
            self.ui.ynormValue.setEnabled(False)
            self.ui.ynormcb.setEnabled(False)
            self.ui.sliderx.setEnabled(False)
            self.ui.slidery.setEnabled(False)
            self.ui.yavecb.setEnabled(False)
            self.ui.graphsel.setEnabled(True)
            self.multXY.setEnabled(False)
            self.multXY.setVisible(False)
            self.multD.setText("Multiple")
            self.matchD.setText("Multiple with background")
            self.ui.bgdataCb.setText('Bg. data')
            self.fycb.setText('f(x)')
            self.yaddButton.setEnabled(False)
            self.yremButton.setEnabled(False)
            self.xaddButton.setEnabled(False)
            self.xremButton.setEnabled(False)
            self.ui.xavecb.setEnabled(False)
            self.ui.yrCb.setEnabled(False)
            self.ui.yraddButton.setEnabled(False)
            self.ui.yrremButton.setEnabled(False)
            self.flrzValue.setText('1*y')
            self.fxyValue.setText('1240/x')
            self.flzcb.setText('f(y)')
            self.frzcb.setText('f(y)')
            
            #self.ySliceAction.setEnabled(False)
            #self.xSliceAction.setEnable(False)
            
            if self.ui.refinecb.isChecked():
                self.refineBtn()
            else:
                self.xleftlb='X'
                self.ytoplb='Y'
                self.xtoplb='X'
                self.ztoplb='Z'
                if self.impw.ui.xyz.isChecked():
                    self.yleftlb='Z'
                    self.yrightlb='Z'
                    self.xrightlb='Y'
                else:
                    self.yleftlb='Y'
                    self.yrightlb='Y'
                    self.xrightlb='X'
            
        elif self.impw.ui.xyz.isChecked():
            self.ax2D.clear()
            self.optsDynW=optsWindow(leftright='Left Figure',xyzmode=self.impw.ui.xyz.isChecked())
            self.optsSpecW=optsWindow(leftright='Right Figure',xyzmode=self.impw.ui.xyz.isChecked())
            if not self.optsDynW.holdcb.isChecked():
                self.axdyn.clear()
            if not self.optsSpecW.holdcb.isChecked():
                self.axspec.clear()
            self.ax2D.tick_params(direction='in',pad=-25,labelcolor=self.axcolor2D,left=True,labelleft=True,bottom=True,labelbottom=True)
            self.xleftlb='X'
            self.yleftlb='Z'
            self.xrightlb='Y'
            self.yrightlb='Z'
            self.xtoplb='X'
            self.ytoplb='Y'
            self.ztoplb='Z'
            self.c_map_ax.tick_params(left=True,labelleft=True,bottom=True,labelbottom=True)
            self.c_map_ax.set(frame_on=True)
            self.c_map_ax.set_ylabel(self.ztoplb,rotation=0)
            
            self.axspec.set_xlabel(self.xrightlb)
            self.axspec.set_ylabel(self.yrightlb)
            self.axdyn.set_xlabel(self.xleftlb)
            self.axdyn.set_ylabel(self.yleftlb)
            self.ax2D.set_ylabel(self.ytoplb)
            self.ax2D.set_xlabel(self.xtoplb)
            self.ax2D.yaxis.set_label_coords(0.075,0.5)
            self.ax2D.xaxis.set_label_coords(0.5,0.125)
            self.m2D.draw()
            self.mdyn.draw()
            self.mspec.draw()
            self.ui.ylb.setEnabled(True)
            self.ui.yValue.setEnabled(True)
            self.ui.xlb.setEnabled(True)
            self.ui.xValue.setEnabled(True)
            self.ui.yavecb.setEnabled(True)
            self.ui.ynormlb.setEnabled(True)
            self.ui.ynormValue.setEnabled(True)
            self.ui.ynormcb.setEnabled(True)
            self.ui.sliderx.setEnabled(True) 
            self.ui.slidery.setEnabled(True)
            self.ui.graphsel.setEnabled(False)
            self.multXY.setEnabled(True)
            self.multXY.setVisible(True)
            self.multD.setText("Multiple at single x and y")
            self.matchD.setText("Matched with x and y")
            self.ui.bgdataCb.setText('Link')
            self.fycb.setText('f(y)')
            self.fycb.setEnabled(True)
            self.fyaddButton.setEnabled(True)
            self.fyremButton.setEnabled(True)
            self.yaddButton.setEnabled(True)
            self.yremButton.setEnabled(True)
            self.xaddButton.setEnabled(True)
            self.xremButton.setEnabled(True)
            self.ui.xavecb.setEnabled(True)
            self.ui.yrCb.setEnabled(True)
            self.ui.yraddButton.setEnabled(True)
            self.ui.yrremButton.setEnabled(True)
            self.flrzValue.setText('1*z')
            self.fxyValue.setText('x-0.1')
            self.flzcb.setText('f(z)')
            self.frzcb.setText('f(z)')
            if self.ui.refinecb.isChecked():
                self.refineBtn()
            else:
                self.xleftlb='X'
                self.ytoplb='Y'
                self.xtoplb='X'
                self.ztoplb='Z'
                if self.impw.ui.xyz.isChecked():
                    self.yleftlb='Z'
                    self.yrightlb='Z'
                    self.xrightlb='Y'
                else:
                    self.yleftlb='Y'
                    self.yrightlb='Y'
                    self.xrightlb='X'
    def modechangedMain(self):
        if self.impw.ui.xyz.isChecked():
            self.impw.ui.xyz.setChecked(True)
        elif self.impw.ui.xy.isChecked():
            self.impw.ui.xy.setChecked(True)
    def selectimpBtn(self):
        filter="txt(*.txt)"
        prfilename = QFileDialog.getOpenFileName(self,None, "Select Preset File",filter)
        self.impw.ui.presetloc.setText(prfilename[0])
        if not prfilename[0]=='':
            self.impw_list=np.loadtxt(prfilename[0], delimiter = " ",dtype=str).tolist()
            if self.impw_list==[]:
                prnames=[]
            else:
                prnames=self.impw_list[0].split(',')
                prnames.sort()
            self.impw.ui.listprefs.clear()
            self.ui.listprefs_main.clear()
            self.impw.ui.listprefs.addItems(prnames)
            self.ui.listprefs_main.addItems(prnames)
            self.prefimp()
            self.prefimp_main()
    def selectfunBtn(self):
        filter="txt(*.txt)"
        funfilename = QFileDialog.getOpenFileName(self,None, "Select Functions File",filter)
        self.funw.ui.funloc.setText(funfilename[0])
        if not funfilename[0]=='':
            self.funw_list=np.loadtxt(funfilename[0], delimiter = " ",dtype=str).tolist()
            if self.funw_list==[]:
                funnames=[]
            else:
                funnames=self.funw_list[0].split(',/')
                funnames.sort()
            self.funw.ui.listfuns.clear()
            self.fitw.ui.listfuns_main.clear()
            self.funw.ui.listfuns.addItems(funnames)
            self.fitw.ui.listfuns_main.addItems(funnames)
            self.funimp()
            self.funimp_main()
            self.funw_list[-2]=self.funw.ui.pyfileloc.text()
    def selectPrefSampleBtn(self):
        try:
            filter=''.join([self.impw.ui.dendwith.currentText(),'(*',self.impw.ui.dendwith.currentText(),')'])
            self.filelocPreview = QFileDialog.getOpenFileName(self,None, "Select Data to Preview",filter)
            self.impw.ui.sfileloc.setText(self.filelocPreview[0])
            self.impw.show()
        except Exception as Argument:
            self.genLogforException(Argument)
            self.impw.show()
    def execPyFuns(self):
        try:
            #This is the way to import external python functions to fit:
            pyPath = self.funw.ui.pyfileloc.text()
            spec = importlib.util.spec_from_file_location("customPyFuns", pyPath)
            pyF = importlib.util.module_from_spec(spec)
            sys.modules["customPyFuns"] = pyF
            spec.loader.exec_module(pyF)
            return pyF
        except Exception as Argument:
            self.genLogforException(Argument)
    def viewPyFuns(self):
        try:
            pyF = self.execPyFuns()
            allmembers = getmembers(pyF, isfunction)
            self.pyFunsDlg.funsList.clear()
            self.pyFunsDlg.parsList.clear()
            for i in range(len(allmembers)):
                lbtext = ''.join(['pyF.',allmembers[i][0],'(x,p)'])
                self.pyFunsDlg.funsList.addItem(lbtext)
                self.pyFunsDlg.parsList.addItem('?')
            
            #Make parameters ediatable:
            for index in range(self.pyFunsDlg.parsList.count()):
                item = self.pyFunsDlg.parsList.item(index)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
                
            self.pyFunsDlg.show()
        except Exception as Argument:
            self.genLogforException(Argument)
    def addPyFuns(self):
        for i in range(self.pyFunsDlg.funsList.count()):
            del self.funw_list[-1]
            del self.funw_list[-1]
            #print(self.funw.ui.listfuns.findText('test')==-1)
            if self.funw.ui.listfuns.findText(self.pyFunsDlg.funsList.item(i).text()[4:])==-1:
                self.funw.ui.listfuns.addItem(self.pyFunsDlg.funsList.item(i).text()[4:])
                self.fitw.ui.listfuns_main.addItem(self.pyFunsDlg.funsList.item(i).text()[4:])
                newfun=self.pyFunsDlg.funsList.item(i).text()
                newfun=',/'.join([newfun,self.pyFunsDlg.parsList.item(i).text()])
                self.funw_list.append(newfun)
                self.funw_list[0]=',/'.join([self.funw_list[0],self.pyFunsDlg.funsList.item(i).text()[4:]])
            self.funw_list.append(self.funw.ui.pyfileloc.text())
            self.funw_list.append(self.funw.ui.listfuns.currentText())
    
    def selectPyBtn(self):
        try:
            filter="py(*.py)"
            filelocPreview = QFileDialog.getOpenFileName(self,None, "Select python file",filter)
            self.funw.ui.pyfileloc.setText(filelocPreview[0])
            self.funw.show()
        except Exception as Argument:
            self.genLogforException(Argument)
            self.funw.show()
    
    def showPreviewDf(self):
        try:
            self.impw.df=self.xyzdatagenerator(self.filelocPreview[0],addmode='single')[3][0]
            model = pandasModel(self.impw.df)
            self.view.setModel(model)
            self.view.resize(800, 600)
            self.dfPrevDlg.show()
        except Exception as Argument:
            self.genLogforException(Argument)
        
    def loadDefimpBtn(self):
        #DataDir = getResourcePath("prs")
        DataDir = self.makeFolderinDocuments('Instrument Presets')
        prPath = DataDir / 'presets_default.txt'
        self.impw.ui.presetloc.setText(str(prPath))
        self.impw_list=np.loadtxt(prPath, delimiter = " ",dtype=str).tolist()
        if self.impw_list==[]:
            prnames=[]
        else:
            prnames=self.impw_list[0].split(',')
            prnames.sort()
        self.impw.ui.listprefs.clear()
        self.ui.listprefs_main.clear()
        self.impw.ui.listprefs.addItems(prnames)
        self.ui.listprefs_main.addItems(prnames)
        try:
            self.defPreset = self.impw_list[-1]
        except Exception as Argument:
            self.defPreset = 'XY-column'
            self.genLogforException(Argument)
        self.prefimp()
        self.prefimp_main()
    def loadDeffunBtn(self):
        #DataDir = getResourcePath("prs")
        DataDir = self.makeFolderinDocuments('Functions')
        funPath = DataDir / 'functions_default.txt'
        self.funw.ui.funloc.setText(str(funPath))
        self.funw_list=np.loadtxt(funPath, delimiter = " ",dtype=str).tolist()
        if self.funw_list==[]:
            funnames=[]
        else:
            funnames=self.funw_list[0].split(',/')
            funnames.sort()
        self.funw.ui.listfuns.clear()
        self.fitw.ui.listfuns_main.clear()
        self.funw.ui.listfuns.addItems(funnames)
        self.fitw.ui.listfuns_main.addItems(funnames)
        try:
            self.defFunction = self.funw_list[-1]
        except Exception as Argument:
            self.defFunction = 'Linear'
            self.genLogforException(Argument)
        self.funimp()
        self.funimp_main()
        self.funw.ui.pyfileloc.setText(self.funw_list[-2])
    def loadIntimpBtn(self):
        DataDir = getResourcePath("prs")
        #DataDir = self.makeFolderinDocuments('Instrument Presets')
        prPath = DataDir / 'presets_default.txt'
        self.impw.ui.presetloc.setText('presets_default.txt')
        self.impw_list=np.loadtxt(prPath, delimiter = " ",dtype=str).tolist()
        if self.impw_list==[]:
            prnames=[]
        else:
            prnames=self.impw_list[0].split(',')
            prnames.sort()
        self.impw.ui.listprefs.clear()
        self.ui.listprefs_main.clear()
        self.impw.ui.listprefs.addItems(prnames)
        self.ui.listprefs_main.addItems(prnames)
        try:
            self.defPreset = self.impw_list[-1]
        except Exception as Argument:
            self.defPreset = 'XY-column'
            self.genLogforException(Argument)
        self.prefimp()
        self.prefimp_main()
    def loadIntfunBtn(self):
        DataDir = getResourcePath("funs")
        #DataDir = self.makeFolderinDocuments('Instrument Presets')
        funPath = DataDir / 'functions_default.txt'
        self.funw.ui.funloc.setText('functions_default.txt')
        self.funw_list=np.loadtxt(funPath, delimiter = " ",dtype=str).tolist()
        #print(self.funw_list)
        if self.funw_list==[]:
            funnames=[]
        else:
            funnames=self.funw_list[0].split(',/')
            funnames.sort()
        self.funw.ui.listfuns.clear()
        self.fitw.ui.listfuns_main.clear()
        self.funw.ui.listfuns.addItems(funnames)
        self.fitw.ui.listfuns_main.addItems(funnames)
        try:
            self.defFunction = self.funw_list[-1]
        except Exception as Argument:
            self.defFunction = 'Linear'
            self.genLogforException(Argument)
        self.funimp()
        self.funimp_main()
        self.funw.ui.pyfileloc.setText(self.funw_list[-2])
    def loadimpBtn(self):
        try:
            #DataDir = getResourcePath("prs")
            #DataDir = self.makeFolderinDocuments('Instrument Presets')
            #prPath = DataDir / 'presets_default.txt'
            prPath = self.impw.ui.presetloc.text()
            self.impw_list=np.loadtxt(prPath, delimiter = " ",dtype=str).tolist()
            if self.impw_list==[]:
                prnames=[]
            else:
                prnames=self.impw_list[0].split(',')
                prnames.sort()
            self.impw.ui.listprefs.clear()
            self.ui.listprefs_main.clear()
            self.impw.ui.listprefs.addItems(prnames)
            self.ui.listprefs_main.addItems(prnames)
            try:
                self.defPreset = self.impw_list[-1]
            except Exception as Argument:
                self.defPreset = 'XY-column'
                self.genLogforException(Argument)
            self.prefimp()
            self.prefimp_main()
        except Exception as Argument:
            self.genLogforException(Argument)
            self.loadIntimpBtn()
            self.showPopInfo('Select preset location',color = 'red',widgetToShowOn=self.mbar)
    def loadfunBtn(self):
        try:
            #DataDir = getResourcePath("prs")
            #DataDir = self.makeFolderinDocuments('Instrument Presets')
            #prPath = DataDir / 'presets_default.txt'
            funPath = self.funw.ui.funloc.text()
            self.funw_list=np.loadtxt(funPath, delimiter = " ",dtype=str).tolist()
            if self.funw_list==[]:
                funnames=[]
            else:
                funnames=self.funw_list[0].split(',/')
                funnames.sort()
            self.funw.ui.listfuns.clear()
            self.fitw.ui.listfuns_main.clear()
            self.funw.ui.listfuns.addItems(funnames)
            self.fitw.ui.listfuns_main.addItems(funnames)
            try:
                self.defFunction = self.funw_list[-1]
            except Exception as Argument:
                self.defFunction = 'Linear'
                self.genLogforException(Argument)
            self.funimp()
            self.funimp_main()
            self.funw.ui.pyfileloc.setText(self.funw_list[-2])
        except Exception as Argument:
            self.genLogforException(Argument)
            self.loadIntfunBtn()
            self.showPopInfo('Select functions location',color = 'red',widgetToShowOn=self.mbar)
    def prefimp_main(self):
        ind=self.impw.ui.listprefs.findText(self.ui.listprefs_main.currentText())
        self.impw.ui.listprefs.setCurrentIndex(ind)
        try:
            self.prefimp()
        except Exception as Argument:
            self.genLogforException(Argument)
    def funimp_main(self):
        ind=self.funw.ui.listfuns.findText(self.fitw.ui.listfuns_main.currentText())
        self.funw.ui.listfuns.setCurrentIndex(ind)
        self.fitw.ui.fValueEdit.setText(self.funw.ui.funText.text())
        try:
            self.funimp()
        except Exception as Argument:
            self.genLogforException(Argument)
        
    def dataBoxActivated(self):
        try:
            ind = self.ui.listprefs_main.findText(self.ui.dataBox.currentText().split('     /')[-1])
            self.ui.listprefs_main.setCurrentIndex(ind)
            self.prefimp_main()
            if self.impw.ui.xyz.isChecked():
                self.ax2D.clear()
                self.nd=[self.ui.dataBox.currentText()]
                if not self.ui.darkCheck.isChecked():
                    color3Dtemp='jet'
                else:
                    color3Dtemp='twilight'
                if hasattr(self, 't'):
                    self.plotxyz(self.d,0,self.nd,self.t,self.twr,self.fig2D,self.ax2D,color3D=color3Dtemp,tscatter=self.tsc)
                self.m2D.draw()
            elif not self.impw.ui.xyz.isChecked():
                self.nd=[self.ui.dataBox.currentText()]
        except Exception as Argument:
            self.genLogforException(Argument)
            #self.showPopInfo('Make sure that the data loaded with correct preset!',durationToShow=4, color = 'red')
        #self.nd = 
    def prefimp(self):
        if self.impw_list == []:
            temparr=[]
        else:
            prnames=self.impw_list[0].split(',')
            indt=prnames.index(self.impw.listprefs.currentText())
            ind=self.ui.listprefs_main.findText(self.impw.ui.listprefs.currentText())
            self.ui.listprefs_main.setCurrentIndex(ind)
            temparr=self.impw_list[indt+1].split(',')
        for i in range(len(temparr)):
            if i==0 and temparr[i]=='row':
                self.impw.ui.xrowcb.setChecked(True)
            elif i==0 and temparr[i]=='col':
                self.impw.ui.xcolcb.setChecked(True)
            elif i==0 and temparr[i]=='none':
                self.impw.ui.xnonecb.setChecked(True)
                
            elif i==1:
                self.impw.ui.rowXst.setText(temparr[i])
                
            elif i==2:
                self.impw.ui.colXst.setText(temparr[i])
                
            elif i==3:
                self.impw.ui.coefx.setText(temparr[i])
                
            elif i==4 and temparr[i]=='row':
                self.impw.ui.yrowcb.setChecked(True)
            elif i==4 and temparr[i]=='col':
                self.impw.ui.ycolcb.setChecked(True)
            elif i==4 and temparr[i]=='none':
                self.impw.ui.ynonecb.setChecked(True)
                
            elif i==5:
                self.impw.ui.rowYst.setText(temparr[i])
                
            elif i==6:
                self.impw.ui.colYst.setText(temparr[i])
                
            elif i==7:
                self.impw.ui.coefy.setText(temparr[i])
                
            elif i==8 and temparr[i]=='comma':
                index = self.impw.ui.dlmtr.findText(',')
                self.impw.ui.dlmtr.setCurrentIndex(index)
            elif i==8 and temparr[i]=='space':
                index = self.impw.ui.dlmtr.findText('space')
                self.impw.ui.dlmtr.setCurrentIndex(index)
                
            elif i==9 and temparr[i]=='csv':
                index = self.impw.ui.dendwith.findText('.csv')
                self.impw.ui.dendwith.setCurrentIndex(index)
            elif i==9 and temparr[i]=='txt':
                index = self.impw.ui.dendwith.findText('.txt')
                self.impw.ui.dendwith.setCurrentIndex(index)
            elif i==9 and temparr[i]=='dat':
                index = self.impw.ui.dendwith.findText('.dat')
                self.impw.ui.dendwith.setCurrentIndex(index)
            elif i==9 and temparr[i]=='xlsx':
                index = self.impw.ui.dendwith.findText('.xlsx')
                self.impw.ui.dendwith.setCurrentIndex(index)
                
            elif i==10 and temparr[i]=='xy':
                self.impw.ui.xy.setChecked(True)
            elif i==10 and temparr[i]=='xyz':
                self.impw.ui.xyz.setChecked(True)
                
            elif i==11:
                self.impw.ui.rowZst.setText(temparr[i])
                
            elif i==12:
                self.impw.ui.colZst.setText(temparr[i])
                
            elif i==13 and temparr[i]=='flipped':
                self.impw.ui.flipdatacb.setChecked(True)
            elif i==13 and temparr[i]=='not-flipped':
                self.impw.ui.flipdatacb.setChecked(False)
                
            elif i==14:
                self.impw.ui.xlabel.setText(temparr[i].replace('_',' '))
            elif i==15:
                self.impw.ui.ylabel.setText(temparr[i].replace('_',' '))
            elif i==16:
                self.impw.ui.zlabel.setText(temparr[i].replace('_',' '))
            elif i==17 and not temparr[i]=='x-Exist':
                index = self.impw.ui.multXwith.findText(temparr[i])
                self.impw.ui.multXwith.setCurrentIndex(index)
            elif i==18 and not temparr[i]=='y-Exist':
                index = self.impw.ui.multYwith.findText(temparr[i])
                self.impw.ui.multYwith.setCurrentIndex(index)
            else:
                pass
        temptext=' - '.join([self.impw.ui.dendwith.currentText()[1:],self.impw.bgmode.checkedButton().text()[0:-5],self.impw.ui.listprefs.currentText()])
        temptext=' - '.join([self.impw.ui.dendwith.currentText()[1:],self.impw.ui.listprefs.currentText()])
        temptext=' - '.join([self.impw.ui.dendwith.currentText()[1:]])
        temptext=''.join(['Imports: ',temptext])
    def funimp(self):
        if self.funw_list == []:
            temparr=[]
        else:
            funnames=self.funw_list[0].split(',/')
            #print(funnames)
            indt=funnames.index(self.funw.listfuns.currentText())
            ind=self.fitw.ui.listfuns_main.findText(self.funw.ui.listfuns.currentText())
            self.fitw.ui.listfuns_main.setCurrentIndex(ind)
            temparr=self.funw_list[indt+1].split(',/')
        for i in range(len(temparr)):
            if i==0:
                self.funw.ui.funText.setText(temparr[i])
            elif i==1:
                self.funw.ui.noOfPars.setText(temparr[i])
            else:
                pass
        self.fitw.ui.fValueEdit.setText(self.funw.ui.funText.text())
    def addpresetBtn(self):
        self.impw.ui.listprefs.addItem(self.impw.ui.newPreset.text())
        self.ui.listprefs_main.addItem(self.impw.ui.newPreset.text())
        del self.impw_list[-1]
        newpres=''
        if self.impw.ui.xrowcb.isChecked():
            newpres='row'
        elif self.impw.ui.xcolcb.isChecked():
            newpres='col'
        elif self.impw.ui.xnonecb.isChecked():
            newpres='none'
        
        newpres=','.join([newpres,self.impw.ui.rowXst.text()])
        newpres=','.join([newpres,self.impw.ui.colXst.text()])
        newpres=','.join([newpres,self.impw.ui.coefx.text()])
        
            
        if self.impw.ui.yrowcb.isChecked():
            newpres=','.join([newpres,'row'])
        elif self.impw.ui.ycolcb.isChecked():
            newpres=','.join([newpres,'col'])
        elif self.impw.ui.ynonecb.isChecked():
            newpres=','.join([newpres,'none'])
        
        newpres=','.join([newpres,self.impw.ui.rowYst.text()])
        newpres=','.join([newpres,self.impw.ui.colYst.text()])
        newpres=','.join([newpres,self.impw.ui.coefy.text()])
            
        if self.impw.ui.dlmtr.currentText()==',':
            newpres=','.join([newpres,'comma'])
        elif self.impw.ui.dlmtr.currentText()=='space':
            newpres=','.join([newpres,'space'])
            
        if self.impw.ui.dendwith.currentText()=='.csv':
            newpres=','.join([newpres,'csv'])
        elif self.impw.ui.dendwith.currentText()=='.txt':
            newpres=','.join([newpres,'txt'])
        elif self.impw.ui.dendwith.currentText()=='.dat':
            newpres=','.join([newpres,'dat'])
        elif self.impw.ui.dendwith.currentText()=='.xlsx':
            newpres=','.join([newpres,'xlsx'])
            
        if self.impw.ui.xy.isChecked():
            newpres=','.join([newpres,'xy'])
        elif self.impw.ui.xyz.isChecked():
            newpres=','.join([newpres,'xyz'])
        
        newpres=','.join([newpres,self.impw.ui.rowZst.text()])
        newpres=','.join([newpres,self.impw.ui.colZst.text()])
            
        if self.impw.ui.flipdatacb.isChecked():
            newpres=','.join([newpres,'flipped'])
        else:
            newpres=','.join([newpres,'not-flipped'])
        
        newpres=','.join([newpres,self.impw.ui.xlabel.text().replace(' ','_')])
        newpres=','.join([newpres,self.impw.ui.ylabel.text().replace(' ','_')])
        newpres=','.join([newpres,self.impw.ui.zlabel.text().replace(' ','_')])
        
        if self.impw.ui.xnonecb.isChecked():
            newpres=','.join([newpres,self.impw.ui.multXwith.currentText()])
        else:
            newpres=','.join([newpres,'x-Exist'])
        
        if self.impw.ui.ynonecb.isChecked():
            newpres=','.join([newpres,self.impw.ui.multYwith.currentText()])
        else:
            newpres=','.join([newpres,'y-Exist'])
        
        self.impw_list.append(newpres)
        self.impw_list[0]=','.join([self.impw_list[0],self.impw.ui.newPreset.text()])
        self.impw_list.append(self.impw.ui.listprefs.currentText())
        #print(self.impw_list)
    def addfunBtn(self):
        del self.funw_list[-1]
        del self.funw_list[-1]
        self.funw.ui.listfuns.addItem(self.funw.ui.newFun.text())
        self.fitw.ui.listfuns_main.addItem(self.funw.ui.newFun.text())
        
        newfun=self.funw.ui.funText.text()
        newfun=',/'.join([newfun,self.funw.ui.noOfPars.text()])
        
        self.funw_list.append(newfun)
        self.funw_list[0]=',/'.join([self.funw_list[0],self.funw.ui.newFun.text()])
        self.funw_list.append(self.funw.ui.pyfileloc.text())
        self.funw_list.append(self.funw.ui.listfuns.currentText())
        #print(self.funw_list)
    def rempresetBtn(self):
        try:
            ttorem = self.impw.ui.listprefs.currentText()
            test = self.impw_list
            ttitles = test[0].split(',')
            indtorem = ttitles.index(ttorem)
            del ttitles[indtorem]
            ttitles=','.join(ttitles)
            del test[indtorem+1]
            test[0] = ttitles
            
            self.impw_list = test
            self.impw.ui.listprefs.removeItem(self.impw.ui.listprefs.currentIndex())
        except Exception as Argument:
            self.genLogforException(Argument)
    def remfunBtn(self):
        try:
            ttorem = self.funw.ui.listfuns.currentText()
            test = self.funw_list
            ttitles = test[0].split(',/')
            indtorem = ttitles.index(ttorem)
            del ttitles[indtorem]
            ttitles=',/'.join(ttitles)
            del test[indtorem+1]
            test[0] = ttitles
            
            self.funw_list = test
            self.funw.ui.listfuns.removeItem(self.funw.ui.listfuns.currentIndex())
            #print(self.funw_list)
        except Exception as Argument:
            self.genLogforException(Argument)
        
    def savePresBtn(self):
        try:
            del self.impw_list[-1]
            self.impw_list.append(self.impw.ui.listprefs.currentText()) #This will also add presets file what user preferred default preset is
            filter=''.join(['txt','(*','.txt',')'])
            qfdlg=QFileDialog()
            qfdlg.setFileMode(QFileDialog.AnyFile)
            newpresfile = qfdlg.getSaveFileName(self, None, "Create New File",filter)
            np.savetxt(newpresfile[0],self.impw_list, delimiter = " ",fmt='%s')
        except Exception as Argument:
            self.genLogforException(Argument)
    def saveFunBtn(self):
        try:
            self.funw_list[-2]=self.funw.ui.pyfileloc.text()
            del self.funw_list[-1]
            self.funw_list.append(self.funw.ui.listfuns.currentText()) #This will also add functions file what user preferred default function is
            filter=''.join(['txt','(*','.txt',')'])
            qfdlg=QFileDialog()
            qfdlg.setFileMode(QFileDialog.AnyFile)
            newpresfile = qfdlg.getSaveFileName(self, None, "Create New File",filter)
            np.savetxt(newpresfile[0],self.funw_list, delimiter = " ",fmt='%s')
        except Exception as Argument:
            self.genLogforException(Argument)
    def saveDefPresetBtn(self):
        #DataDir = getResourcePath("prs")
        try:
            del self.impw_list[-1]
            self.impw_list.append(self.impw.ui.listprefs.currentText()) 
            DataDir = self.makeFolderinDocuments('Instrument Presets')
            presetPath = DataDir/'presets_default.txt'
            np.savetxt(presetPath,self.impw_list, delimiter = " ",fmt='%s')
            self.impw.ui.presetloc.setText(str(presetPath))
        except Exception as Argument:
            self.genLogforException(Argument)
    def saveDefFunBtn(self):
        #DataDir = getResourcePath("prs")
        try:
            self.funw_list[-2]=self.funw.ui.pyfileloc.text()
            del self.funw_list[-1]
            self.funw_list.append(self.funw.ui.listfuns.currentText()) 
            DataDir = self.makeFolderinDocuments('Functions')
            functionPath = DataDir/'functions_default.txt'
            np.savetxt(functionPath,self.funw_list, delimiter = " ",fmt='%s')
            self.funw.ui.funloc.setText(str(functionPath))
        except Exception as Argument:
            self.genLogforException(Argument)
    # def copyInternalPreset(self):
    #     internalDir = getResourcePath('prs')
    #     internalPresetPath = internalDir / 'presets.txt'
    #     externalDir = self.makeFolderinDocuments('Instrument Presets')
    #     externalPresetsPath = externalDir/'presets_default.txt'
    #     shutil.copyfile(internalPresetPath, externalPresetsPath)
        #np.save(presetsPath)
# plotfunctions goes below:
    
    def v2in(self, nparray,val,tolerance=0.1):
        ind = np.nanargmin(np.abs(nparray - val))
        return ind
    
    def xyzdatagenerator(self,filesloc,addmode='multiple'):
        def nonfloatRemover(n1):
            nonnums=[]
            for i in range(len(n1)):
                remtr=-1 #Will be used when items are removed from our array
                for j in range(len(n1[i])):
                    try:
                        float(n1[i][j])
                    except ValueError:
                        remtr+=1
                        nonnums.append([i,j,remtr])
            
            for i in range(len(nonnums)):
                n1[nonnums[i][0]].remove(n1[nonnums[i][0]][nonnums[i][1]-nonnums[i][2]])
            
            remtrlist=[]
            remtr=-1
            for i in range(len(n1)):
                if n1[i]==[]:
                    remtr+=1
                    remtrlist.append([i,remtr])
                    
            for i in range(len(remtrlist)):
                #n1.remove(n1[remtrlist[i][0]-remtrlist[i][0]])
                n1.remove([])
            
            n1len=[]
            for n1i in n1:
                n1len.append(len(n1i))
            
            lenmost=max(set(n1len), key = n1len.count)
            
            badnums=[]
            remtr=-1
            for i in range(len(n1)):
                if len(n1[i])!=lenmost:
                    remtr+=1
                    badnums.append([i,remtr])
            
            for i in range(len(badnums)):
                n1.remove(n1[badnums[i][0]-badnums[i][1]])
            return n1
        
        dends=self.impw.ui.dendwith.currentText()
        xyzmode=self.impw.ui.xyz.isChecked()
        if self.impw.ui.dlmtr.currentText()==',':
            dlmtr=','
        elif self.impw.ui.dlmtr.currentText()=='space':
            dlmtr='\t'
        
        if addmode !="single":
            Xis=self.impw.ui.bgx.checkedButton().text()
            rowXst=int(float(self.impw.ui.rowXst.text()))
            colXst=int(float(self.impw.ui.colXst.text()))
            coefx=float(self.impw.ui.coefx.text())
            
            Yis=self.impw.ui.bgy.checkedButton().text()
            rowYst=int(float(self.impw.ui.rowYst.text()))
            colYst=int(float(self.impw.ui.colYst.text()))
            colZst = int(float(self.impw.ui.colZst.text()))
            rowZst = int(float(self.impw.ui.rowZst.text()))
        else:
            Xis='col'
            rowXst=1
            colXst=1
            coefx=1
            
            Yis='col'
            rowYst=1
            colYst=1
            colZst = 1
            rowZst = 1
        flipdata=self.impw.ui.flipdatacb.isChecked()
        
        file_paths=[]
        file_names=[]
        foldnames=[]
        dflist=[]
        
        if dends=='.csv' or dends=='.txt' or dends=='.dat':
            if addmode=="multiple":
                for file in os.listdir(filesloc):
                    if file.endswith(dends):
                        file_paths.append(os.path.join(filesloc, file))
                        file_names.append(file[0:-4])
                        foldnames.append(filesloc.name)
            elif addmode=="single":
                file_paths=[filesloc]
                file_names=['Sample Data']
                foldnames=['Sample Data Location']
            data_dict=dict()
            for fi in range(len(file_paths)):
                try:
                    with open(file_paths[fi], newline='') as file:
                        reader = csv.reader(file,delimiter=dlmtr)
                        n=[]
                        line_count = 0
                        for row in reader:
                            n.append(row)
                            line_count+=1
                except Exception as Argument:
                    self.genLogforException(Argument)
                n=nonfloatRemover(n)
                dflist.append(pd.DataFrame(np.array(n).astype(float)))
                if xyzmode:
                    z=[[0]*(len(n[1])+1-colZst) for _ in range((len(n))+1-rowZst)]
                    for j in range(0,len(n)+1-rowZst):
                        for i in range(0,len(n[j])+1-colZst):
                            z[j][i]=n[j-1+rowZst][i-1+colZst]
                if Xis=='row' and Yis=='col':
                    y=[0]*(len(n)+1-rowYst)
                    for j in range(0,len(n)+1-rowYst):
                        y[j]=n[j-1+rowYst][colYst-1]
                    x=n[rowXst-1][colXst-1:len(n[0])+1]
                elif Xis=='col' and Yis=='row':
                    x=[0]*(len(n)+1-rowYst)
                    for j in range(0,len(n)+1-rowXst):
                        x[j]=n[j-1+rowXst][colXst-1]
                    y=n[rowXst-1][colXst-1:len(n[0])+1]
                elif Xis=='col' and Yis=='col':
                    y=[0]*(len(n)+1-rowYst)
                    for j in range(0,len(n)+1-rowYst):
                        y[j]=n[j-1+rowYst][colYst-1]
                    x=[0]*(len(n)+1-rowYst)
                    for j in range(0,len(n)+1-rowXst):
                        x[j]=n[j-1+rowXst][colXst-1]
                elif Xis=='row' and Yis=='row':
                    x=n[rowXst-1][colXst-1:len(n[0])+1]
                    y=n[rowYst-1][colYst-1:len(n[0])+1]
                elif Xis=='none' and Yis=='col':
                    y=[0]*(len(n)+1-rowYst)
                    for j in range(0,len(n)+1-rowYst):
                        y[j]=n[j-1+rowYst][colYst-1]
                    if self.impw.ui.multXwith.currentText() == 'y-row/col':
                        x=list(range(1,len(y)+1))
                    elif self.impw.ui.multXwith.currentText() == 'z-row' and xyzmode:
                        x=list(range(1,len(z)+1))
                    elif self.impw.ui.multXwith.currentText() == 'z-col' and xyzmode:
                        x=list(range(1,len(z[0])+1))
                    x=np.array(x)*coefx
                    x=x.tolist()
                elif Xis=='none' and Yis=='row':
                    y=n[rowYst-1][colYst-1:len(n[0])+1]
                    if self.impw.ui.multXwith.currentText() == 'y-row/col':
                        x=list(range(1,len(y)+1))
                    elif self.impw.ui.multXwith.currentText() == 'z-row' and xyzmode:
                        x=list(range(1,len(z)+1))
                    elif self.impw.ui.multXwith.currentText() == 'z-col' and xyzmode:
                        x=list(range(1,len(z[0])+1))
                    x=np.array(x)*coefx
                    x=x.tolist()
                elif Xis=='col' and Yis=='none':
                    x=[0]*(len(n)+1-rowXst)
                    for j in range(0,len(n)+1-rowXst):
                        x[j]=n[j-1+rowXst][colXst-1]
                    if self.impw.ui.multXwith.currentText() == 'x-row/col':
                        y=list(range(1,len(x)+1))
                    elif self.impw.ui.multXwith.currentText() == 'z-row' and xyzmode:
                        y=list(range(1,len(z)+1))
                    elif self.impw.ui.multXwith.currentText() == 'z-col' and xyzmode:
                        y=list(range(1,len(z[0])+1))
                    y=np.array(y)*coefx
                    y=y.tolist()
                elif Xis=='row' and Yis=='none':
                    x=n[rowXst-1][colXst-1:len(n[0])+1]
                    if self.impw.ui.multXwith.currentText() == 'x-row/col':
                        y=list(range(1,len(x)+1))
                    elif self.impw.ui.multXwith.currentText() == 'z-row' and xyzmode:
                        y=list(range(1,len(z)+1))
                    elif self.impw.ui.multXwith.currentText() == 'z-col' and xyzmode:
                        y=list(range(1,len(z[0])+1))
                    y=np.array(y)*coefx
                    y=y.tolist()
                x=np.array(x).astype(float)
                y=np.array(y).astype(float)
                if flipdata:
                    x=np.flip(x)
                    y=np.flip(y)
                if xyzmode:
                    z=np.array(z).astype(float)
                    if flipdata:
                        z=np.flip(z)
                    if Xis == 'col' or Yis == 'row': #This is due to the fact that x axis of contour plot as default is a row array, need to be transposed
                        z=np.transpose(z)
                        x=np.transpose(x)
                        y=np.transpose(y)
                    #tempdata={'a':file_names[fi], 't':x, 'w':y, 'd':z}
                    tempdata={'a':'     /'.join([file_names[fi],foldnames[fi],self.ui.listprefs_main.currentText()]), 't':x, 'w':y, 'd':z}
                else:
                    #tempdata={'a':file_names[fi], 'x':x, 'y':y}
                    tempdata={'a':'     /'.join([file_names[fi],foldnames[fi],self.ui.listprefs_main.currentText()]), 'x':x, 'y':y}
                
                data_dict['     /'.join([file_names[fi],foldnames[fi],self.ui.listprefs_main.currentText()])]=tempdata
        return data_dict, file_names, foldnames,dflist
    def wslice(self,s,w):
        ddyn=s['d'][self.v2in(s['w'],w),:]
        return ddyn
    
    def tslice(self,s,t):
        dspec=s['d'][:,self.v2in(s['t'],t)]
        return dspec
    def h2rgb(self,h):
        pi=math.pi
        h=2*pi*mod(h,1)
        rgb=np.fmax(0,np.array([cos(h),cos(h-2*pi/3),cos(h-4*pi/3)])-cos(2*pi/3))/(1-cos(2*pi/3))
        rgb=tuple(rgb.tolist())
        return rgb
    def plotxy(self,d,nd,xyr,fig,ax,absmode,marker='-',color3D='viridis', tscatter=[0],showleg=False, normatx=False,xnorm=0, normaty=False,ynorm=0):
        self.legendtext_dyn=[]
        self.legendtext_spec=[]
        xyrl=xyr
        cltracker=0
        for ni in nd:
            x0=d[ni]['x']
            y0=d[ni]['y']
            ind=nd.index(ni)
            if self.ui.graphsel.currentText()=='plot left':
                y=y0[self.v2in(x0,xyrl[0]):(self.v2in(x0,xyrl[1])+1)]
                x=x0[self.v2in(x0,xyrl[0]):(self.v2in(x0,xyrl[1])+1)]
                if self.ui.fycb.isChecked():
                    x=self.flx(self.fyList.item(ind).text(),x)
                if self.ui.flzcb.isChecked():
                    y=self.fly(self.flzList.item(ind).text(),y)
            elif self.ui.graphsel.currentText()=='plot right':
                y=y0[self.v2in(x0,xyr[0]):(self.v2in(x0,xyr[1])+1)]
                x=x0[self.v2in(x0,xyr[0]):(self.v2in(x0,xyr[1])+1)]
                if self.ui.fxcb.isChecked():
                    x=self.fx(self.fxList.item(ind).text(),x)
                if self.ui.frzcb.isChecked():
                    y=self.fry(self.frzList.item(ind).text(),y)
            
            if self.ui.bgdataCb.isChecked():
                if self.plotModes.checkedAction().text()=="Matched with x and y" and not self.getitems(self.ui.bgdataList)[ind]=='0':
                    yb=d[self.getitems(self.ui.bgdataList)[ind]]['y']
                    yb=yb[self.v2in(x0,xyr[0]):(self.v2in(x0,xyr[1])+1)]
                    if normatx:
                        if xnorm==0:
                            yb=y/max(abs(yb))
                        else:
                            yb=yb/yb[self.v2in(x,xnorm)]
                elif self.plotModes.checkedAction().text()=="Matched with x and y" and self.getitems(self.ui.bgdataList)[ind]=='0':
                    yb=0
                else:
                    yb=d[self.getitems(self.ui.bgdataList)[0]]['y']
                    yb=yb[self.v2in(x0,xyr[0]):(self.v2in(x0,xyr[1])+1)]
                    if normatx:
                        if xnorm==0:
                            yb=yb/max(abs(yb))
                        else:
                            yb=yb/yb[self.v2in(x,xnorm)]
                y=y-yb
            
            if absmode:
                y=abs(y)
            
            if tscatter[0]!=0:
                tempsc=0
                for ts in tscatter:
                    tempsc=tempsc+y[self.v2in(x,ts)]
                tempsc=tempsc/len(tscatter)
                y=y-tempsc
            
            if normatx:
                if xnorm==0:
                    y=y/max(abs(y))
                else:
                    y=y/y[self.v2in(x,xnorm)]
                
            #print(y)
            self.minmax_xy.append(np.nanmin(y))
            self.minmax_xy.append(np.nanmax(y))
            if self.clrCbspec.isChecked() and self.ui.graphsel.currentText()=='plot right':
                manclr=self.rightclist[cltracker]
            elif self.clrCbdyn.isChecked() and self.ui.graphsel.currentText()=='plot left':
                manclr=self.leftclist[cltracker]
            if self.ui.rgbcol.isChecked():
                line, =ax.plot(x, y,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsx.currentText(),color=self.h2rgb(ind/len(nd)))
            elif self.clrCbdyn.isChecked():
                line, =ax.plot(x, y,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsx.currentText(),color=manclr)
                cltracker=cltracker+1
            else:
                line, =ax.plot(x, y,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsx.currentText())
            if self.ui.graphsel.currentText()=='plot right':
                self.legendtext_spec.append(d[ni]['a'])
                self.linespec_all.append(line)
            elif self.ui.graphsel.currentText()=='plot left':
                self.legendtext_dyn.append(d[ni]['a'])
                self.linedyn_all.append(line)
        
        if self.ui.fycb.isChecked() and self.ui.graphsel.currentText()=='plot left':
            xyrl[0]=self.flx(self.fyList.item(ind).text(),xyrl[0])
            xyrl[1]=self.flx(self.fyList.item(ind).text(),xyrl[1])
        elif self.ui.fxcb.isChecked() and self.ui.graphsel.currentText()=='plot right':
            x=self.fx(self.fxList.item(ind).text(),x)
            xyr[0]=self.fx(self.fxList.item(ind).text(),xyr[0])
            xyr[1]=self.fx(self.fxList.item(ind).text(),xyr[1])
        ax.set_xlim(np.nanmin([xyr[0],xyr[1]]),np.nanmax([xyr[0],xyr[1]]))
        if showleg and self.ui.graphsel.currentText()=='plot right':
            if self.optsSpecW.needShortLeg.isChecked():
                temp=self.legshorten(self.legendtext_spec)
                self.legendtext_spec=temp[0]
                temptitle=temp[1]
                ax.set_title(temptitle, fontsize = int(float(self.ui.fontsizeval.text()))-1)
            ax.legend(self.legendtext_spec,framealpha=0.25)
        elif showleg and self.ui.graphsel.currentText()=='plot left':
            if self.optsDynW.needShortLeg.isChecked():
                temp=self.legshorten(self.legendtext_dyn)
                self.legendtext_dyn=temp[0]
                temptitle=temp[1]
                ax.set_title(temptitle, fontsize = int(float(self.ui.fontsizeval.text()))-1)
            ax.legend(self.legendtext_dyn,framealpha=0.25)
        ax.set_ylim(np.nanmin(self.minmax_xy)-0.05*abs(np.nanmin(self.minmax_xy)),np.nanmax(self.minmax_xy)+0.05*abs(np.nanmax(self.minmax_xy)))
        ax.ticklabel_format(axis='y',style='scientific',scilimits=(-2,2))
        return line
    
    def onClick2D(self,event):
        self.xValue.setText(str(int(event.xdata)))
        self.yValue.setText(str(event.ydata))
        self.submitButtonPushed()
    def plotxyz(self,d,plmd,nd,wt,twr,fig,ax,marker='-',color3D='viridis',multmode=True, tscatter=[0],showleg=False, normatx=False,xnorm=0, normaty=False,ynorm=0,absmode=False):
    # =============================================================================
    # Notes:
        #Mode 2: One wavelength multiple data
        #Mode 2.2: One data multiple wavelength
        #Mode 2.5: Match wavelenths with each data
        
        #Mode 1: One delay multiple data
        #Mode 1.2: One data multiple delay
        #Mode 1.5: Match delays with each data
    # =============================================================================
        self.axspec.set_xlabel(self.xrightlb)
        self.axspec.set_ylabel(self.yrightlb)
        self.axdyn.set_xlabel(self.xleftlb)
        self.axdyn.set_ylabel(self.yleftlb)
        self.ax2D.set_ylabel(self.ytoplb)
        self.ax2D.set_xlabel(self.xtoplb)
        if self.impw.ui.xyz.isChecked():
            self.ax2D.yaxis.set_label_coords(0.075,0.5)
            self.ax2D.xaxis.set_label_coords(0.5,0.125)
        if plmd==2:
            line=[]
            cltracker=0
            try:
                for ni in nd:
                    temp=self.wslice(d[ni],wt[0])
                    t=d[ni]['t']
                    ind=nd.index(ni)
                    if self.ui.xrCb.isChecked():
                        xrnew=self.ui.xrList.item(ind).text().split(',')
                        self.twr[0]=float(xrnew[0])
                        self.twr[1]=float(xrnew[1])
                    if self.ui.xrCb.isChecked() and nd==self.getitems(self.ui.dataList):
                        xrnew=self.ui.xrList.item(ind).text().split(',')
                        self.twr[0]=float(xrnew[0])
                        self.twr[1]=float(xrnew[1])
                    elif self.ui.xrCb.isChecked() and nd==self.getitems(self.ui.bgdataList):
                        xrnew=self.ui.xrList.item(ind+self.ui.dataList.count()).text().split(',')
                        self.twr[0]=float(xrnew[0])
                        self.twr[1]=float(xrnew[1])
                    if self.ui.yavecb.isChecked():
                        tempy=0
                        for wm in self.ui.yaveValue.text().split(','):
                            wmf=float(wm)
                            tempyt=self.wslice(d[ni],wmf)
                            tempy=tempy+tempyt
                        tempy=tempy/len(self.ui.yaveValue.text().split(','))
                        temp=tempy
                    if tscatter[0]!=0:
                        tempsc=0
                        for ts in tscatter:
                            tempsc=tempsc+temp[self.v2in(t,ts)]
                        tempsc=tempsc/len(tscatter)
                        temp=temp-tempsc
                    if self.ui.fxcb.isChecked():
                        t=self.fx(self.fxList.item(ind).text(),t)
                        if self.fx(self.fxList.item(ind).text(),twr[0])>self.fx(self.fxList.item(0).text(),twr[1]):
                            temp2=twr[0]
                            twr[0]=self.fx(self.fxList.item(ind).text(),twr[1])
                            twr[1]=self.fx(self.fxList.item(ind).text(),temp2)
                            t=np.flip(t)
                            temp=np.flip(temp)
                        else:
                            twr[0]=self.fx(self.fxList.item(ind).text(),twr[0])
                            twr[1]=self.fx(self.fxList.item(ind).text(),twr[1])
                    temp=temp[self.v2in(t,twr[0]):(self.v2in(t,twr[1])+1)]
                    #temp=10**(-temp)-1
                    t=t[self.v2in(t,twr[0]):(self.v2in(t,twr[1])+1)]
                    
                    if self.ui.flzcb.isChecked() and nd==self.getitems(self.ui.dataList):
                        temp=self.flz(self.flzList.item(ind).text(),temp)
                    elif self.ui.flzcb.isChecked() and nd==self.getitems(self.ui.bgdataList):
                        temp=self.flz(self.flzList.item(ind+self.ui.dataList.count()).text(),temp)
                    elif self.ui.flzcb.isChecked():
                        temp=self.flz(self.flzList.item(ind).text(),temp)
                    
                    if normatx:
                        if xnorm==0:
                            temp=temp/max(abs(temp))
                        else:
                            temp=temp/temp[self.v2in(t,xnorm)]
                    if absmode:
                        temp=abs(temp)
                    self.minmaxtd.append(np.nanmin(temp))
                    self.minmaxtd.append(np.nanmax(temp))
                    if self.ui.rgbcol.isChecked():
                        line, =ax.plot(t, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsx.currentText(),color=self.h2rgb(ind/len(nd)))
                    elif self.clrCbdyn.isChecked():
                        line, =ax.plot(t, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsx.currentText(),color=self.leftclist[cltracker])
                        cltracker=cltracker+1
                    else:
                        line, =ax.plot(t, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsx.currentText())
                    self.linedyn_all.append(line)
                    self.legendtext_dyn.append(d[ni]['a'])
                self.axdyn.set_ylim(np.nanmin(self.minmaxtd),np.nanmax(self.minmaxtd))
            except IndexError:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setText("Make sure to define at least one <FONT COLOR='#800000'>y<sub>slice</sub></FONT> variable")
                msgBox.setWindowTitle("Warning!")
                msgBox.exec()
            ax.set_xlim(twr[0],twr[1])
            ax.set_ylim(np.nanmin(self.minmaxtd)-0.05*abs(np.nanmin(self.minmaxtd)),np.nanmax(self.minmaxtd)+0.05*abs(np.nanmax(self.minmaxtd)))
            if showleg:
                if self.optsDynW.needShortLeg.isChecked():
                    temp=self.legshorten(self.legendtext_dyn)
                    self.legendtext_dyn=temp[0]
                    temptitle=' @'.join([temp[1],str(wt[0])])
                    try:
                        unit = self.impw.ui.ylabel.text().split('(')[1].split(')')[0]
                    except Exception as Argument:
                        self.genLogforException(Argument)
                        unit=''
                    temptitle=''.join([temptitle,unit])
                    ax.set_title(temptitle, fontsize = int(float(self.ui.fontsizeval.text()))-1)
                ax.legend(self.legendtext_dyn,prop={"size":int(float(self.ui.fontsizeval.text()))},loc='best',framealpha=0).set_draggable(True)
            return line
        elif plmd==2.2:
            cltracker=0
            for i in range(len(nd)):
                if self.ui.xrCb.isChecked():
                    xrnew=self.ui.xrList.item(i).text().split(',')
                    self.twr[0]=float(xrnew[0])
                    self.twr[1]=float(xrnew[1])
                for wi in wt:
                    temp=self.wslice(d[nd[i]],wi)
                    t=d[nd[i]]['t']
                    ind=wt.index(wi)
                    if tscatter[0]!=0:
                        tempsc=0
                        for ts in tscatter:
                            tempsc=tempsc+temp[self.v2in(t,ts)]
                        tempsc=tempsc/len(tscatter)
                        temp=temp-tempsc
                    temp=temp[self.v2in(t,twr[0]):self.v2in(t,twr[1])+1]
                    #temp=10**(-temp)-1
                    t=t[self.v2in(t,twr[0]):self.v2in(t,twr[1])+1]
                    if self.ui.fxcb.isChecked():
                        t=self.fx(self.fxList.item(ind).text(),t)
                    if normatx:
                        if xnorm==0:
                            temp=temp/max(abs(temp))
                        else:
                            temp=temp/temp[self.v2in(t,xnorm)]
                    if absmode:
                        temp=abs(temp)
                    if self.ui.flzcb.isChecked() and nd==self.getitems(self.ui.dataList):
                        temp=self.flz(self.flzList.item(ind).text(),temp)
                    elif self.ui.flzcb.isChecked() and nd==self.getitems(self.ui.bgdataList):
                        temp=self.flz(self.flzList.item(ind+self.ui.dataList.count()).text(),temp)
                    self.minmaxtd.append(np.nanmin(temp))
                    self.minmaxtd.append(np.nanmax(temp))
                    if self.ui.rgbcol.isChecked():
                        line, =ax.plot(t, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsx.currentText(),color=self.h2rgb(cltracker/(len(wt)*len(nd))))
                        cltracker=cltracker+1
                    elif self.clrCbdyn.isChecked():
                        line, =ax.plot(t, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsx.currentText(),color=self.leftclist[cltracker])
                        cltracker=cltracker+1
                    else:
                        line, =ax.plot(t, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsx.currentText())
                    self.linedyn_all.append(line)
                    templeg=' @'.join([d[nd[i]]['a'],str(wi)])
                    #unit = axislable.split('(')[1].split(')')[0]
                    try:
                        unit = self.impw.ui.ylabel.text().split('(')[1].split(')')[0]
                    except Exception as Argument:
                        self.genLogforException(Argument)
                        unit=''
                    templeg=''.join([templeg,unit])
                    self.legendtext_dyn.append(templeg)
            ax.set_xlim(twr[0],twr[1])
            ax.set_ylim(np.nanmin(self.minmaxtd)-0.05*abs(np.nanmin(self.minmaxtd)),np.nanmax(self.minmaxtd)+0.05*abs(np.nanmax(self.minmaxtd)))
            if showleg:
                if self.optsDynW.needShortLeg.isChecked():
                    temp=self.legshorten(self.legendtext_dyn)
                    self.legendtext_dyn=temp[0]
                    temptitle=temp[1]
                    ax.set_title(temptitle, fontsize = int(float(self.ui.fontsizeval.text()))-1)
                ax.legend(self.legendtext_dyn,prop={"size":int(float(self.ui.fontsizeval.text()))},loc='best',framealpha=0).set_draggable(True)
            return line
    
        elif plmd==2.5:
            cltracker=0
            try:
                for i in range(len(nd)):
                    temp=self.wslice(d[nd[i]],wt[i])
                    t=d[nd[i]]['t']
                    if tscatter[0]!=0:
                        tempsc=0
                        for ts in tscatter:
                            tempsc=tempsc+temp[self.v2in(t,ts)]
                        tempsc=tempsc/len(tscatter)
                        temp=temp-tempsc
                    temp=temp[self.v2in(t,twr[0]):self.v2in(t,twr[1])+1]
                    #temp=10**(-temp)-1
                    t=t[self.v2in(t,twr[0]):self.v2in(t,twr[1])+1]
                    # if self.ui.xinremcb.isChecked():
                    #     t=t-xins[i]
                    if self.ui.fxcb.isChecked():
                        t=self.fx(self.fxList.item(i).text(),t)
                    if normatx:
                        if xnorm==0:
                            temp=temp/max(abs(temp))
                        else:
                            temp=temp/temp[self.v2in(t,xnorm)]
                    if absmode:
                        temp=abs(temp)
                        
                    if self.ui.flzcb.isChecked() and nd==self.getitems(self.ui.dataList):
                        temp=self.flz(self.flzList.item(i).text(),temp)
                    elif self.ui.flzcb.isChecked() and nd==self.getitems(self.ui.bgdataList):
                        temp=self.flz(self.flzList.item(i+self.ui.dataList.count()).text(),temp)
                        
                    self.minmaxtd.append(np.nanmin(temp))
                    self.minmaxtd.append(np.nanmax(temp))
                    if self.ui.rgbcol.isChecked():
                        line, =ax.plot(t, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsx.currentText(),color=self.h2rgb(i/len(nd)))
                    elif self.clrCbdyn.isChecked():
                        line, =ax.plot(t, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsx.currentText(),color=self.leftclist[cltracker])
                        cltracker=cltracker+1
                    else:
                        line, =ax.plot(t, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsx.currentText())
                    self.linedyn_all.append(line)
                    templeg=' @'.join([d[nd[i]]['a'],str(wt[i])])
                    try:
                        unit = self.impw.ui.ylabel.text().split('(')[1].split(')')[0]
                    except Exception as Argument:
                        self.genLogforException(Argument)
                        unit=''
                    templeg=''.join([templeg,unit])
                    self.legendtext_dyn.append(templeg)
            except IndexError:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setText("Make sure <FONT COLOR='#800000'>y<sub>slice</sub></FONT> values have same amount of variables as your number of <FONT COLOR='#800000'>Dataset</FONT> you are trying to match")
                msgBox.setWindowTitle("Warning!")
                msgBox.exec()
            ax.set_xlim(twr[0],twr[1])
            ax.set_ylim(np.nanmin(self.minmaxtd)-0.05*abs(np.nanmin(self.minmaxtd)),np.nanmax(self.minmaxtd)+0.05*abs(np.nanmax(self.minmaxtd)))
            if showleg:
                if self.optsDynW.needShortLeg.isChecked():
                    temp=self.legshorten(self.legendtext_dyn)
                    self.legendtext_dyn=temp[0]
                    temptitle=temp[1]
                    ax.set_title(temptitle, fontsize = int(float(self.ui.fontsizeval.text()))-1)
                ax.legend(self.legendtext_dyn,prop={"size":int(float(self.ui.fontsizeval.text()))},loc='best',framealpha=0).set_draggable(True)
            return line
    
        elif plmd==1:
            cltracker=0
            line=[]
            try:
                for ni in nd:
                    temp=self.tslice(d[ni],wt[0])
                    ind=nd.index(ni)
                    if self.ui.yrCb.isChecked() and nd==self.getitems(self.ui.dataList):
                        yrnew=self.ui.yrList.item(ind).text().split(',')
                        self.twr[2]=float(yrnew[0])
                        self.twr[3]=float(yrnew[1])
                    elif self.ui.yrCb.isChecked() and nd==self.getitems(self.ui.bgdataList):
                        yrnew=self.ui.yrList.item(ind+self.ui.dataList.count()).text().split(',')
                        self.twr[2]=float(yrnew[0])
                        self.twr[3]=float(yrnew[1])
                    w=d[ni]['w']
                    t=d[ni]['t']
                    s=d[nd[0]]['d']
                    s0=np.zeros([len(w),len(t)])
                    if tscatter[0]!=0:
                        tempsc=0
                        for ts in tscatter:
                            tempsc=tempsc+self.tslice(d[ni],ts)
                        tempsc=tempsc/len(tscatter)
                        temp=temp-tempsc
                        if not len(nd)>1:
                            for  i in range(len(t)):
                                s0[:,i]=s[:,i]-tempsc
                    else:
                        s0=s
                    temp=temp[self.v2in(w,twr[2]):(self.v2in(w,twr[3])+1)]
                    #temp=10**(-temp)-1
                    sn=s0[self.v2in(w,twr[2]):self.v2in(w,twr[3])+1,self.v2in(t,twr[0]):self.v2in(t,twr[1])+1]
                    #sn=10**(-sn)-1
                    w=w[self.v2in(w,twr[2]):(self.v2in(w,twr[3])+1)]
                    
                    if self.ui.fycb.isChecked():
                        w=self.fy(self.fyList.item(ind).text(),w)
                    
                    if normaty:
                        if ynorm==0:
                            temp=temp/max(abs(temp))
                        else:
                            temp=temp/temp[self.v2in(w,ynorm)]
                    if absmode:
                        temp=-temp
                        sn=-sn
                    if self.ui.frzcb.isChecked() and nd==self.getitems(self.ui.dataList):
                        temp=self.frz(self.frzList.item(ind).text(),temp)
                    elif self.ui.frzcb.isChecked() and nd==self.getitems(self.ui.bgdataList):
                        temp=self.frz(self.frzList.item(ind+self.ui.dataList.count()).text(),temp)
                    elif self.ui.frzcb.isChecked():
                        temp=self.frz(self.frzList.item(ind).text(),temp)
                    self.minmax.append(np.nanmin(sn))
                    self.minmax.append(np.nanmax(sn))
                    self.minmaxt.append(np.nanmin(temp))
                    self.minmaxt.append(np.nanmax(temp))
                    if self.ui.bgdataCb.isChecked():
                        clrtemp=self.h2rgb(ind/len(self.getitems(self.ui.dataList)))
                    else:
                        clrtemp=self.h2rgb(ind/len(nd))
                    if self.ui.rgbcol.isChecked():
                        line, =ax.plot(w, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsy.currentText(),color=clrtemp)
                    elif self.clrCbspec.isChecked():
                        line, =ax.plot(w, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsy.currentText(),color=self.rightclist[cltracker])
                        cltracker=cltracker+1
                    else:
                        line, =ax.plot(w, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsy.currentText())
                    self.linespec_all.append(line)
                    self.legendtext_spec.append(d[ni]['a'])
            except IndexError:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setText("Make sure to define at least one <FONT COLOR='#800000'>x<sub>slice</sub></FONT> variable")
                msgBox.setWindowTitle("Warning!")
                msgBox.exec()
            if self.ui.fycb.isChecked():
                if self.fy(self.fyList.item(ind).text(),twr[2])>self.fy(self.fyList.item(0).text(),twr[3]):
                    temp2=twr[2]
                    twr[2]=self.fy(self.fyList.item(ind).text(),twr[3])
                    twr[3]=self.fy(self.fyList.item(ind).text(),temp2)
                else:
                    twr[2]=self.fy(self.fyList.item(ind).text(),twr[2])
                    twr[3]=self.fy(self.fyList.item(ind).text(),twr[3])
            ax.set_xlim(twr[2],twr[3])
            try:
                if len(nd)==1 and not multmode and not normaty and self.optsSpecW.auto_zlimcb.isChecked():
                    ax.set_ylim(min(self.minmax),max(self.minmax))
                elif len(nd)>1 or multmode:
                    ax.set_ylim(min(self.minmaxt),max(self.minmaxt))
            except Exception as Argument:
                self.genLogforException(Argument)
            plt.show()
            if showleg and 'legendtext_spec' in self.__dict__:
                if self.optsSpecW.needShortLeg.isChecked():
                    temp=self.legshorten(self.legendtext_spec)
                    self.legendtext_spec=temp[0]
                    temptitle=' @'.join([temp[1],str(wt[0])])
                    try:
                        unit = self.impw.ui.xlabel.text().split('(')[1].split(')')[0]
                    except Exception as Argument:
                        self.genLogforException(Argument)
                        unit=''
                    temptitle=''.join([temptitle,unit])
                    ax.set_title(temptitle, fontsize = int(float(self.ui.fontsizeval.text()))-1)
                ax.legend(self.legendtext_spec,prop={"size":int(float(self.ui.fontsizeval.text()))},loc='best',framealpha=0).set_draggable(True)
            return line
        elif plmd==1.2:
            cltracker=0
            for i in range(len(nd)):
                if self.ui.yrCb.isChecked() and nd==self.getitems(self.ui.dataList):
                    yrnew=self.ui.yrList.item(i).text().split(',')
                    self.twr[2]=float(yrnew[0])
                    self.twr[3]=float(yrnew[1])
                elif self.ui.yrCb.isChecked() and nd==self.getitems(self.ui.bgdataList):
                    yrnew=self.ui.yrList.item(i+self.ui.dataList.count()).text().split(',')
                    self.twr[2]=float(yrnew[0])
                    self.twr[3]=float(yrnew[1])
                for ti in wt:
                    temp=self.tslice(d[nd[i]],ti)
                    w=d[nd[i]]['w']
                    ind=wt.index(ti)
                    if tscatter[0]!=0:
                        tempsc=0
                        for ts in tscatter:
                            tempsc=tempsc+self.tslice(d[nd[i]],ts)
                        tempsc=tempsc/len(tscatter)
                        temp=temp-tempsc
                    
                    temp=temp[self.v2in(w,twr[2]):self.v2in(w,twr[3])+1]
                    w=w[self.v2in(w,twr[2]):self.v2in(w,twr[3])+1]
                    if normaty:
                        if ynorm==0:
                            temp=temp/max(abs(temp))
                        else:
                            temp=temp/temp[self.v2in(w,ynorm)]
                    if absmode:
                        temp=-temp
                    
                    if self.ui.fycb.isChecked():
                        w=self.fy(self.fyList.item(ind).text(),w)
                    
                    if self.ui.frzcb.isChecked() and nd==self.getitems(self.ui.dataList):
                        temp=self.frz(self.frzList.item(ind).text(),temp)
                    elif self.ui.frzcb.isChecked() and nd==self.getitems(self.ui.bgdataList):
                        temp=self.frz(self.frzList.item(ind+self.ui.dataList.count()).text(),temp)
                    self.minmax.append(np.nanmin(temp))
                    self.minmax.append(np.nanmax(temp))
                    if self.ui.rgbcol.isChecked():
                        line, =ax.plot(w, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsy.currentText(),color=self.h2rgb(cltracker/(len(wt)*len(nd))))
                        cltracker=cltracker+1
                    elif self.clrCbspec.isChecked():
                        line, =ax.plot(w, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsy.currentText(),color=self.rightclist[cltracker])
                        cltracker=cltracker+1
                    else:
                        line, =ax.plot(w, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsy.currentText())
                    self.linespec_all.append(line)
                    templeg=' @'.join([d[nd[i]]['a'],str(ti)])
                    try:
                        unit = self.impw.ui.xlabel.text().split('(')[1].split(')')[0]
                    except Exception as Argument:
                        self.genLogforException(Argument)
                        unit=''
                    templeg=''.join([templeg,unit])
                    self.legendtext_spec.append(templeg)
            if self.ui.fycb.isChecked():
                if self.fy(self.fyList.item(ind).text(),twr[2])>self.fy(self.fyList.item(0).text(),twr[3]):
                    temp2=twr[2]
                    twr[2]=self.fy(self.fyList.item(ind).text(),twr[3])
                    twr[3]=self.fy(self.fyList.item(ind).text(),temp2)
                else:
                    twr[2]=self.fy(self.fyList.item(ind).text(),twr[2])
                    twr[3]=self.fy(self.fyList.item(ind).text(),twr[3])
            ax.set_xlim(twr[2],twr[3])
            ax.set_ylim(min(self.minmax),max(self.minmax))
            if showleg:
                if self.optsSpecW.needShortLeg.isChecked():
                    temp=self.legshorten(self.legendtext_spec)
                    self.legendtext_spec=temp[0]
                    temptitle=temp[1]
                    ax.set_title(temptitle, fontsize = int(float(self.ui.fontsizeval.text()))-1)
                ax.legend(self.legendtext_spec,prop={"size":int(float(self.ui.fontsizeval.text()))},loc='best',framealpha=0).set_draggable(True)
            return line
        elif plmd==1.5:
            cltracker=0
            try:
                for i in range(len(nd)):
                    temp=self.tslice(d[nd[i]],wt[i])
                    w=d[nd[i]]['w']
                    if tscatter[0]!=0:
                        tempsc=0
                        for ts in tscatter:
                            tempsc=tempsc+self.tslice(d[nd[i]],ts)
                        tempsc=tempsc/len(tscatter)
                        temp=temp-tempsc
                    temp=temp[self.v2in(w,twr[2]):self.v2in(w,twr[3])+1]
                    #temp=10**(-temp)-1
                    w=w[self.v2in(w,twr[2]):self.v2in(w,twr[3])+1]
                    if self.ui.fycb.isChecked():
                        w=self.fy(self.fyList.item(i).text(),w)
                    if normaty:
                        if ynorm==0:
                            temp=temp/max(abs(temp))
                        else:
                            temp=temp/temp[self.v2in(w,ynorm)]
                    if absmode:
                        temp=-temp
                    if self.ui.frzcb.isChecked() and nd==self.getitems(self.ui.dataList):
                        temp=self.frz(self.frzList.item(i).text(),temp)
                    elif self.ui.frzcb.isChecked() and nd==self.getitems(self.ui.bgdataList):
                        temp=self.frz(self.frzList.item(i+self.ui.dataList.count()).text(),temp)
                    self.minmax.append(np.nanmin(temp))
                    self.minmax.append(np.nanmax(temp))
                    if self.ui.rgbcol.isChecked():
                        line, =ax.plot(w, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsy.currentText(),color=self.h2rgb(i/len(nd)))
                    elif self.clrCbdyn.isChecked():
                        line, =ax.plot(w, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsy.currentText(),color=self.leftclist[cltracker])
                        cltracker=cltracker+1
                    else:
                        line, =ax.plot(w, temp,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=self.ui.markerlsy.currentText())
                    self.linespec_all.append(line)
                    templeg=' @'.join([d[nd[i]]['a'],str(wt[i])])
                    try:
                        unit = self.impw.ui.xlabel.text().split('(')[1].split(')')[0]
                    except Exception as Argument:
                        self.genLogforException(Argument)
                        unit=''
                    templeg=''.join([templeg,unit])
                    self.legendtext_spec.append(templeg)
            except IndexError:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setText("Make sure <FONT COLOR='#800000'>X<sub>slice</sub></FONT> values have same amount of variables as your number of <FONT COLOR='#800000'>Dataset</FONT> you are trying to match")
                msgBox.setWindowTitle("Warning!")
                msgBox.exec()
            ax.set_xlim(twr[2],twr[3])
            ax.set_ylim(min(self.minmax),max(self.minmax))
            if showleg:
                if self.optsSpecW.needShortLeg.isChecked():
                    temp=self.legshorten(self.legendtext_spec)
                    self.legendtext_spec=temp[0]
                    temptitle=temp[1]
                    ax.set_title(temptitle, fontsize = int(float(self.ui.fontsizeval.text()))-1)
                ax.legend(self.legendtext_spec,prop={"size":int(float(self.ui.fontsizeval.text()))},loc='best',framealpha=0).set_draggable(True)
            return line
        elif plmd==0:
            t=d[nd[0]]['t']
            w=d[nd[0]]['w']
            s=d[nd[0]]['d']
            twr[0]=float(self.ui.xminValue.text())
            twr[1]=float(self.ui.xmaxValue.text())
            twr[2]=float(self.ui.yminValue.text())
            twr[3]=float(self.ui.ymaxValue.text())
            s0=np.empty([len(w),len(t)])
            if tscatter[0]!=0:
                tempsc=0
                for ts in tscatter:
                    tempsc=tempsc+self.tslice(d[nd[0]],ts)
                tempsc=tempsc/len(tscatter)
                for  i in range(len(t)):
                    s0[:,i]=s[:,i]-tempsc
            else:
                s0=s
            
            if self.ui.fxcb.isChecked():
                t=self.fx(self.fxList.item(0).text(),t)
                if self.fx(self.fxList.item(0).text(),twr[0])>self.fx(self.fxList.item(0).text(),twr[1]):
                    temp=twr[0]
                    twr[0]=self.fx(self.fxList.item(0).text(),twr[1])
                    twr[1]=self.fx(self.fxList.item(0).text(),temp)
                    t=np.flip(t)
                    s0=np.flip(s0,1)
                else:
                    twr[0]=self.fx(self.fxList.item(0).text(),twr[0])
                    twr[1]=self.fx(self.fxList.item(0).text(),twr[1])
            if self.ui.fycb.isChecked():
                w=self.fy(self.fyList.item(0).text(),w)
                if self.fy(self.fyList.item(0).text(),twr[2])>self.fy(self.fyList.item(0).text(),twr[3]):
                    temp=twr[2]
                    twr[2]=self.fy(self.fyList.item(0).text(),twr[3])
                    twr[3]=self.fy(self.fyList.item(0).text(),temp)
                    w=np.flip(w)
                    s0=np.flip(s0,0)
                else:
                    twr[2]=self.fy(self.fyList.item(0).text(),twr[2])
                    twr[3]=self.fy(self.fyList.item(0).text(),twr[3])
            
            sn=s0[self.v2in(w,twr[2]):self.v2in(w,twr[3])+1,self.v2in(t,twr[0]):self.v2in(t,twr[1])+1]
            #sn=10**(-sn)-1
            ww=w[self.v2in(w,twr[2]):self.v2in(w,twr[3])+1]
            tt=t[self.v2in(t,twr[0]):self.v2in(t,twr[1])+1]
            
            if self.opts2DW.mirrorX.isChecked():
                tt=np.insert(tt,0,-np.flip(tt))
                sn=np.append(np.flip(sn,1),sn,axis = 1)
                twr[0]=-twr[1]
                
            t,w=np.meshgrid(tt, ww)
            line = ax.contourf(t, w, sn,cmap=color3D,levels=100)
            
            ax.set_xlim(twr[0],twr[1])
            ax.set_ylim(twr[2],twr[3])
            
            def format_coord(x, y):
                z = sn[self.v2in(ww,y),self.v2in(tt,x)]
                return 'x=%1.4f y=%1.4f z=%1.5f'%(x, y, z)
            
            ax.format_coord = format_coord
            self.c_map_ax.clear()
            self.c_map_ax.axes.get_xaxis().set_visible(False)
            self.c_map_ax.axes.get_yaxis().set_visible(True)
            self.cb2D=matplotlib.colorbar.ColorbarBase(self.c_map_ax, cmap=plt.get_cmap(color3D), orientation = 'vertical',norm=matplotlib.colors.Normalize(np.nanmin(sn), np.nanmax(sn)),ticks=[np.nanmin(sn),np.nanmax(sn)])
            self.c_map_ax.yaxis.set_ticks_position('left')
            self.c_map_ax.set_ylabel(self.ztoplb)
            self.c_map_ax.yaxis.set_label_position('left')
            self.c_map_ax.yaxis.set_label_coords(0.1,1.05)
            return line
        else:
            line=[]
            return line
    def refineBtn(self):
        self.ytoplb=''
        self.xtoplb=''
        if self.impw.ui.xyz.isChecked():
            if self.refinecb.isChecked():
                self.xleftlb=self.impw.ui.xlabel.text()
                self.yleftlb=self.impw.ui.zlabel.text()
                self.xrightlb=self.impw.ui.ylabel.text()
                self.yrightlb=self.impw.ui.zlabel.text()
                self.xtoplb=self.xleftlb
                self.ytoplb=self.xrightlb
                self.ztoplb=self.impw.ui.zlabel.text()
            else:
                self.xleftlb='X'
                self.ytoplb='Y'
                self.xtoplb='X'
                self.ztoplb='Z'
                self.yleftlb='Z'
                self.yrightlb='Z'
                self.xrightlb='Y'
            
            self.axdyn.set_xlabel(self.xleftlb)
            self.axdyn.set_ylabel(self.yleftlb)
            
            self.axspec.set_xlabel(self.xrightlb)
            self.axspec.set_ylabel(self.yrightlb)
            
            self.ax2D.set_ylabel(self.ytoplb)
            self.ax2D.set_xlabel(self.xtoplb)
            self.ax2D.yaxis.set_label_coords(0.075,0.5)
            self.ax2D.xaxis.set_label_coords(0.5,0.125)
            self.c_map_ax.tick_params(left=True,labelleft=True,bottom=True,labelbottom=True)
            self.c_map_ax.set(frame_on=True)
            self.c_map_ax.set_ylabel(self.ztoplb,rotation=0)
        else:
            if self.refinecb.isChecked():
                self.xleftlb=self.impw.ui.xlabel.text()
                self.yleftlb=self.impw.ui.ylabel.text()
                self.xrightlb=self.impw.ui.xlabel.text()
                self.yrightlb=self.impw.ui.ylabel.text()
                self.xtoplb=''
                self.ytoplb=''
                self.ztoplb=''
            else:
                self.xleftlb='X'
                self.yleftlb='Y'
                self.yrightlb='Y'
                self.xrightlb='X'
                self.xtoplb=''
                self.ytoplb=''
                self.ztoplb=''
            
            self.axdyn.set_xlabel(self.xleftlb)
            self.axdyn.set_ylabel(self.yleftlb)
            
            self.axspec.set_xlabel(self.xrightlb)
            self.axspec.set_ylabel(self.yrightlb)
            
            self.ax2D.set_ylabel(self.ytoplb)
            self.ax2D.set_xlabel(self.xtoplb)
            self.ax2D.yaxis.set_label_coords(0.075,0.5)
            self.ax2D.xaxis.set_label_coords(0.5,0.125)
            self.c_map_ax.tick_params(left=False,labelleft=False,bottom=False,labelbottom=False)
            self.c_map_ax.set(frame_on=False)
            self.c_map_ax.set_ylabel(self.ztoplb,rotation=0)
        self.axspec.xaxis.get_label().set_fontsize(int(float(self.ui.fontsizeval.text())))
        self.axspec.yaxis.get_label().set_fontsize(int(float(self.ui.fontsizeval.text())))
        if self.impw.ui.xyz.isChecked():
            if not self.axspec.get_legend()==None:
                temptxt=self.axspec.get_legend().get_texts()
                self.legendtext_spec=[]
                for legtx in temptxt:
                    self.legendtext_spec.append(legtx.get_text())
            if self.ui.legcb.isChecked():
                self.axspec.legend(self.legendtext_spec,prop={"size":int(float(self.ui.fontsizeval.text()))},loc='best',framealpha=0).set_draggable(True)
        elif not self.impw.ui.xyz.isChecked() and self.graphsel.currentText()=="plot right":
            if not self.axspec.get_legend()==None:
                temptxt=self.axspec.get_legend().get_texts()
                self.legendtext_spec=[]
                for legtx in temptxt:
                    self.legendtext_spec.append(legtx.get_text())
            if self.ui.legcb.isChecked():
                self.axspec.legend(self.legendtext_spec,prop={"size":int(float(self.ui.fontsizeval.text()))},loc='best',framealpha=0).set_draggable(True)
        
        for label in (self.axspec.get_xticklabels() + self.axspec.get_yticklabels()):
            label.set_fontsize(int(float(self.ui.fontsizeval.text())))
        
        self.axdyn.xaxis.get_label().set_fontsize(int(float(self.ui.fontsizeval.text())))
        self.axdyn.yaxis.get_label().set_fontsize(int(float(self.ui.fontsizeval.text())))
        if self.impw.ui.xyz.isChecked():
            if not self.axdyn.get_legend()==None:
                self.legendtext_dyn=[]
                temptxt=self.axdyn.get_legend().get_texts()
                for legtx in temptxt:
                    self.legendtext_dyn.append(legtx.get_text())
            if self.ui.legcb.isChecked():
                self.axdyn.legend(self.legendtext_dyn,prop={"size":int(float(self.ui.fontsizeval.text()))},loc='best',framealpha=0).set_draggable(True)
        elif not self.impw.ui.xyz.isChecked() and self.graphsel.currentText()=="plot left":
            if not self.axdyn.get_legend()==None:
                self.legendtext_dyn=[]
                temptxt=self.axdyn.get_legend().get_texts()
                for legtx in temptxt:
                    self.legendtext_dyn.append(legtx.get_text())
            if self.ui.legcb.isChecked():
                self.axdyn.legend(self.legendtext_dyn,prop={"size":int(float(self.ui.fontsizeval.text()))},loc='best',framealpha=0).set_draggable(True)
            
        for label in (self.axdyn.get_xticklabels() + self.axdyn.get_yticklabels()):
            label.set_fontsize(int(float(self.ui.fontsizeval.text())))
        self.axdyn.title.set_fontsize(int(float(self.ui.fontsizeval.text())))
        self.axspec.title.set_fontsize(int(float(self.ui.fontsizeval.text())))
        self.mdyn.figure.tight_layout()
        self.mspec.figure.tight_layout()
        self.mspec.draw()
        self.mdyn.draw()
        self.m2D.draw()
    
    def fontBtn(self,newsize):
        self.axspec.xaxis.get_label().set_fontsize(int(newsize))
        self.axspec.yaxis.get_label().set_fontsize(int(newsize))
        for label in (self.axspec.get_xticklabels() + self.axspec.get_yticklabels()):
            label.set_fontsize(int(newsize))
        
        for label in (self.axdyn.get_xticklabels() + self.axdyn.get_yticklabels()):
            label.set_fontsize(int(newsize))
        self.axdyn.xaxis.get_label().set_fontsize(int(newsize))
        self.axdyn.yaxis.get_label().set_fontsize(int(newsize))
        
        for label in (self.ax2D.get_xticklabels() + self.ax2D.get_yticklabels()):
            label.set_fontsize(int(newsize))
        self.ax2D.xaxis.get_label().set_fontsize(int(newsize))
        self.ax2D.yaxis.get_label().set_fontsize(int(newsize))
        
        for label in (self.c_map_ax.get_xticklabels() + self.c_map_ax.get_yticklabels()):
            label.set_fontsize(int(newsize))
        self.c_map_ax.xaxis.get_label().set_fontsize(int(newsize))
        self.c_map_ax.yaxis.get_label().set_fontsize(int(newsize))
        try:
            if self.impw.ui.xyz.isChecked():
                temptxt=self.axspec.get_legend().get_texts()
                self.legendtext_spec=[]
                for legtx in temptxt:
                    self.legendtext_spec.append(legtx.get_text())
                if self.ui.legcb.isChecked():
                    self.axspec.legend(self.legendtext_spec,prop={"size":int(float(self.ui.fontsizeval.text()))},loc='best',framealpha=0).set_draggable(True)
            elif not self.impw.ui.xyz.isChecked() and self.graphsel.currentText()=="plot right":
                temptxt=self.axspec.get_legend().get_texts()
                self.legendtext_spec=[]
                for legtx in temptxt:
                    self.legendtext_spec.append(legtx.get_text())
                if self.ui.legcb.isChecked():
                    self.axspec.legend(self.legendtext_spec,prop={"size":int(float(self.ui.fontsizeval.text()))},loc='best',framealpha=0).set_draggable(True)
        except Exception as Argument:
            self.genLogforException(Argument)
        try:
            if self.impw.ui.xyz.isChecked():
                self.legendtext_dyn=[]
                temptxt=self.axdyn.get_legend().get_texts()
                for legtx in temptxt:
                    self.legendtext_dyn.append(legtx.get_text())
                if self.ui.legcb.isChecked():
                    self.axdyn.legend(self.legendtext_dyn,prop={"size":int(float(self.ui.fontsizeval.text()))},loc='best',framealpha=0).set_draggable(True)
            elif not self.impw.ui.xyz.isChecked() and self.graphsel.currentText()=="plot left":
                self.legendtext_dyn=[]
                temptxt=self.axdyn.get_legend().get_texts()
                for legtx in temptxt:
                    self.legendtext_dyn.append(legtx.get_text())
                if self.ui.legcb.isChecked():
                    self.axdyn.legend(self.legendtext_dyn,prop={"size":int(float(self.ui.fontsizeval.text()))},loc='best',framealpha=0).set_draggable(True)
        except Exception as Argument:
            self.genLogforException(Argument)
        self.axdyn.title.set_fontsize(int(float(self.ui.fontsizeval.text())))
        self.axspec.title.set_fontsize(int(float(self.ui.fontsizeval.text())))
        try:
            self.mdyn.figure.tight_layout()
            self.mspec.figure.tight_layout()
        except Exception as Argument:
            self.genLogforException(Argument)
        self.mspec.draw()
        self.mdyn.draw()
        self.m2D.draw()    
    
    def save_data(self,objkeys,objs,filename):
        objdict=dict()
        for i in range(len(objkeys)):
            objdict[objkeys[i]]=objs[i]
        pickle_out = open("".join([filename,'.pickle']),'wb')
        pickle.dump(objdict, pickle_out)
        pickle_out.close()
    def load_data(self,filename):
        pickle_in = open("".join([filename,'.pickle']),'rb')
        objdict = pickle.load(pickle_in)
        return objdict
    
    #Below are functions for fit window:
        
    def xdataboxchanged(self):
        if self.fitw.ui.xdatabox.currentText()=='xright':
            self.fitw.ui.ydatabox.setCurrentText('yright')
        elif self.fitw.ui.xdatabox.currentText()=='xleft':
            self.fitw.ui.ydatabox.setCurrentText('yleft')
    def ydataboxchanged(self):
        if self.fitw.ui.ydatabox.currentText()=='yright':
            self.fitw.ui.xdatabox.setCurrentText('xright')
        elif self.fitw.ui.ydatabox.currentText()=='yleft':
            self.fitw.ui.xdatabox.setCurrentText('xleft')
    def fitSubmitButtonPushed(self):
        try:
            if self.fitw.ui.ydatabox.currentText()=='yright':
                self.fitw.xdata=self.axspec.lines[0].get_xdata()
                self.fitw.ydata=self.axspec.lines[0].get_ydata()
                marker=self.ui.markery.currentText()
                markerls=self.ui.markerlsy.currentText()
            else:
                self.fitw.xdata=self.axdyn.lines[0].get_xdata()
                self.fitw.ydata=self.axdyn.lines[0].get_ydata()
                marker=self.ui.markerx.currentText()
                markerls=self.ui.markerlsx.currentText()
            self.lenofx=max([len(self.fitw.xdata),100])
            #self.lenofx=self.lenofx*100 #This might be needed, not sure why I put this here?
            if self.fitw.ui.nonecb.isChecked():
                self.fitw.axFit.clear()
                self.fitw.axFit.plot(self.fitw.xdata, self.fitw.ydata,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=markerls)
                self.fitw.mFit.draw()
            elif self.fitw.ui.simulatecb.isChecked():
                # self.lenofx=max([len(self.fitw.xdata),100])
                # self.lenofx=self.lenofx*100
                self.fitw.x_fit=linspace(np.nanmin(self.fitw.xdata),np.nanmax(self.fitw.xdata),self.lenofx)
                self.x_sim=self.fitw.x_fit
                self.psim=[0]*int(float(self.fitw.ui.parsValue.text()))
                for i in range(int(float(self.fitw.ui.parsValue.text()))):
                    self.psim[i]=float(self.fitw.psliders[i].slval.text())
                funstr=self.fitw.ui.fValue.text()
                #pyPath = self.funw.ui.pyfileloc.text()
                def simfun(x,p):
                    pyF = self.execPyFuns()
                    return eval(funstr)
                self.simfun=simfun
                y_sim=simfun(self.x_sim,self.psim)
                self.fitw.axFit.clear()
                self.linesim, =self.fitw.axFit.plot(self.x_sim, y_sim,'-', ms=5, markerfacecolor="None",markeredgewidth=1.5,ls='-')
                self.fitw.mFit.draw()
            elif self.fitw.ui.trycb.isChecked():
                # self.lenofx=max([len(self.fitw.xdata),100])
                # self.lenofx=self.lenofx*100
                #self.fitw.x_fit=linspace(np.nanmin(self.fitw.xdata),np.nanmax(self.fitw.xdata),self.lenofx)
                self.fitw.x_fit=self.fitw.xdata
                self.x_try=self.fitw.x_fit
                self.ptry=[0]*int(float(self.fitw.ui.parsValue.text()))
                for i in range(int(float(self.fitw.ui.parsValue.text()))):
                    self.ptry[i]=float(self.fitw.psliders[i].slval.text())
                funstr=self.fitw.ui.fValue.text()
                def tryfun(x,p):
                    pyF = self.execPyFuns()
                    return eval(funstr)
                y_try=tryfun(self.x_try,self.ptry)
                self.fitw.axFit.clear()
                self.linetryplot, =self.fitw.axFit.plot(self.fitw.xdata, self.fitw.ydata,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=markerls)
                self.linetry, =self.fitw.axFit.plot(self.x_try, y_try,"-", ms=1, markerfacecolor="None",markeredgewidth=1.5,ls="-", linewidth=3)
                self.linetries=[0]*self.fitw.ui.fList.count()
                for i in range(self.fitw.ui.fList.count()):
                       funstr=self.fitw.ui.fList.item(i).text()
                       def tempfitfun(x,p):
                           pyF = self.execPyFuns()
                           return eval(funstr)
                       y_fit_temp=tempfitfun(self.x_try,self.ptry)
                       self.linetries[i],=self.fitw.axFit.plot(self.x_try, y_fit_temp,"-", ms=1, markerfacecolor="None",markeredgewidth=1.5,ls=":",linewidth=3)
                self.fitw.mFit.draw()
            elif self.fitw.ui.fitcb.isChecked():
                x_fit=self.fitw.xdata
                funstr=self.fitw.ui.fValue.text()
                def fitfun(x,*p): 
                    pyF = self.execPyFuns()
                    return eval(funstr)
                self.p0=[0]*int(float(self.fitw.ui.parsValue.text()))
                self.lb=[0]*int(float(self.fitw.ui.parsValue.text()))
                self.ub=[0]*int(float(self.fitw.ui.parsValue.text()))
                for i in range(int(float(self.fitw.ui.parsValue.text()))):
                    self.p0[i]=float(self.fitw.psliders[i].slval.text())
                    self.lb[i]=float(self.fitw.psliders[i].slmin.text())
                    self.ub[i]=float(self.fitw.psliders[i].slmax.text())
                
                xd=self.fitw.xdata
                yd=self.fitw.ydata
                if self.fitw.ui.fitrcb.isChecked():
                    xfitr=[float(self.fitw.ui.fitrange.text().split(',')[0]),float(self.fitw.ui.fitrange.text().split(',')[1])]
                    xdnew=xd[self.v2in(xd,xfitr[0]):self.v2in(xd,xfitr[1])]
                    ydnew=yd[self.v2in(xd,xfitr[0]):self.v2in(xd,xfitr[1])]
                    xd=xdnew
                    yd=ydnew
                popt, pcov = curve_fit(fitfun, xd, yd,self.p0, bounds=(self.lb,self.ub))
                residuals = yd- fitfun(xd, *popt)
                
                SS = np.sum(residuals**2)
                N  = len(xd)
                K  = len(popt)+1
                self.fitw.currentAIC = N*log(SS/N)+2*K+(2*K*(K+1))/(N-K-1)
                
                popt_err=np.sqrt(np.diag(pcov))
                y_fit=fitfun(x_fit,*popt)
                if self.fitw.ui.fitplrangecb.isChecked():
                    xfitplr=[float(self.fitw.ui.fitplrange.text().split(',')[0]),float(self.fitw.ui.fitplrange.text().split(',')[1])]
                    xfitnew=x_fit[self.v2in(x_fit,xfitplr[0]):self.v2in(x_fit,xfitplr[1])]
                    yfitnew=y_fit[self.v2in(x_fit,xfitplr[0]):self.v2in(x_fit,xfitplr[1])]
                    x_fit=xfitnew
                    y_fit=yfitnew
                self.fitw.axFit.clear()
                
                #For column of data:
                self.csvarray=np.zeros((self.lenofx+2,self.fitw.ui.fList.count()*2+4),dtype=object)
                self.csvarray[:][:] = np.nan
                self.csvarray[0][0]='Data'
                self.csvarray[0][1]=''
                self.csvarray[1][0]='x'
                self.csvarray[1][1]='y'
                self.csvarray[2:len(self.fitw.xdata)+2,0]=self.fitw.xdata
                self.csvarray[2:len(self.fitw.ydata)+2,1]=self.fitw.ydata
                self.csvarray[0][2]='Fit'
                self.csvarray[0][3]=''
                self.csvarray[1][2]='x'
                self.csvarray[1][3]='y'
                self.csvarray[2:len(x_fit)+2,2]=x_fit
                self.csvarray[2:len(y_fit)+2,3]=y_fit
                
                self.lineplot,= self.fitw.axFit.plot(self.fitw.xdata, self.fitw.ydata,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=markerls)
                self.linefit, =self.fitw.axFit.plot(x_fit, y_fit,"-", ms=1, markerfacecolor="None",markeredgewidth=1.5,ls="-",linewidth=3)
                for i in range(self.fitw.ui.fList.count()):
                   funstr=self.fitw.ui.fList.item(i).text()
                   def tempfitfun(x,*p):
                       pyF = self.execPyFuns()
                       return eval(funstr)
                   y_fit_temp=tempfitfun(x_fit,*popt)
                   self.csvarray[0][4+2*(i)]=''.join(['Fit ',str(i+1)])
                   self.csvarray[0][5+2*(i)]=''
                   self.csvarray[1][4+2*(i)]='x'
                   self.csvarray[1][5+2*(i)]='y'
                   self.csvarray[2:len(x_fit)+2,4+2*(i)]=x_fit
                   self.csvarray[2:len(y_fit_temp)+2,5+2*(i)]=y_fit_temp
                   self.fitw.axFit.plot(x_fit, y_fit_temp,"-", ms=1, markerfacecolor="None",markeredgewidth=1.5,ls=":",linewidth=3)
                self.fitw.mFit.draw()
                self.fitw.ui.optparams.setText(str(popt).replace(']','').replace('[',''))
                self.fitw.ui.optErrPars.setText(str(popt_err).replace(']','').replace('[',''))
                presetsDir = self.makeFolderinDocuments('Data')
                dataPath = presetsDir / 'datafit.csv'
                np.savetxt(dataPath, self.csvarray, delimiter = ",",fmt="%s")
                
                #Will work on these later:
                    
                # if self.fitw.multfitmode.isChecked() and not self.fitw.ui.plonlycb.isChecked():
                #     poptarr=[]
                #     if self.fitw.xdatabox.currentText()=='xright':
                #         nd=self.ui.dataBox.currentText()
                #         t=self.d[nd]['t']
                #         tr=self.fitw.ui.xyfitrange.text().split(',')
                #         trin=float(tr[0])
                #         trfin=float(tr[1])
                #         self.xy=t[self.v2in(t,trin):self.v2in(t,trfin)]
                #         plt.figure(figsize=(14, 7))
                #         for xyi in self.xy:
                #             #time.sleep(0.4)
                #             w=self.d[nd]['w']
                #             temp=self.tslice(self.d[nd],xyi)
                #             if self.tsc[0]!=0:
                #                 tempsc=0
                #                 for ts in self.tsc:
                #                     tempsc=tempsc+self.tslice(self.d[nd],ts)
                #                 tempsc=tempsc/len(self.tsc)
                #                 temp=temp-tempsc
                #             temp=temp[self.v2in(w,self.twr[2]):(self.v2in(w,self.twr[3])+1)]
                #             w=w[self.v2in(w,self.twr[2]):(self.v2in(w,self.twr[3])+1)]
                #             xd=w
                #             yd=10**(-temp)-1
                #             popt, pcov = curve_fit(fitfun, xd, yd,self.p0, bounds=(self.lb,self.ub))
                #             y_fit=fitfun(x_fit,*popt)
                #             popt_err=np.sqrt(np.diag(pcov))
                #             plt.clf()
                #             plt.cla()
                #             plt.plot(xd, yd,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=markerls)
                #             plt.plot(x_fit, y_fit,"-", ms=1, markerfacecolor="None",markeredgewidth=1.5,ls=":",linewidth=3)
                #             for i in range(self.fitw.ui.fList.count()):
                #                 funstr=self.fitw.ui.fList.item(i).text()
                #                 def tempfitfun(x,p):
                #                     pyF = self.execPyFuns()
                #                     return eval(funstr)
                #                 y_fit_temp=tempfitfun(x_fit,popt)
                #                 plt.plot(x_fit, y_fit_temp,"-", ms=1, markerfacecolor="None",markeredgewidth=1.5,ls=":",linewidth=3)
                #             plt.show()
                #             plt.pause(1e-3)
                #             poptarr.append(popt)
                #         if self.fitw.ui.plotaftercb.isChecked():
                #             plt.figure(figsize=(14, 7))
                #             plt.clf()
                #             plt.cla()
                #             self.poptarrnp=np.array(poptarr)
                #             plotpars=self.fitw.ui.plotpars.text()
                #             self.plotpars=plotpars.split(',')
                #             xpl=self.xy
                #             for i in range(len(self.plotpars)):
                #                 ypl=self.poptarrnp[0:len(xpl),int(float(self.plotpars[i]))]
                #                 plt.plot(xpl, ypl,"o", ms=3, markerfacecolor="None",markeredgewidth=1.5,ls="-",linewidth=1)
                #             plt.gca().legend(self.fitw.ui.plotparsleg.text().split(','),framealpha=0.25)
                #             plt.show()
                #         self.fitw.mFit.draw()
                # elif self.fitw.ui.plonlycb.isChecked():
                #     plt.figure(figsize=(14, 7))
                #     plt.clf()
                #     plt.cla()
                #     xpl=self.xy
                #     for i in range(len(self.plotpars)):
                #         ypl=self.poptarrnp[0:len(xpl),int(float(self.plotpars[i]))]
                #         plt.plot(xpl, ypl,"o", ms=3, markerfacecolor="None",markeredgewidth=1.5,ls="-",linewidth=1)
                #     plt.gca().legend(self.fitw.ui.plotparsleg.text().split(','),framealpha=0.25)
                #     plt.show()
                # else:
                #     xd=self.fitw.xdata
                #     yd=self.fitw.ydata
                #     if self.fitw.ui.fitrcb.isChecked():
                #         xfitr=[float(self.fitw.ui.fitrange.text().split(',')[0]),float(self.fitw.ui.fitrange.text().split(',')[1])]
                #         xdnew=xd[self.v2in(xd,xfitr[0]):self.v2in(xd,xfitr[1])]
                #         ydnew=yd[self.v2in(xd,xfitr[0]):self.v2in(xd,xfitr[1])]
                #         xd=xdnew
                #         yd=ydnew
                #     popt, pcov = curve_fit(fitfun, xd, yd,self.p0, bounds=(self.lb,self.ub))
                #     popt_err=np.sqrt(np.diag(pcov))
                #     y_fit=fitfun(x_fit,*popt)
                #     if self.fitw.ui.fitplrangecb.isChecked():
                #         xfitplr=[float(self.fitw.ui.fitplrange.text().split(',')[0]),float(self.fitw.ui.fitplrange.text().split(',')[1])]
                #         xfitnew=x_fit[self.v2in(x_fit,xfitplr[0]):self.v2in(x_fit,xfitplr[1])]
                #         yfitnew=y_fit[self.v2in(x_fit,xfitplr[0]):self.v2in(x_fit,xfitplr[1])]
                #         x_fit=xfitnew
                #         y_fit=yfitnew
                #     self.fitw.axFit.clear()
                    
                #     #For column of data:
                #     self.csvarray=np.zeros((self.lenofx+2,self.fitw.ui.fList.count()*2+4),dtype=object)
                #     self.csvarray[:][:] = np.nan
                #     self.csvarray[0][0]='Data'
                #     self.csvarray[0][1]=''
                #     self.csvarray[1][0]='x'
                #     self.csvarray[1][1]='y'
                #     self.csvarray[2:len(self.fitw.xdata)+2,0]=self.fitw.xdata
                #     self.csvarray[2:len(self.fitw.ydata)+2,1]=self.fitw.ydata
                #     self.csvarray[0][2]='Fit'
                #     self.csvarray[0][3]=''
                #     self.csvarray[1][2]='x'
                #     self.csvarray[1][3]='y'
                #     self.csvarray[2:len(x_fit)+2,2]=x_fit
                #     self.csvarray[2:len(y_fit)+2,3]=y_fit
                    
                #     self.lineplot,= self.fitw.axFit.plot(self.fitw.xdata, self.fitw.ydata,marker, ms=5, markerfacecolor="None",markeredgewidth=1.5,ls=markerls)
                #     self.linefit, =self.fitw.axFit.plot(x_fit, y_fit,"-", ms=1, markerfacecolor="None",markeredgewidth=1.5,ls="-",linewidth=3)
                #     for i in range(self.fitw.ui.fList.count()):
                #        funstr=self.fitw.ui.fList.item(i).text()
                #        def tempfitfun(x,*p):
                #            pyF = self.execPyFuns()
                #            return eval(funstr)
                #        y_fit_temp=tempfitfun(x_fit,*popt)
                #        self.csvarray[0][4+2*(i)]=''.join(['Fit ',str(i+1)])
                #        self.csvarray[0][5+2*(i)]=''
                #        self.csvarray[1][4+2*(i)]='x'
                #        self.csvarray[1][5+2*(i)]='y'
                #        self.csvarray[2:len(x_fit)+2,4+2*(i)]=x_fit
                #        self.csvarray[2:len(y_fit_temp)+2,5+2*(i)]=y_fit_temp
                #        self.fitw.axFit.plot(x_fit, y_fit_temp,"-", ms=1, markerfacecolor="None",markeredgewidth=1.5,ls=":",linewidth=3)
                #     self.fitw.mFit.draw()
                #     self.fitw.ui.optparams.setText(str(popt).replace(']','').replace('[',''))
                #     self.fitw.ui.optErrPars.setText(str(popt_err).replace(']','').replace('[',''))
                #     presetsDir = self.makeFolderinDocuments('Data')
                #     dataPath = presetsDir / 'datafit.csv'
                #     np.savetxt(dataPath, self.csvarray, delimiter = ",",fmt="%s")
        except Exception as Argument:
            self.genLogforException(Argument)
    def modelsUpdate(self):
        try:
            if self.fitw.modelsW.modelList1.findText(self.fitw.modelName.text())==-1:
                self.fitw.modelAICs.append(self.fitw.currentAIC)
                self.fitw.modelsList.append(self.fitw.modelName.text())
                self.fitw.modelsW.modelList1.addItem(self.fitw.modelName.text())
                self.fitw.modelsW.modelList2.addItem(self.fitw.modelName.text())
                self.showPopInfo("Successfully added", durationToShow = 0.5,widgetToShowOn=self.fitw.notesedit,color='green')
            else:
                self.showPopInfo("Model already exist!", durationToShow = 0.5,widgetToShowOn=self.fitw.notesedit,color='orange')
        except Exception as Argument:
            self.showPopInfo("Make sure to fit first then add!", durationToShow = 0.5,widgetToShowOn=self.fitw.notesedit,color='red')
            self.genLogforException(Argument)
    def modelsClear(self):
        self.fitw.modelsW.modelList1.clear()
        self.fitw.modelsW.modelList2.clear()
        self.fitw.modelAICs=[]
        self.fitw.modelsList=[]
    def modelsCompare(self):
        try:
            ind1 = self.fitw.modelsList.index(self.fitw.modelsW.modelList1.currentText())
            ind2 = self.fitw.modelsList.index(self.fitw.modelsW.modelList2.currentText())
            AIC1 = self.fitw.modelAICs[ind1]
            AIC2 = self.fitw.modelAICs[ind2]
            model_ratio1to2=exp((AIC2-AIC1)/2)
            if model_ratio1to2>1:
                self.fitw.modelsW.comparisonResult.setText(''.join([ 'Model ',self.fitw.modelsList[ind1],' is better than model ',self.fitw.modelsList[ind2],' by the factor of ',"{0:.2e}".format(model_ratio1to2)]))
            elif model_ratio1to2<1:
                self.fitw.modelsW.comparisonResult.setText(''.join([ 'Model ',self.fitw.modelsList[ind2],' is better than model ',self.fitw.modelsList[ind1],' by the factor of ',"{0:.2e}".format(1/model_ratio1to2)]))
            else:
                self.fitw.modelsW.comparisonResult.setText('Models are same!')
        except Exception as Argument:
            self.fitw.modelsW.comparisonResult.setText('Failed! Make sure to fit first!')
            self.genLogforException(Argument)
    def comparisonInfoAdd(self):
        items = [0]*self.fitw.modelsW.infoList.count()
        listy=self.ui.yList
        if not items:
            listy.addItem(self.fitw.modelsW.comparisonResult.text())
        elif listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.insertItem(listy.row(listitems)+1,self.fitw.modelsW.comparisonResult.text())
        else:
            listy.insertItem(0,self.ui.yValue.text())
    def comparisonInfoRem(self):
        listy=self.fitw.modelsW.infoList
        if listy.selectedItems():
            for listitems in listy.selectedItems():
                listy.takeItem(listy.row(listitems))
        else:
            listy.takeItem(listy.row(listy.item(0)))
    def faddBtn(self):
        try:
            items = [0]*self.fitw.ui.fList.count()
            listf=self.fitw.ui.fList
            self.fitw.parcounter = self.fitw.parcounter+int(float(self.funw.ui.noOfPars.text()))
            self.fitw.parcounterList.insert(0,int(float(self.funw.ui.noOfPars.text())))
            if not items:
                listf.addItem(self.fitw.ui.fValueEdit.text())
            elif listf.selectedItems():
                for listitems in listf.selectedItems():
                    listf.insertItem(listf.row(listitems)+1,self.fitw.ui.fValueEdit.text())
            else:
                listf.insertItem(0,self.fitw.ui.fValueEdit.text())
            tempstr=''
            for i in range(self.fitw.ui.fList.count()):
                if i==0:
                    tempstr=''.join([tempstr,self.fitw.ui.fList.item(i).text()])
                else:
                    tempstr='+'.join([tempstr,self.fitw.ui.fList.item(i).text()])
            self.fitw.ui.fValue.setText(tempstr)
            funstr=self.fitw.ui.fValue.text()
            funstr=funstr.replace('[','_')
            funstr=funstr.replace(']','')
            try:
                lat=self.py2tex(funstr)
            except:
                lat=funstr
            self.fitw.axFun.clear()
            self.fitw.axFun.axis('off')
            self.fitw.axFun.text(0.5,0.4, r"$%s$" % lat, fontsize = 12,horizontalalignment='center',
            verticalalignment='center')
            self.fitw.mFun.draw()
            self.fitw.parsValue.setText(str(self.fitw.parcounter))
            self.addremparam()
        except Exception as Argument:
            self.genLogforException(Argument)
    def fremBtn(self):
        try:
            listf=self.fitw.ui.fList
            #self.fitw.parcounter = self.fitw.parcounter-int(float(self.funw.ui.noOfPars.text()))
            if listf.selectedItems():
                for listitems in listf.selectedItems():
                    ind = listf.row(listitems)
                    self.fitw.parcounter=self.fitw.parcounter-self.fitw.parcounterList[ind]
                    del self.fitw.parcounterList[ind]
                    listf.takeItem(listf.row(listitems))
            else:
                if not self.fitw.parcounterList==[]:
                    self.fitw.parcounter=self.fitw.parcounter-self.fitw.parcounterList[0]
                    del self.fitw.parcounterList[0]
                listf.takeItem(listf.row(listf.item(0)))
            tempstr=''
            for i in range(self.fitw.ui.fList.count()):
                if i==0:
                    tempstr=''.join([tempstr,self.fitw.ui.fList.item(i).text()])
                else:
                    tempstr='+'.join([tempstr,self.fitw.ui.fList.item(i).text()])
            self.fitw.ui.fValue.setText(tempstr)
            funstr=self.fitw.ui.fValue.text()
            funstr=funstr.replace('[','')
            funstr=funstr.replace(']','')
            try:
                if funstr!='':
                    lat=self.py2tex(funstr)
                else:
                    lat=self.py2tex('NaN')
            except:
                lat = funstr
            self.fitw.axFun.clear()
            self.fitw.axFun.axis('off')
            self.fitw.axFun.text(0.5,0.4, r"$%s$" % lat, fontsize = 12,horizontalalignment='center',
            verticalalignment='center')
            self.fitw.mFun.draw()
            self.fitw.parsValue.setText(str(self.fitw.parcounter))
            self.addremparam()
        except Exception as Argument:
            self.genLogforException(Argument)
    def addremparam(self):
        try:
            no_ofpar=int(float(self.fitw.ui.parsValue.text()))
            if no_ofpar>(self.fitw.ui.sliderlayout.count()):
                no_ofpars_toadd=no_ofpar-self.fitw.ui.sliderlayout.count()
                #indcs=[]
                for i in range(no_ofpars_toadd):
                    self.fitw.ui.sliderlayout.addWidget(sliderObj(sliderno=self.fitw.ui.sliderlayout.count(),app=self.app))
                    lastind=self.fitw.ui.sliderlayout.count()-1
                    #indcs
                    self.fitw.psliders.append(self.fitw.ui.sliderlayout.itemAt(lastind).widget())
                    self.fitw.psliders[lastind].slval.textChanged.connect(lambda val, indc=lastind: self.paramchanged(val,indc)) #Need to understand this part, confused, but works
            elif no_ofpar<(self.fitw.ui.sliderlayout.count()):
                no_ofpars_torem=self.fitw.ui.sliderlayout.count()-no_ofpar
                for i in range(no_ofpars_torem):
                    lastind=self.fitw.ui.sliderlayout.count()-1
                    self.fitw.ui.sliderlayout.itemAt(lastind).widget().deleteLater()
                    self.fitw.ui.sliderlayout.removeWidget(self.fitw.ui.sliderlayout.itemAt(lastind).widget())
                    del self.fitw.psliders[lastind]
            self.ptry=[0]*int(float(self.fitw.ui.parsValue.text()))
            self.psim=[0]*int(float(self.fitw.ui.parsValue.text()))
        except Exception as Argument:
            self.genLogforException(Argument)
    def paramchanged(self, n,ind):
        try:
            if self.fitw.ui.simulatecb.isChecked():
                self.psim[ind]=float(self.fitw.psliders[ind].slval.text())
                y_sim_new=self.simfun(self.x_sim,self.psim)
                self.linesim.set_ydata(y_sim_new)
                self.fitw.mFit.draw()
            elif self.fitw.ui.trycb.isChecked():
                self.ptry[ind]=float(self.fitw.psliders[ind].slval.text())
                funstr=self.fitw.ui.fValue.text()
                def tryfun(x,p):
                    pyF = self.execPyFuns()
                    return eval(funstr)
                y_try_new=tryfun(self.x_try,self.ptry)
                self.linetry.set_ydata(y_try_new)
                for i in range(self.fitw.ui.fList.count()):
                    funstr=self.fitw.ui.fList.item(i).text()
                    def tempfitfun(x,p):
                        pyF = self.execPyFuns()
                        return eval(funstr)
                    newydata=tempfitfun(self.x_try,self.ptry)
                    self.linetries[i].set_ydata(newydata)
                self.fitw.mFit.draw()
        except Exception as Argument:
            self.genLogforException(Argument)
    def quickparamaddBtn(self):
        try:
            paramstoadd=self.fitw.ui.inparams.text().split(' ')
            paramstoadd = [y for y in paramstoadd if y != '']
            rangetemp=np.nanmin([len(paramstoadd),len(self.fitw.psliders)])
            #print(paramstoadd)
            if not paramstoadd==[]:
                for i in range(rangetemp):
                    self.fitw.psliders[i].slval.setText(paramstoadd[i])
                    self.fitw.psliders[i].slidernumchanged()
            else:
                for i in range(len(self.fitw.psliders)):
                    self.fitw.psliders[i].slidernumchanged()
        except Exception as Argument:
            for i in range(rangetemp):
                self.fitw.psliders[i].slidernumchanged()
            self.genLogforException(Argument)
    def py2tex(self,expr):
        pt = ast.parse(expr)
        return LatexVisitor().visit(pt.body[0].value)
    def saveBtn(self, nameToSave = '',needSaved=True,showPopInfo=True,fitneedsaved=True): #need fix
        try:
            list_tosave=[]
            
            templist=self.ui.controlwindowframe.findChildren(QLineEdit)
            for widgets in templist:
                list_tosave.append(widgets.text())
            
            templist=self.ui.controlwindowframe.findChildren(QCheckBox)
            for widgets in templist:
                list_tosave.append(str(widgets.isChecked()))
            
            templist=self.ui.controlwindowframe.findChildren(QRadioButton)
            for widgets in templist:
                list_tosave.append(str(widgets.isChecked()))
            
            templist=self.ui.controlwindowframe.findChildren(QComboBox)
            for widgets in templist:
                list_tosave.append(widgets.currentText())
                
            templist=self.ui.controlwindowframe.findChildren(QListWidget)
            for widgets in templist:
                temp=[]
                for i in range(widgets.count()):
                    temp.append(widgets.item(i).text())
                list_tosave.append(temp)
            #self.menuFrame.findChildren(QMenu)[0].actions()[2].text()
            
            list_tosave.append(self.getitemsqc(self.ui.filesLoc))
            list_tosave.append(self.ui.dataBox.currentText())
            
            #Below are to save fit tool parameters:
            if fitneedsaved:
                templist=self.fitw.ui.fitcontrolsframe.findChildren(QLineEdit)
                for widgets in templist:
                    list_tosave.append(widgets.text())
                
                templist=self.fitw.ui.fitcontrolsframe.findChildren(QCheckBox)
                for widgets in templist:
                    list_tosave.append(str(widgets.isChecked()))
                    
                templist=self.fitw.ui.fitcontrolsframe.findChildren(QComboBox)
                for widgets in templist:
                    list_tosave.append(widgets.currentText())
                    
                templist=self.fitw.ui.fitcontrolsframe.findChildren(QRadioButton)
                for widgets in templist:
                    list_tosave.append(str(widgets.isChecked()))
                    
                templist=self.fitw.ui.fitcontrolsframe.findChildren(QListWidget)
                for widgets in templist:
                    temp=[]
                    for i in range(widgets.count()):
                        temp.append(widgets.item(i).text())
                    list_tosave.append(temp)
                    
                
                list_tosave.append(self.fitw.ui.notesedit.text())
                
                
                # templist=self.fitw.ui.paramsframe.findChildren(QLineEdit)
                # for widgets in templist:
                #     list_tosave.append(widgets.text())
                
                # templist=self.fitw.ui.paramsframe.findChildren(QCheckBox)
                # for widgets in templist:
                #     list_tosave.append(str(widgets.isChecked()))
                    
                
                templist=self.fitw.ui.slidersframe.findChildren(QLineEdit)
                for widgets in templist:
                    list_tosave.append(widgets.text())
                
                templist=self.fitw.ui.slidersframe.findChildren(QCheckBox)
                for widgets in templist:
                    list_tosave.append(str(widgets.isChecked()))
                list_tosave.append(self.fitw.ui.fValue.text())
            
            templist=self.mbar.findChildren(QMenu)
            for menu in templist:
                temp=[]
                for action in menu.actions():
                    temp.append(action.isChecked())
                list_tosave.append(temp)
            if showPopInfo:
                self.showPopInfo('Successfully saved!',durationToShow=0.5, color = 'green',widgetToShowOn=self.mbar)
            if needSaved and not nameToSave=='':
                np.save(nameToSave,list_tosave)
            else:
                return list_tosave
        except Exception as Argument:
            self.genLogforException(Argument)
            self.showPopInfo('Issue with saving! Check read-write permissions.',durationToShow=1.5, color = 'red',widgetToShowOn=self.mbar)
    
    def loadBtn(self,datatoload, arrayLoadMode = False, needLoaded = True, showPopInfo = True, fitneedloaded=True):
        try:
            if arrayLoadMode:
                list_toload = datatoload
            else:
                list_toload=np.load(datatoload,allow_pickle=True)
            
            k=0;
            templist=self.ui.controlwindowframe.findChildren(QLineEdit)
            for widgets in templist:
                widgets.setText(list_toload[k])
                k=k+1
            
            templist=self.ui.controlwindowframe.findChildren(QCheckBox)
            for widgets in templist:
                if list_toload[k]=='True':
                    s=True
                else:
                    s=False
                widgets.setChecked(s)
                k=k+1
            
            templist=self.ui.controlwindowframe.findChildren(QRadioButton)
            for widgets in templist:
                if list_toload[k]=='True':
                    s=True
                else:
                    s=False
                    
                widgets.setChecked(s)
                k=k+1
            
            templist=self.ui.controlwindowframe.findChildren(QComboBox)
            for widgets in templist:
                widgets.setCurrentText(list_toload[k])
                k=k+1
            
            templist=self.ui.controlwindowframe.findChildren(QListWidget)
            for widgets in templist:
                widgets.clear()
                temp=list_toload[k]
                for i in range(len(temp)):
                    widgets.insertItem(i,temp[i])
                k=k+1
            self.ui.filesLoc.clear()
            self.ui.dataBox.clear()
            self.ui.filesLoc.addItems(list_toload[k])
            k=k+1
            self.prefimp_main()
            if needLoaded:
                self.addallBtn()
            if self.ui.dataBox.count()!=0:
                ind=self.ui.dataBox.findText(list_toload[k])
                self.ui.dataBox.setCurrentIndex(ind)
            k=k+1
            
            if self.ui.filesLoc.count()!=0:
                self.ui.addButton.setEnabled(True)
                self.ui.addallButton.setEnabled(True)
                self.ui.refreshButton.setEnabled(True)
                self.ui.refreshAllButton.setEnabled(True)
            
            #Below are fit parameter loads
            if fitneedloaded:
                templist=self.fitw.ui.fitcontrolsframe.findChildren(QLineEdit)
                for widgets in templist:
                    widgets.setText(list_toload[k])
                    k=k+1
                
                templist=self.fitw.ui.fitcontrolsframe.findChildren(QCheckBox)
                for widgets in templist:
                    if list_toload[k]=='True':
                        s=True
                    else:
                        s=False
                    widgets.setChecked(s)
                    k=k+1
                    
                templist=self.fitw.ui.fitcontrolsframe.findChildren(QComboBox)
                for widgets in templist:
                    widgets.setCurrentText(list_toload[k])
                    k=k+1
                
                templist=self.fitw.ui.fitcontrolsframe.findChildren(QRadioButton)
                for widgets in templist:
                    if list_toload[k]=='True':
                        s=True
                    else:
                        s=False
                    widgets.setChecked(s)
                    k=k+1
                
                templist=self.fitw.ui.fitcontrolsframe.findChildren(QListWidget)
                for widgets in templist:
                    temp=list_toload[k]
                    widgets.clear()
                    for i in range(len(temp)):
                        widgets.insertItem(i,temp[i]) #check this
                    k=k+1
                
                
                self.fitw.ui.notesedit.setText(list_toload[k])
                k=k+1
                
                
                # templist=self.fitw.ui.paramsframe.findChildren(QLineEdit)
                # for widgets in templist:
                #     widgets.setText(list_toload[k])
                #     k=k+1
                
                # templist=self.fitw.ui.paramsframe.findChildren(QCheckBox)
                # for widgets in templist:
                #     if list_toload[k]=='True':
                #         s=True
                #     else:
                #         s=False
                #     widgets.setChecked(s)
                #     k=k+1
                
                self.addremparam()
                
                templist=self.fitw.ui.slidersframe.findChildren(QLineEdit)
                for widgets in templist:
                    widgets.setText(list_toload[k])
                    k=k+1
                
                templist=self.fitw.ui.slidersframe.findChildren(QCheckBox)
                for widgets in templist:
                    if list_toload[k]=='True':
                        s=True
                    else:
                        s=False
                    widgets.setChecked(s)
                    k=k+1
                
                for ind in range(int(float(self.fitw.ui.parsValue.text()))):
                    sliderObj.minlimchanged(self.fitw.psliders[ind])
                
                self.fitw.ui.fValue.setText(list_toload[k])
                k=k+1
            
            templist=self.mbar.findChildren(QMenu)
            for i in range(len(templist)-1):
                temp=list_toload[k]
                actsList = templist[i].actions()
                for i in range(len(temp)):
                    actsList[i].setChecked(temp[i])
                k=k+1
            
            if showPopInfo:
                self.showPopInfo('Successfully loaded!',durationToShow=0.5, color = 'green',widgetToShowOn=self.mbar)
        except Exception as Argument:
            self.genLogforException(Argument)
            if showPopInfo:
                self.showPopInfo('Loading issue. Partially loaded.',durationToShow=1.5, color = 'orange',widgetToShowOn=self.mbar)
        
    def resetBtn(self):
        #DataDir = getResourcePath("/Users/seyitliyev/Desktop/My Drive/PhD - NCSU/PhD Projects/Python/PyInstaller_pack/Graphxyz_clean/src/data")
        presetsDir = self.makeFolderinDocuments('Saved Tabs')
        #presetsDir = getResourcePath(os.path.expanduser('~'))/'Documents'/'Graphxyz'/'Saved Tabs'
        #presetsDir = getResourcePath("npys")
        npyPath = presetsDir / 'reset.npy'
        self.loadBtn(npyPath,showPopInfo=False,needLoaded=False,fitneedloaded=False)
        self.ax2D.clear()
        self.axdyn.clear()
        self.axspec.clear()
        self.m2D.draw()
        self.mdyn.draw()
        self.mspec.draw()
        #self.customAxisClear(self.axdyn)
        #self.axdyn.clear()
        #self.modechanged()
        self.showPopInfo('Successfully reset!',durationToShow=0.5, color = 'green',widgetToShowOn=self.mbar)
        #self.hideAllViews()
    def loadDefBtn(self):
        try:
            #presetsDir = getResourcePath("npys")
            npyDir = self.makeFolderinDocuments ('Saved Tabs')
            npyPath = npyDir / 'default.npy'
            #npyPath = presetsDir / 'default.npy'
            self.loadBtn(npyPath)
            self.submitButtonPushed()
        except Exception as Argument:
            self.genLogforException(Argument)
            self.showPopInfo('Data could not be loaded! Check if the location of the data on the hard drive changed.',durationToShow=2, color = 'orange',widgetToShowOn=self.mbar)
    def loadasBtn(self):
        try:
            file_dialog = QFileDialog()
            #filter=''.join([self.impw.ui.dendwith.currentText(),'(*',self.impw.ui.dendwith.currentText(),')'])
            #print(filter)
            filter = '.npy(*.npy)'
            file_dialog.setNameFilters([filter])
            #file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
            file_view = file_dialog.findChild(QListView, 'listView')
            if file_view:
                file_view.setSelectionMode(QAbstractItemView.MultiSelection)
            f_tree_view = file_dialog.findChild(QTreeView)
            if f_tree_view:
                f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)
            if file_dialog.exec():
                folderLoc = file_dialog.selectedFiles()
            #print(folderLoc)
            #presetsDir = getResourcePath(os.path.expanduser('~'))/'Documents'/'Graphxyz'/'Saved tabs'
            #npyPath = presetsDir / 'default.npy'
            self.loadBtn(folderLoc[0])
            self.submitButtonPushed()
        except Exception as Argument:
            self.genLogforException(Argument)
            self.showPopInfo('Data could not be loaded! Check if the location of the data on the hard drive changed.',durationToShow=2, color = 'orange',widgetToShowOn=self.mbar)
    def saveasBtn(self):
        try:
            filter=''.join(['npy','(*','.npy',')'])
            qfdlg=QFileDialog()
            #qfdlg.setFileMode(QFileDialog.AnyFile)
            npySave = qfdlg.getSaveFileName(self, None, "Create New File",filter)
            self.saveBtn(npySave[0])
            self.submitButtonPushed()
        except Exception as Argument:
            self.genLogforException(Argument)
        #np.savetxt(newpresfile[0],self.impw_list, delimiter = " ",fmt='%s')
    def saveDefBtn(self):
        #npyDir = getResourcePath("npys")
        npyDir = self.makeFolderinDocuments ('Saved Tabs')
        npyPath = npyDir / 'default'
        self.saveBtn(npyPath)
    def loadfitBtn(self): #needs fix, use pathlib
        list_toload=np.load(''.join([self.fitw.ui.dataloadname.text(),'.npy']),allow_pickle=True)
        k=0;
        
        templist=self.fitw.ui.fitcontrolsframe.findChildren(QLineEdit)
        for widgets in templist:
            widgets.setText(list_toload[k])
            k=k+1
        
        templist=self.fitw.ui.fitcontrolsframe.findChildren(QCheckBox)
        for widgets in templist:
            if list_toload[k]=='True':
                s=True
            else:
                s=False
            widgets.setChecked(s)
            k=k+1
            
        templist=self.fitw.ui.fitcontrolsframe.findChildren(QComboBox)
        for widgets in templist:
            widgets.setCurrentText(list_toload[k])
            k=k+1
        
        templist=self.fitw.ui.fitcontrolsframe.findChildren(QRadioButton)
        for widgets in templist:
            if list_toload[k]=='True':
                s=True
            else:
                s=False
            widgets.setChecked(s)
            k=k+1
        
        templist=self.fitw.ui.fitcontrolsframe.findChildren(QListWidget)
        for widgets in templist:
            temp=list_toload[k]
            widgets.clear()
            for i in range(len(temp)):
                widgets.insertItem(i,temp[i]) #check this
            k=k+1
        
        
        self.fitw.ui.notesedit.setText(list_toload[k])
        k=k+1
        
        
        templist=self.fitw.ui.paramsframe.findChildren(QLineEdit)
        for widgets in templist:
            widgets.setText(list_toload[k])
            k=k+1
        
        templist=self.fitw.ui.paramsframe.findChildren(QCheckBox)
        for widgets in templist:
            if list_toload[k]=='True':
                s=True
            else:
                s=False
            widgets.setChecked(s)
            k=k+1
        
        self.addremparam()
        
        templist=self.fitw.ui.slidersframe.findChildren(QLineEdit)
        for widgets in templist:
            widgets.setText(list_toload[k])
            k=k+1
        
        templist=self.fitw.ui.slidersframe.findChildren(QCheckBox)
        for widgets in templist:
            if list_toload[k]=='True':
                s=True
            else:
                s=False
            widgets.setChecked(s)
            k=k+1
        
        for ind in range(int(float(self.fitw.ui.parsValue.text()))):
            sliderObj.minlimchanged(self.fitw.psliders[ind])
        
        self.fitw.ui.fValue.setText(list_toload[k])
        k=k+1
        
    def savefitBtn(self):
        list_tosave=[]
        
        templist=self.fitw.ui.fitcontrolsframe.findChildren(QLineEdit)
        for widgets in templist:
            list_tosave.append(widgets.text())
        
        templist=self.fitw.ui.fitcontrolsframe.findChildren(QCheckBox)
        for widgets in templist:
            list_tosave.append(str(widgets.isChecked()))
            
        templist=self.fitw.ui.fitcontrolsframe.findChildren(QComboBox)
        for widgets in templist:
            list_tosave.append(widgets.currentText())
            
        templist=self.fitw.ui.fitcontrolsframe.findChildren(QRadioButton)
        for widgets in templist:
            list_tosave.append(str(widgets.isChecked()))
            
        templist=self.fitw.ui.fitcontrolsframe.findChildren(QListWidget)
        for widgets in templist:
            temp=[]
            for i in range(widgets.count()):
                temp.append(widgets.item(i).text())
            list_tosave.append(temp)
            
        
        list_tosave.append(self.fitw.ui.notesedit.text())
        
        
        templist=self.fitw.ui.paramsframe.findChildren(QLineEdit)
        for widgets in templist:
            list_tosave.append(widgets.text())
        
        templist=self.fitw.ui.paramsframe.findChildren(QCheckBox)
        for widgets in templist:
            list_tosave.append(str(widgets.isChecked()))
            
        
        templist=self.fitw.ui.slidersframe.findChildren(QLineEdit)
        for widgets in templist:
            list_tosave.append(widgets.text())
        
        templist=self.fitw.ui.slidersframe.findChildren(QCheckBox)
        for widgets in templist:
            list_tosave.append(str(widgets.isChecked()))
            
        list_tosave.append(self.fitw.ui.fValue.text())
        np.save(self.fitw.ui.fitsavename.text(),list_tosave) #needs fix, use pathlib
        
    def copyfig(self,fromcanvas):
        try:
            figloc = self.makeFolderinDocuments('Saved Figures')
            figloc = figloc/'tempimg.svg'
            fromcanvas.figure.savefig(figloc, format='svg', dpi=1200,bbox_inches=0, transparent=True)
            datatocopy = QMimeData()
            pathtofile=os.path.abspath(figloc)
            url = QUrl.fromLocalFile(pathtofile)
            datatocopy.setUrls([url])
            self.app.clipboard().setMimeData(datatocopy)
        except Exception as Argument:
            self.genLogforException(Argument)
    def legshorten(self,long_leg):
        try:
            def find_all(a_str, sub):
                start = 0
                while True:
                    start = a_str.find(sub, start)
                    if start == -1: return
                    yield start
                    start += len(sub) # use start += 1 to find overlapping matches
            
            short_leg = []
            for strs in long_leg:
                short_leg.append("" + strs)
            for i in range(len(long_leg)):
                short_leg [i] = short_leg[i].replace('_',' ')
                short_leg [i] = short_leg[i].replace('-',' ')
            
            wrd_strs = [[]*len(long_leg) for _ in range(len(long_leg))]
            for j in range(len(short_leg)):
                ind_sp=list(find_all(short_leg[j],' '))
                ind_sp.insert(0,-1)
                for i in range(len(ind_sp)):
                    if i<len(ind_sp)-1:
                        wrd_strs[j].append(short_leg[j][ind_sp[i]+1:ind_sp[i+1]])
                    else:
                        wrd_strs[j].append(short_leg[j][ind_sp[i]+1:]);
            
            str_rem = set(wrd_strs[0])
            for s in wrd_strs[1:]:
                str_rem.intersection_update(s)
            str_rem=list(str_rem)
            
            remCnt = [[]*len(wrd_strs) for _ in range(len(wrd_strs))]
            for i in range(len(wrd_strs)):
                for j in range(len(str_rem)):
                    remCnt[i].append(wrd_strs[i].count(str_rem[j]))
            
            
                        
            for i in range(len(wrd_strs)):
                for j in range(len(str_rem)):
                    for k in range(remCnt[i][j]):
                        indx=short_leg[i].index(str_rem[j])
                        if not str_rem[j]==' ' and not str_rem[j]=='' and indx!=0:
                            short_leg[i]=short_leg[i].replace(''.join([' ',str_rem[j]]),'',1)
                        if not str_rem[j]==' ' and not str_rem[j]=='' and indx==0:
                            short_leg[i]=short_leg[i].replace(str_rem[j],'',1)
                            short_leg[i]=short_leg[i][1:]
            for i in range(len(short_leg)):
                short_leg[i]=short_leg[i].strip()
            
            tempsorted=[]
            for i in range(len(long_leg)):
                long_leg [i] = long_leg[i].replace('_',' ')
                long_leg [i] = long_leg[i].replace('-',' ')
            for j in range(len(str_rem)):
                tempsorted.append(long_leg[0].index(str_rem[j]))
            tempor=[0]*len(tempsorted)
            for i in range(len(tempsorted)):
                tempor[i]=tempsorted[i]
            tempsorted.sort()
            
            ordtojjoin=[]
            
            for i in range(len(tempor)):
                ordtojjoin.append(tempor.index(tempsorted[i]))
            
            if ordtojjoin==[]:
                titletouse=''
            else:
                titletouse=str_rem[ordtojjoin[0]]
                for i in range(len(ordtojjoin)-1):
                    titletouse=' '.join([titletouse,str_rem[ordtojjoin[i+1]]])
            
            return [short_leg,titletouse]
        except Exception as Argument:
            return [long_leg,'']
            self.genLogforException(Argument)
    
    def autogenX (self):
        try:
            self.dlistGr=self.getitems(self.xyzmaker.ui.dataGrList)
            if self.xyzmaker.ui.addautocb.isChecked():
                self.xlistGr=self.legshorten(self.getitems(self.xyzmaker.ui.dataGrList))[0]
                for i in range(len(self.dlistGr)):
                    self.xlistGr[i]=self.xlistGr[i].replace(' ','')
                    self.xlistGr[i]=self.xlistGr[i].replace(self.xyzmaker.ui.unitGr.text(),'')
                self.xyzmaker.ui.xGrList.clear()
                self.xyzmaker.ui.xGrList.addItems(self.xlistGr)
            self.xdataGr=np.array(self.xlistGr).astype(float)
            self.xdataGrnotsort=np.array(self.xlistGr).astype(float)
            self.xdataGr.sort()
        except Exception as Argument:
            self.genLogforException(Argument)
    def addtoGroup(self):
        try:
            dtemp3D=dict()
            lenlist=[]
            tempdictname={self.xyzmaker.ui.Grname.text():[self.dlistGr,self.xlistGr]}
            for i in range(self.xyzmaker.ui.xGrList.count()):
                lenlist.append(len(self.dGrtemp[self.dlistGr[i]]['x']))
            maxlen=max(lenlist)
            indtomax=lenlist.index(maxlen)
            z=[[0]*(self.xyzmaker.ui.xGrList.count()) for _ in range(maxlen)]
            z=np.array(z).astype(float)
            z[:][:]=np.nan
            for i in range(self.xyzmaker.ui.xGrList.count()):
                indtotake=self.v2in(self.xdataGrnotsort,self.xdataGr[i])
                z[0:len(self.dGrtemp[self.dlistGr[indtotake]]['y']),i]=self.dGrtemp[self.dlistGr[indtotake]]['y']
            y=self.dGrtemp[self.dlistGr[indtomax]]['x']
            x=self.xdataGr
            tempdata={'a':self.xyzmaker.ui.Grname.text(), 't':x, 'w':y, 'd':z}
            dtemp3D[self.xyzmaker.ui.Grname.text()]=tempdata
            if self.dGrnames==[] or self.dGrnames[-1]!=self.xyzmaker.ui.Grname.text():
                tempbtn=QPushButton(self.xyzmaker.ui)
                tempbtn.setText(self.xyzmaker.ui.Grname.text())
                self.grdatanames={**self.grdatanames,**tempdictname}
                tempbtn.clicked.connect(lambda itemstoadd: self.grnameClicked(itemstoadd=self.grdatanames[tempbtn.text()]))
                self.xyzmaker.ui.datagenlay.addWidget(tempbtn)
                self.dGr={**self.dGr, **dtemp3D}
                self.dGrnames.append(self.xyzmaker.ui.Grname.text())
        except Exception as Argument:
            self.genLogforException(Argument)
    def remfrGr(self):
        try:
            lastind=self.xyzmaker.ui.datagenlay.count()-1
            self.xyzmaker.ui.datagenlay.itemAt(lastind).widget().deleteLater()
            self.xyzmaker.ui.datagenlay.removeWidget(self.xyzmaker.ui.datagenlay.itemAt(lastind).widget())
            del self.dGr[self.dGrnames[lastind]]
            del self.dGrnames[lastind]
        except Exception as Argument:
            self.genLogforException(Argument)
    def grtomain(self):
        try:
            self.ui.dataBox.addItems(self.dGrnames)
            self.d={**self.d, **self.dGr}
        except Exception as Argument:
            self.genLogforException(Argument)
    def grnameClicked(self,itemstoadd):
        try:
            tempdlg=QDialog()
            tempdlg.resize(250,300)
            tempdlg.setMaximumSize(250,300)
            templay=QtWidgets.QHBoxLayout(tempdlg)
            dlistw=QListWidget()
            dlistw.setMaximumSize(150,300)
            dlistw.addItems(itemstoadd[0])
            xlistw=QListWidget()
            xlistw.addItems(itemstoadd[1])
            xlistw.setMaximumSize(100,300)
            templay.addWidget(dlistw)
            templay.addWidget(xlistw)
            tempdlg.exec()
        except Exception as Argument:
            self.genLogforException(Argument)
    def draw_blit(self,figcanvas,ax,line,axbackground):
        figcanvas.restore_region(axbackground)
        ax.draw_artist(line)
        figcanvas.blit(ax.bbox)
        figcanvas.flush_events()
    def resizeEvent(self, event):
        newSize = self.geometry()
        self.screenSizeChanged.emit(newSize)
        return super().resizeEvent(event)
    def showPopInfo(self,labelToShow,widgetToShowOn=None,durationToShow = 2,color = 'green'):
        # labelToShow='this is information'
        # durationToShow = 4
        # locationToShow = [500,500]
        
        # labelToShow=arr[0]
        # durationToShow = arr[1]
        # locationToShow = arr[2]
        uisize = widgetToShowOn.mapToGlobal(QPoint(0, 0))
        locationToShow = [int(uisize.x()+widgetToShowOn.geometry().width()/2),int(uisize.y()+widgetToShowOn.geometry().height()/4)]

        start = time.time()
        testlabel = QLabel()
        testlabel.setStyleSheet(''.join(["QLabel { background-color : white; color : ",color,"; }"]))
        testlabel.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        testlabel.setText(labelToShow)

        # eff = QGraphicsOpacityEffect()
        # testlabel.setGraphicsEffect(eff)
        # a = QPropertyAnimation(eff,b"opacity")
        # a.setDuration(durationToShow*1000*3)
        # a.setStartValue(0)
        # a.setEndValue(1)
        # a.setEasingCurve(QEasingCurve.InBack)
        # a.start(QPropertyAnimation.DeleteWhenStopped)

        eff = QGraphicsOpacityEffect()
        testlabel.setGraphicsEffect(eff)
        a = QPropertyAnimation(eff,b"opacity")
        a.setDuration(int(durationToShow*1000*3))
        a.setStartValue(1)
        a.setEndValue(0.2)
        a.setEasingCurve(QEasingCurve.OutBack)
        a.start(QPropertyAnimation.DeleteWhenStopped)

        testlabel.move(locationToShow[0],locationToShow[1])
        testlabel.show()
        #testlabel.raise_()

        while time.time()-start<=durationToShow:
            QApplication.processEvents()

        testlabel.close()
class PlotCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100, left=0.075, bottom=0.12, right=0.95, top=0.9):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.subplots_adjust(left, bottom, right, top)
        self.figure=fig
        self.axes = fig.add_subplot(111)
        super(PlotCanvas, self).__init__(fig)
        self.setParent(parent)
class impOptionsWindow(QDialog):
    def __init__(self):
        super().__init__()
        DataDir = getResourcePath("uis")
        uiPath = DataDir / 'impOptions.ui'
        self.ui = uic.loadUi(uiPath,self)
        self.ui.setWindowTitle('Preset options')
class funOptionsWindow(QDialog):
    def __init__(self):
        super().__init__()
        DataDir = getResourcePath("uis")
        uiPath = DataDir / 'funOptions.ui'
        self.ui = uic.loadUi(uiPath,self)
        self.ui.setWindowTitle('Function options')
class pyFunWindow(QDialog):
    def __init__(self):
        super().__init__()
        DataDir = getResourcePath("uis")
        uiPath = DataDir / 'pyFuns.ui'
        self.ui = uic.loadUi(uiPath,self)
        self.ui.setWindowTitle('Import Python functions')
class fitWindow(QDialog):
    screenSizeChanged = QtCore.pyqtSignal(QtCore.QRect)
    def __init__(self,app,mainDialog):
        super().__init__()
        DataDir = getResourcePath("uis")
        uiPath = DataDir / 'Fit.ui'
        self.ui = uic.loadUi(uiPath,self)
        self.ui.setWindowTitle('Fit the Data')
        self.fitfigcanvas=PlotCanvas(self, width=7.41, height=4.61, bottom=0.1, dpi=100)
        self.ui.layoutFit.addWidget(self.fitfigcanvas,1, 0, 1, 2)
        indexFit=self.ui.layoutFit.count()-1
        self.mFit=self.ui.layoutFit.itemAt(indexFit).widget()
        self.axFit=self.mFit.axes
        self.axFit.ticklabel_format(axis='y',style='sci',scilimits=(-2,2))
        self.figFit=self.mFit.figure
        self.app = app
        self.currWindowSize = self.app.desktop().geometry()
        self.parcounter = 0 #Counts the # parameters need to be added
        self.parcounterList = [] #Needs to be tracked when function is removed
        self.ui.optparams.setReadOnly(True)
        self.ui.optErrPars.setReadOnly(True)
        self.ui.fValueEdit.setReadOnly(True)
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(mainDialog.loadDefBtn)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(mainDialog.saveDefBtn)
        
        self.modelsW=modelsWindow()
        self.modelsButton.clicked.connect(self.showModels)
        self.modelsList = []
        self.modelAICs = []
        
        # self.mbar = self.menuAdder()
        # #self.mbar.setObjectName("tabMenuBar")
        # self.mbar.setMaximumHeight(50)
        # self.mbar.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.Maximum)
        # self.fitMenuLayout.addWidget(self.mbar)
        
        self.cpfitbtn=QtWidgets.QPushButton(self)
        self.cpfitbtn.setMaximumSize(QtCore.QSize(32, 32))
        self.cpfitbtn.setText('C')
        self.cpfitbtn.setToolTip('Press to Copy to Clipboard')
        self.ui.layoutFit.addWidget(self.cpfitbtn,0, 1, 1, 1)
        
        self.ui.layoutFit.addWidget(NavigationToolbar_new(self.mFit, self.axFit,self,isGraph = False),0, 0, 1, 1)
        index=self.ui.layoutFit.count()-1
        self.fitTlb = self.ui.layoutFit.itemAt(index).widget()
        self.fitTlb.setMaximumSize(QtCore.QSize(2250, int(self.currWindowSize.height()*0.015)))
        
        self.eqcanvas=PlotCanvas(self, width=17.41, height=2,dpi=100)
        self.eqcanvas.setMaximumSize(QtCore.QSize(3000, int(self.currWindowSize.height()*0.05)))
        self.ui.layoutFun.addWidget(self.eqcanvas,1, 0, 1, 2)
        indexFun=self.ui.layoutFun.count()-1
        self.mFun=self.ui.layoutFun.itemAt(indexFun).widget()
        self.axFun=self.mFun.axes
        self.axFun.axis('off')
        
        self.cpeqbtn=QtWidgets.QPushButton(self)
        self.cpeqbtn.setMaximumSize(QtCore.QSize(32, 32))
        self.cpeqbtn.setText('C')
        self.cpeqbtn.setToolTip('Press to Copy to Clipboard')
        self.ui.layoutFun.addWidget(self.cpeqbtn,0, 1, 1, 1)
        
        self.ui.layoutFun.addWidget(NavigationToolbar_new(self.mFun,self.axFun, self, isGraph = False,isEquation = True),0, 0, 1, 1)
        
        index=self.ui.layoutFun.count()-1
        self.eqTlb=self.ui.layoutFun.itemAt(index).widget()
        self.eqTlb.setMaximumSize(QtCore.QSize(1500, int(self.currWindowSize.height()*0.015)))
        self.screenSizeChanged.connect(lambda newSize: self.resizeUI2(newSize))
        self.exceptionLogLocation = self.makeFolderinDocuments('.logs')
    def showModels(self):
        uisize = self.ui.modelsButton.mapToGlobal(QPoint(0, 0))
        self.modelsW.move(int(uisize.x()-uisize_main.width()*0.05),int(uisize.y())) 
        self.modelsW.show()
    def makeFolderinDocuments(self, foldName): 
        foldDir = getResourcePath(os.path.expanduser('~'))/'Documents'/'Graphxyz'
        os.makedirs(foldDir, exist_ok = True)
        foldDir = foldDir / foldName
        os.makedirs(foldDir, exist_ok = True)
        return foldDir
    def genLogforException(self, Argument):
        logLoc = self.exceptionLogLocation
        logLoc = logLoc / 'Exception logs.txt'
        f = open(logLoc, "a")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f.write(''.join(['\n',str([exc_tb.tb_lineno,Argument]),datetime.now(). strftime("%m/%d/%Y, %H:%M:%S")]))
        f.close()
    def resizeUI2(self,newSize):
        refDPI = 120
        newDPI=QApplication.screens()[0].physicalDotsPerInch()
        #print(newDPI)
        self.height = newSize.height()
        self.width = newSize.width()
        self.heightold = 900
        self.widthold = 1440
        font_coef = (np.sqrt(self.heightold**2+self.widthold**2) / np.sqrt(self.height**2+self.width**2))
        self.k_vert=self.height/self.heightold
        self.k_hor=self.width/self.widthold
        self.k_font = (self.k_vert + self.k_hor)/2
        #self.k_font = max(self.k_vert*newDPI/refDPI,self.k_hor*newDPI/refDPI)
        self.k_font2=max(self.k_vert,self.k_hor)*newDPI/refDPI
        
        #self.ui.controlwindowframe.resize(self.ui.frameDyn.width(),self.ui.controlwindowframe.height())
        
        comp1=self.ui.findChildren(QPushButton)
        comp2=self.ui.findChildren(QLabel)
        comp3=self.ui.findChildren(QLineEdit)
        comp4=self.ui.findChildren(QRadioButton)
        comp5=self.ui.findChildren(QCheckBox)
        comp6=self.ui.findChildren(QComboBox)
        comp7=self.ui.findChildren(QListWidget)
        
        comp=comp1+comp2+comp3+comp4+comp5+comp6+comp7
        for ci in range(len(comp)):
            compi=comp[ci]
            try:
                fonttemp=compi.font()
                fontitype=fonttemp.family()
                if platform.system().lower()=='windows':
                    #print(font_coef*1*self.k_font)
                    compi.setFont(QFont(fontitype,int(self.orFonts[ci]*1))) #This needs to be refined, right now it kinda does the job
                else:
                    compi.setFont(QFont(fontitype,max(int(self.orFonts[ci]*0.9*self.k_font2),10)))
            except Exception as Argument:
                self.genLogforException(Argument)
        try:
            minToolbarWidth_win = int(self.app.activeWindow().geometry().height()*0.03)
            minToolbarWidth_mac = int(self.app.activeWindow().geometry().height()*0.03)
            #print(minToolbarWidth_mac)
            # if platform.system().lower()=='windows':
            #     self.mdynTlb.setMaximumSize(QtCore.QSize(1250, max(int(25*self.k_vert),minToolbarWidth_win) ))
            #     self.mspecTlb.setMaximumSize(QtCore.QSize(1250, max(int(25*self.k_vert),minToolbarWidth_win) ))
            #     self.m2DTlb.setMaximumSize(QtCore.QSize(1250, max(int(25*self.k_vert),minToolbarWidth_win) ))
            # else:
            #     self.mdynTlb.setMaximumSize(QtCore.QSize(1250, max(int(25*self.k_vert),minToolbarWidth_mac) ))
            #     self.mspecTlb.setMaximumSize(QtCore.QSize(1250, max(int(25*self.k_vert),minToolbarWidth_mac) ))
            #     self.m2DTlb.setMaximumSize(QtCore.QSize(1250, max(int(25*self.k_vert),minToolbarWidth_mac) ))
            if platform.system().lower()=='windows':
                self.fitTlb.setMaximumSize(QtCore.QSize(1250, minToolbarWidth_win ))
                self.eqTlb.setMaximumSize(QtCore.QSize(1250, minToolbarWidth_win ))
            else:
                self.fitTlb.setMaximumSize(QtCore.QSize(1250, minToolbarWidth_win ))
                self.eqTlb.setMaximumSize(QtCore.QSize(1250, minToolbarWidth_win ))
        except Exception as Argument:
            self.genLogforException(Argument)
        #self.fontBtn(str(int(9*self.k_font)))
    def resizeEvent(self, event):
        newSize = self.geometry()
        self.screenSizeChanged.emit(newSize)
        return super().resizeEvent(event)
class xyzMakerWindow(QDialog):
    def __init__(self):
        super().__init__()
        DataDir = getResourcePath("uis")
        uiPath = DataDir / '3dmaker.ui'
        self.ui = uic.loadUi(uiPath,self)
        
        self.ui.setWindowTitle('3D Maker')
        self.ui.datagenlay = QtWidgets.QGridLayout(self.ui.dataGenList)
class modelsWindow(QDialog):
    def __init__(self):
        super().__init__()
        DataDir = getResourcePath("uis")
        uiPath = DataDir / 'models.ui'
        self.ui = uic.loadUi(uiPath,self)
        self.ui.setWindowTitle('Compare models')
class sliderObj(QFrame):
    def __init__(self,sliderno,app):
        super().__init__()
        self.app = app
        self.currWindowSize = self.app.desktop().geometry()
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setObjectName(''.join(['slider',str(sliderno)]))
        self.setMinimumSize(QtCore.QSize(int(0.03*self.currWindowSize.width()), 150))
        self.setMaximumSize(QtCore.QSize(int(0.045*self.currWindowSize.width()), 5000))
        #self.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Preferred)
        gridlayout=QtWidgets.QGridLayout(self)
        gridlayout.setContentsMargins(0,0,0,0)
        gridlayout.setSpacing(0)
        self.pslider=QSlider(QtCore.Qt.Vertical)
        self.pslider.setTickPosition(QtWidgets.QSlider.NoTicks)
        gridlayout.addWidget(self.pslider,2,0,1,1)
        plabel=QLabel(''.join(['p',str(sliderno)]))
        plabel.setAlignment(QtCore.Qt.AlignCenter)
        gridlayout.addWidget(plabel,0,0,1,2)
        self.slmax=QLineEdit('50')
        self.slmax.setAlignment(QtCore.Qt.AlignCenter)
        self.slval=QLineEdit('25')
        self.slval.setAlignment(QtCore.Qt.AlignCenter)
        self.slmin=QLineEdit('0')
        self.slmin.setAlignment(QtCore.Qt.AlignCenter)
        gridlayout.addWidget(self.slmax,1,0,1,2)
        gridlayout.addWidget(self.slval,2,1,1,1)
        gridlayout.addWidget(self.slmin,3,0,1,2)
        #gridlayout.addWidget(QLineEdit(''.join(['p',str(sliderno)])),0,0,1,1)
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.Ignored)
        self.slacno=0.0005
        self.slacc=max(int(1/((float(self.slmax.text())-float(self.slmin.text()))*self.slacno)),1)
        self.pslider.setMaximum(int(float(self.slmax.text())*self.slacc))
        self.pslider.setMinimum(int(float(self.slmin.text())*self.slacc))
        self.pslider.setSingleStep(int(1))
        self.pslider.valueChanged.connect(self.pslidervaluechanged)
        self.pslider.sliderReleased.connect(self.psliderrelease)
        self.slmax.editingFinished.connect(self.maxlimchanged)
        self.slmin.editingFinished.connect(self.minlimchanged)
        self.slval.editingFinished.connect(self.slidernumchanged)
        self.pslider.setValue(int(float(self.slval.text())*self.slacc))
        #self.compNo = float(1/self.slacc*100) #To check whether limit needs to be changed
        self.exceptionLogLocation = self.makeFolderinDocuments('.logs')
    def makeFolderinDocuments(self, foldName): 
        foldDir = getResourcePath(os.path.expanduser('~'))/'Documents'/'Graphxyz'
        os.makedirs(foldDir, exist_ok = True)
        foldDir = foldDir / foldName
        os.makedirs(foldDir, exist_ok = True)
        return foldDir
    def genLogforException(self, Argument):
        logLoc = self.exceptionLogLocation
        logLoc = logLoc / 'Exception logs.txt'
        f = open(logLoc, "a")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f.write(''.join(['\n',str([exc_tb.tb_lineno,Argument]),datetime.now(). strftime("%m/%d/%Y, %H:%M:%S")]))
        f.close()
    def psliderrelease(self):
        pass
    def pslidervaluechanged(self):
        #self.pslider.setTracking(True)
        self.slval.setText(self.num2str(self.pslider.value()/self.slacc,4))
        #self.pslider.setTracking(False)
    def maxlimchanged(self,needvalSet=True,needminSet=True,needmaxSet=True):
        try:
            oldval=float(self.slval.text())
            self.slacc=max(int(1/((float(self.slmax.text())-float(self.slmin.text()))*self.slacno)),1)
            self.compNo = float(1/self.slacc*100) #To check whether limit needs to be changed
            newpos=int(oldval*self.slacc)
            if needmaxSet:
                self.pslider.setMaximum(int(float(self.slmax.text())*self.slacc)) #fix this step 10 later
            if needminSet:
                self.pslider.setMinimum(int(float(self.slmin.text())*self.slacc))
            if needvalSet:
                self.pslider.setValue(newpos)
            self.slval.setText(self.num2str(self.pslider.value()/self.slacc,4))
        except Exception as Argument:
            self.genLogforException(Argument)
    def minlimchanged(self,needvalSet=True,needminSet=True,needmaxSet=True):
        try:
            oldval=float(self.slval.text())
            self.slacc=max(int(1/((float(self.slmax.text())-float(self.slmin.text()))*self.slacno)),1)
            self.compNo = float(1/self.slacc*100) #To check whether limit needs to be changed
            newpos=int(oldval*self.slacc)
            if needminSet:
                self.pslider.setMinimum(int(float(self.slmin.text())*self.slacc))
            if needmaxSet:
                self.pslider.setMaximum(int(float(self.slmax.text())*self.slacc))
            if needvalSet:
                self.pslider.setValue(newpos)
            self.slval.setText(self.num2str(self.pslider.value()/self.slacc,4))
        except Exception as Argument:
            self.genLogforException(Argument)
    def slidernumchanged(self):
        try:
            minNo = 70
            if abs(float(self.slval.text()))>=float(1/self.slacc*minNo):
                #print('default')
                if int(float(self.slval.text())*self.slacc)>self.pslider.maximum():
                    #print('1')
                    oldval=float(self.slval.text())
                    self.pslider.setMaximum(int((float(self.slval.text())+abs(float(self.slval.text()))*0.5)*self.slacc)) #fix this step 10 later
                    self.pslider.setMinimum(int(float(self.slmin.text())*self.slacc))
                    self.slmax.setText(self.num2str(self.pslider.maximum()/self.slacc,4))
                    self.maxlimchanged(needvalSet=False)
                    self.slacc=max(int(1/((float(self.slmax.text())-float(self.slmin.text()))*self.slacno)),1)
                    newpos=int(oldval*self.slacc)
                    self.pslider.setValue(newpos)
                elif int(float(self.slval.text())*self.slacc)<=self.pslider.maximum() and int(float(self.slval.text())*self.slacc)>=self.pslider.minimum():
                    #print('2')
                    oldval=float(self.slval.text())
                    self.slacc=max(int(1/((float(self.slmax.text())-float(self.slmin.text()))*self.slacno)),1)
                    #self.slacc = int(self.slacc-0.01*self.slacc)
                    newpos=int(oldval*self.slacc)
                    #self.pslider.setMaximum(int(float(self.slmax.text())*1.01*self.slacc)) #fix this step 10 later
                    #self.pslider.setMinimum(int(float(self.slmin.text())*1.01*self.slacc))
                    self.pslider.setValue(newpos)
                elif int(float(self.slval.text())*self.slacc)<self.pslider.minimum():
                    #print('3')
                    oldval=float(self.slval.text())
                    self.pslider.setMaximum(int(float(self.slmax.text())*self.slacc)) 
                    self.pslider.setMinimum(int((float(self.slval.text())-abs(float(self.slval.text())*0.5))*self.slacc))
                    self.slmin.setText(self.num2str(self.pslider.minimum()/self.slacc,4))
                    self.minlimchanged(needvalSet=False)
                    self.slacc=max(int(1/((float(self.slmax.text())-float(self.slmin.text()))*self.slacno)),1)
                    newpos=int(oldval*self.slacc)
                    self.pslider.setValue(newpos)
            elif abs(float(self.slval.text()))<float(1/self.slacc*minNo):
                #print('divided')
                #print(abs(float(self.slval.text())))
                #print(float(1/self.slacc*100))
                if int(float(self.slval.text())*self.slacc)>self.pslider.maximum():
                    #print('1')
                    oldval=float(self.slval.text())
                    self.slacc=max(int(1/((float(self.slmax.text())-float(self.slmin.text()))*self.slacno)),1)
                    newpos=int(oldval*self.slacc)
                    self.pslider.setMaximum(int((float(self.slval.text())+abs(float(self.slval.text()))*0.5)*self.slacc)) #fix this step 10 later
                    self.pslider.setMinimum(int(float(self.slmin.text())*self.slacc))
                    self.slmax.setText(self.num2str(self.pslider.maximum()/self.slacc,4))
                    self.maxlimchanged(needvalSet=False)
                    self.pslider.setValue(newpos)
                if int(float(self.slval.text())*self.slacc)<=self.pslider.maximum() and int(float(self.slval.text())*self.slacc)>=self.pslider.minimum():
                    #print('2')
                    oldval=float(self.slval.text())
                    if abs(float(self.slval.text())) == float(self.slval.text()):
                        self.pslider.setMaximum(int(2*minNo)) #fix this step 10 later
                        self.pslider.setMinimum(int(float(self.slmin.text())*self.slacc))
                        self.slmax.setText(self.num2str(self.pslider.maximum()/self.slacc,4))
                        self.maxlimchanged(needvalSet=False)
                    else:
                        self.pslider.setMaximum(int(float(self.slmax.text())*self.slacc)) #fix this step 10 later
                        self.pslider.setMinimum(int(2*minNo))
                        self.slmin.setText(self.num2str(self.pslider.minimum()/self.slacc,4))
                        self.minlimchanged(needvalSet=False)
                    #self.slacc=max(int(1/((float(self.slmax.text())-float(self.slmin.text()))*self.slacno)),1)
                    newpos=int(oldval*self.slacc)
                    self.pslider.setValue(newpos)
                elif int(float(self.slval.text())*self.slacc)<self.pslider.minimum():
                    #print('3')
                    oldval=float(self.slval.text())
                    self.pslider.setMaximum(int(float(self.slmax.text())*self.slacc)) 
                    self.pslider.setMinimum(int((float(self.slval.text())-abs(float(self.slval.text())*0.5))*self.slacc))
                    self.slmin.setText(self.num2str(self.pslider.minimum()/self.slacc,4))
                    self.minlimchanged(needvalSet=False)
                    self.slacc=max(int(1/((float(self.slmax.text())-float(self.slmin.text()))*self.slacno)),1)
                    newpos=int(oldval*self.slacc)
                    self.pslider.setValue(newpos)
        except Exception as Argument:
            self.genLogforException(Argument)
        
        # try:
        #     if int(float(self.slval.text())*self.slacc)>self.pslider.maximum():
        #         oldval=float(self.slval.text())
        #         self.slacc=max(int(1/((float(self.slmax.text())-float(self.slmin.text()))*self.slacno)),1)
        #         newpos=int(oldval*self.slacc)
        #         self.pslider.setMaximum(int((float(self.slval.text())+float(self.slval.text())*0.5)*self.slacc)) #fix this step 10 later
        #         self.pslider.setMinimum(int(float(self.slmin.text())*self.slacc))
        #         self.pslider.setValue(newpos)
        #         self.slmax.setText(self.num2str(self.pslider.maximum()/self.slacc,4))
        #     elif int(float(self.slval.text())*self.slacc)<self.pslider.minimum():
        #         oldval=float(self.slval.text())
        #         self.slacc=max(int(1/((float(self.slmax.text())-float(self.slmin.text()))*self.slacno)),1)
        #         newpos=int(oldval*self.slacc)
        #         self.pslider.setMaximum(int(float(self.slmax.text())*self.slacc)) 
        #         self.pslider.setMinimum(int((float(self.slval.text())-abs(float(self.slval.text())*0.5))*self.slacc))
        #         self.pslider.setValue(newpos)
        #         self.slmin.setText(self.num2str(self.pslider.minimum()/self.slacc,4))
        #     self.pslider.setValue(int(float(self.slval.text())*self.slacc))
        # except Exception as Argument:
        #     self.genLogforException(Argument)
            # else:
                
            # if int(float(self.slval.text())*self.slacc)>self.pslider.maximum():
            #     oldval=float(self.slval.text())
            #     self.slacc=max(int(1/((float(self.slmax.text())-float(self.slmin.text()))*self.slacno)),1)
            #     newpos=int(oldval*self.slacc)
            #     #self.pslider.setMaximum(int((float(self.slval.text())+float(self.slval.text())*0.5)*self.slacc)) #fix this step 10 later
            #     #self.pslider.setMinimum(int((float(self.slval.text())-abs(float(self.slval.text())*0.5))*self.slacc))
            #     #self.pslider.setValue(newpos)
            #     self.slmax.setText(self.num2str((float(self.slval.text())+abs(float(self.slval.text())*0.45)),4))
            #     self.maxlimchanged(needvalSet=False)
            #     self.slmin.setText(self.num2str((float(self.slval.text())-abs(float(self.slval.text())*0.55)),4))
            #     self.minlimchanged(needvalSet=False)
            #     #self.pslider.setValue(newpos)
            #     #self.slmax.setText(self.num2str(self.pslider.maximum()/self.slacc,4))
            #     #self.slmin.setText(self.num2str(self.pslider.minimum()/self.slacc,4))
            #     #print(int(float(self.slval.text())))
            #     #print(newpos/self.slacc)
            # elif int(float(self.slval.text())*self.slacc)<self.pslider.minimum():
            #     oldval=float(self.slval.text())
            #     self.slacc=max(int(1/((float(self.slmax.text())-float(self.slmin.text()))*self.slacno)),1)
            #     newpos=int(oldval*self.slacc)
            #     #self.pslider.setMaximum(int((float(self.slval.text())+float(self.slval.text())*0.5)*self.slacc)) #fix this step 10 later
            #     #self.pslider.setMinimum(int((float(self.slval.text())-abs(float(self.slval.text())*0.5))*self.slacc))
            #     #self.pslider.setValue(newpos)
            #     self.slmin.setText(self.num2str((float(self.slval.text())-abs(float(self.slval.text())*0.55)),4))
            #     self.minlimchanged(needvalSet=False)
            #     self.slmax.setText(self.num2str((float(self.slval.text())+abs(float(self.slval.text())*0.45)),4))
            #     self.maxlimchanged(needvalSet=False)
            #     #self.pslider.setValue(newpos)
            #     #self.slmax.setText(self.num2str(self.pslider.maximum()/self.slacc,4))
            #     #self.slmin.setText(self.num2str(self.pslider.minimum()/self.slacc,4))
            #     #print(int(float(self.slval.text())))
            #     #print(newpos/self.slacc)
            # else:
    def num2str(self,x,p):
        """
        returns a string representation of x formatted with a precision of p
    
        Based on the webkit javascript implementation taken from here:
        https://code.google.com/p/webkit-mirror/source/browse/JavaScriptCore/kjs/number_object.cpp
        """
    
        x = float(x)
    
        if x == 0.:
            return "0." + "0"*(p-1)
    
        out = []
    
        if x < 0:
            out.append("-")
            x = -x
    
        e = int(math.log10(x))
        tens = math.pow(10, e - p + 1)
        n = math.floor(x/tens)
    
        if n < math.pow(10, p - 1):
            e = e -1
            tens = math.pow(10, e - p+1)
            n = math.floor(x / tens)
    
        if abs((n + 1.) * tens - x) <= abs(n * tens -x):
            n = n + 1
    
        if n >= math.pow(10,p):
            n = n / 10.
            e = e + 1
    
        m = "%.*g" % (p, n)
    
        if e < -2 or e >= p:
            out.append(m[0])
            if p > 1:
                out.append(".")
                out.extend(m[1:p])
            out.append('e')
            if e > 0:
                out.append("+")
            out.append(str(e))
        elif e == (p -1):
            out.append(m)
        elif e >= 0:
            out.append(m[:e+1])
            if e+1 < len(m):
                out.append(".")
                out.extend(m[e+1:])
        else:
            out.append("0.")
            out.extend(["0"]*-(e+1))
            out.append(m)
        return "".join(out)
class clrDlg(QDialog):
    def __init__(self,leftright,uisize,defcolor,cListItems):
        super().__init__()
        self.setWindowTitle(leftright)
        self.clrgen_hex=defcolor
        self.clrgen_rgb=clrs.to_rgb(self.clrgen_hex)
        screenWidth = uisize.width();
        screenHeight = uisize.height();
        left = uisize.left();
        bottom = uisize.bottom();
        self.resize(int(screenWidth/12),int(screenHeight/3.5))
        if leftright=='Left Figure':
            self.move(int(left+screenWidth/2.5),int(bottom-screenHeight/2.2))
        else:
            self.move(int(left+screenWidth/1.1),int(bottom-screenHeight/2.2))
        grdly=QtWidgets.QGridLayout(self)
        clrBtn=QtWidgets.QPushButton(self)
        clrBtn.setMaximumSize(QtCore.QSize(150, 30))
        clrBtn.setText('Choose')
        clrAdd=QtWidgets.QPushButton(self)
        clrAdd.setMaximumSize(QtCore.QSize(75, 30))
        clrAdd.setText('+')
        clrRem=QtWidgets.QPushButton(self)
        clrRem.setMaximumSize(QtCore.QSize(75, 30))
        clrRem.setText('-')
        self.clrtext=QtWidgets.QLineEdit(self)
        self.clrtext.setText(self.clrgen_hex)
        self.clrtext.setStyleSheet(''.join(['color: black; background-color: ',self.clrgen_hex]))
        self.cList=QtWidgets.QListWidget(self)
        self.addItems(self.cList,cListItems)
        grdly.addWidget(self.clrtext, 0, 0, 1, 2)
        grdly.addWidget(clrBtn, 1, 0, 1, 2)
        grdly.addWidget(clrAdd, 2, 0, 1, 1)
        grdly.addWidget(clrRem, 2, 1, 1, 1)
        grdly.addWidget(self.cList, 3, 0, 1, 2)
        
        clrBtn.clicked.connect(self.openColorDialog)
        clrAdd.clicked.connect(self.claddBtn)
        clrRem.clicked.connect(self.clremBtn)
    def closeEvent(self,event):
        self.clrlist=[(1,1,1)]
        self.defcolor=self.clrgen_hex
        self.cListItems=self.getItems(self.cList)
    def openColorDialog(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.clrgen_rgb=clrs.to_rgb(color.name())
            self.clrgen_hex=color.name()
        self.clrtext.setText(self.clrgen_hex)
        self.clrtext.setStyleSheet(''.join(['color: black; background-color: ',self.clrgen_hex]))
    def claddBtn(self):
        items = [0]*self.cList.count()
        listc=self.cList
        itemtoadd=QListWidgetItem(self.clrtext.text())
        itemtoadd.setBackground(QColor(self.clrgen_hex))
        if not items:
            listc.addItem(itemtoadd)
        elif listc.selectedItems():
            for listitems in listc.selectedItems():
                listc.insertItem(listc.row(listitems)+1,itemtoadd)
        else:
            listc.insertItem(0,itemtoadd)
    def clremBtn(self):
        listc=self.cList
        if listc.selectedItems():
            for listitems in listc.selectedItems():
                listc.takeItem(listc.row(listitems))
        else:
            listc.takeItem(listc.row(listc.item(0)))
    def addItems(self,tolist,fromstr):
        tolist.clear()
        for i in range(len(fromstr)):
            itemtoadd=QListWidgetItem(fromstr[i])
            itemtoadd.setBackground(QColor(fromstr[i]))
            tolist.addItem(itemtoadd)
    def getItems(self,fromthislist):
        strlist=[0]*self.cList.count()
        for i in range(fromthislist.count()):
            strlist[i]=fromthislist.item(i).text()
        return strlist
class optsWindow(QDialog):
    def __init__(self,leftright,xyzmode):
        super().__init__()
        self.setWindowTitle('Graph Options')
        self.optlayout=QtWidgets.QVBoxLayout(self)
        if not leftright == "Top Figure":
            
            self.absz=QtWidgets.QCheckBox(self)
            self.flipz=QtWidgets.QCheckBox(self)
            self.semilogz=QtWidgets.QCheckBox(self)
            self.semilogx=QtWidgets.QCheckBox(self)
            self.holdcb=QtWidgets.QCheckBox(self)
            self.auto_zlimcb=QtWidgets.QCheckBox(self)
            self.auto_xlimcb=QtWidgets.QCheckBox(self)
            self.needShortLeg = QtWidgets.QCheckBox(self)
            
            self.auto_xlimcb.setChecked(True)
            self.auto_zlimcb.setChecked(True)
            self.needShortLeg.setChecked(True)
            # if leftright=='Left Figure':
            #     self.auto_zlimcb.setChecked(True)
            
            self.holdcb.setText("Hold Current Line(s)")
            if xyzmode:
                self.absz.setText("|Z|")
                self.flipz.setText("-Z")
                self.semilogz.setText("semilog(Z)")
                self.auto_zlimcb.setText("Auto Adjust Limits: Z")
                if leftright=='Left Figure':
                    self.semilogx.setText("semilog(X)")
                    self.auto_xlimcb.setText("Auto Adjust Limits: X")
                else:
                    self.semilogx.setText("semilog(Y)")
                    self.auto_xlimcb.setText("Auto Adjust Limits: Y")
            else:
                self.absz.setText("|Y|")
                self.flipz.setText("-Y")
                self.semilogz.setText("semilog(Y)")
                self.semilogx.setText("semilog(X)")
                self.auto_zlimcb.setText("Auto Adjust Limits: Y")
                self.auto_xlimcb.setText("Auto Adjust Limits: X")
            self.needShortLeg.setText("Short Legends")
            
            self.optlayout.addWidget(self.absz)
            self.optlayout.addWidget(self.flipz)
            self.optlayout.addWidget(self.semilogz)
            self.optlayout.addWidget(self.semilogx)
            self.optlayout.addWidget(self.holdcb)
            self.optlayout.addWidget(self.auto_xlimcb)
            self.optlayout.addWidget(self.auto_zlimcb)
            self.optlayout.addWidget(self.needShortLeg)
        else:
            self.mirrorX=QtWidgets.QCheckBox(self)
            self.mirrorX.setText("Mirror in X")
            self.mirrorY=QtWidgets.QCheckBox(self)
            self.mirrorY.setText("Mirror in Y")
            self.optlayout.addWidget(self.mirrorX)
            self.optlayout.addWidget(self.mirrorY)
class multWindow(QDialog):
    def __init__(self,sourceLabels):
        super().__init__()
        self.setWindowTitle(''.join(['Choose multiple',sourceLabels[0],' to ',sourceLabels[1].lower()]))
        self.optlayout=QtWidgets.QVBoxLayout(self)
        self.list = QListWidget(self)
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.button = QPushButton(self)
        self.button.setText(sourceLabels[1])
        self.button.setMaximumWidth(100)
        self.button.setMaximumHeight(32)
        self.optlayout.addWidget(self.list)
        self.optlayout.addWidget(self.button)
class LatexVisitor(ast.NodeVisitor):

    def prec(self, n):
        return getattr(self, 'prec_'+n.__class__.__name__, getattr(self, 'generic_prec'))(n)

    def visit_Call(self, n):
        func = self.visit(n.func)
        args = ', '.join(map(self.visit, n.args))
        if func == 'sqrt':
            return '\sqrt{%s}' % args
        else:
            return r'\operatorname{%s}\left(%s\right)' % (func, args)

    def prec_Call(self, n):
        return 1000

    def visit_Name(self, n):
        return n.id

    def prec_Name(self, n):
        return 1000

    def visit_UnaryOp(self, n):
        if self.prec(n.op) > self.prec(n.operand):
            return r'%s \left(%s\right)' % (self.visit(n.op), self.visit(n.operand))
        else:
            return r'%s %s' % (self.visit(n.op), self.visit(n.operand))

    def prec_UnaryOp(self, n):
        return self.prec(n.op)

    def visit_BinOp(self, n):
        if self.prec(n.op) > self.prec(n.left):
            left = r'\left(%s\right)' % self.visit(n.left)
        else:
            left = self.visit(n.left)
        if self.prec(n.op) > self.prec(n.right):
            right = r'\left(%s\right)' % self.visit(n.right)
        else:
            right = self.visit(n.right)
        if isinstance(n.op, ast.Div):
            return r'\frac{%s}{%s}' % (self.visit(n.left), self.visit(n.right))
        elif isinstance(n.op, ast.FloorDiv):
            return r'\left\lfloor\frac{%s}{%s}\right\rfloor' % (self.visit(n.left), self.visit(n.right))
        elif isinstance(n.op, ast.Pow):
            return r'%s^{%s}' % (left, self.visit(n.right))
        else:
            return r'%s %s %s' % (left, self.visit(n.op), right)

    def prec_BinOp(self, n):
        return self.prec(n.op)

    def visit_Sub(self, n):
        return '-'

    def prec_Sub(self, n):
        return 300

    def visit_Add(self, n):
        return '+'

    def prec_Add(self, n):
        return 300

    def visit_Mult(self, n):
        return '\\;'

    def prec_Mult(self, n):
        return 400

    def visit_Mod(self, n):
        return '\\bmod'

    def prec_Mod(self, n):
        return 500

    def prec_Pow(self, n):
        return 700

    def prec_Div(self, n):
        return 400

    def prec_FloorDiv(self, n):
        return 400

    def visit_LShift(self, n):
        return '\\operatorname{shiftLeft}'

    def visit_RShift(self, n):
        return '\\operatorname{shiftRight}'

    def visit_BitOr(self, n):
        return '\\operatorname{or}'

    def visit_BitXor(self, n):
        return '\\operatorname{xor}'

    def visit_BitAnd(self, n):
        return '\\operatorname{and}'

    def visit_Invert(self, n):
        return '\\operatorname{invert}'

    def prec_Invert(self, n):
        return 800

    def visit_Not(self, n):
        return '\\neg'

    def prec_Not(self, n):
        return 800

    def visit_UAdd(self, n):
        return '+'

    def prec_UAdd(self, n):
        return 800

    def visit_USub(self, n):
        return '-'

    def prec_USub(self, n):
        return 800
    def visit_Num(self, n):
        return str(n.n)

    def prec_Num(self, n):
        return 1000

    def generic_visit(self, n):
        if isinstance(n, ast.AST):
            return r'' % (n.__class__.__name__, ', '.join(map(self.visit, [getattr(n, f) for f in n._fields])))
        else:
            return str(n)

    def generic_prec(self, n):
        return 0

class CustomMessageBox(QMessageBox):

    def __init__(self, *__args):
        QMessageBox.__init__(self)
        self.timeout = 0
        self.autoclose = False
        self.currentTime = 0
    
    def showEvent(self, QShowEvent):
        self.currentTime = 0
        if self.autoclose:
            self.startTimer(1000)
    
    def timerEvent(self, *args, **kwargs):
        self.currentTime += 1
        if self.currentTime >= self.timeout:
            self.done(0)
    
    @staticmethod
    def showWithTimeout(timeoutSeconds, message, title, icon=QMessageBox.Information, buttons=QMessageBox.Ok):
        w = CustomMessageBox()
        w.autoclose = True
        w.timeout = timeoutSeconds
        w.setText(message)
        w.setWindowTitle(title)
        w.setIcon(icon)
        w.setStandardButtons(buttons)
        w.exec_()

class pandasModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None
class NavigationToolbar_new(NavigationToolbar):
    def __init__(self, figure_canvas, ax, mainDialog, parent=None, isGraph = True, isEquation = False):
        if isEquation:
            self.toolitems = (('Home', 'Lorem ipsum dolor sit amet', 'home', 'home'),
                ('Pan', 'tincidunt ut laoreet', 'move', 'pan'),
                ('Save', 'sollemnes in futurum', 'filesave', 'save_figure')
                )
        self.ax = ax
        self.mainDialog = mainDialog
        self.isGraph = isGraph
      
        NavigationToolbar.__init__(self, figure_canvas, parent= None)
    #I need to add checkbox to check whether it is xy mode or xyz mode or plot left or plot right?
    def zoom(self):
        super().zoom()
        if self.isGraph:
            xlims = self.ax.get_xlim()
            ylims = self.ax.get_ylim()
            if not self.mainDialog.impw.ui.xyz.isChecked():
                self.mainDialog.ui.xminValue.setText("{0:.1f}".format(xlims[0]))
                self.mainDialog.ui.xmaxValue.setText("{0:.1f}".format(xlims[1]))
                self.mainDialog.ui.yminValue.setText("{0:.1f}".format(ylims[0]))
                self.mainDialog.ui.ymaxValue.setText("{0:.1f}".format(ylims[1]))
            elif self.mainDialog.impw.ui.xyz.isChecked() and self.ax == self.mainDialog.axdyn:
                self.mainDialog.ui.xminValue.setText("{0:.1f}".format(xlims[0]))
                self.mainDialog.ui.xmaxValue.setText("{0:.1f}".format(xlims[1]))
            elif self.mainDialog.impw.ui.xyz.isChecked() and self.ax == self.mainDialog.axspec:
                self.mainDialog.ui.yminValue.setText("{0:.1f}".format(xlims[0]))
                self.mainDialog.ui.ymaxValue.setText("{0:.1f}".format(xlims[1]))
    def home(self):
        super().home()
        if self.isGraph:
            xlims = self.ax.get_xlim()
            ylims = self.ax.get_ylim()
            if not self.mainDialog.impw.ui.xyz.isChecked():
                self.mainDialog.ui.xminValue.setText("{0:.1f}".format(xlims[0]))
                self.mainDialog.ui.xmaxValue.setText("{0:.1f}".format(xlims[1]))
                self.mainDialog.ui.yminValue.setText("{0:.1f}".format(ylims[0]))
                self.mainDialog.ui.ymaxValue.setText("{0:.1f}".format(ylims[1]))
            elif self.mainDialog.impw.ui.xyz.isChecked() and self.ax == self.mainDialog.axdyn:
                self.mainDialog.ui.xminValue.setText("{0:.1f}".format(xlims[0]))
                self.mainDialog.ui.xmaxValue.setText("{0:.1f}".format(xlims[1]))
            elif self.mainDialog.impw.ui.xyz.isChecked() and self.ax == self.mainDialog.axspec:
                self.mainDialog.ui.yminValue.setText("{0:.1f}".format(xlims[0]))
                self.mainDialog.ui.ymaxValue.setText("{0:.1f}".format(xlims[1]))
    def pan(self):
        super().pan()
        if self.isGraph:
            xlims = self.ax.get_xlim()
            ylims = self.ax.get_ylim()
            if not self.mainDialog.impw.ui.xyz.isChecked():
                self.mainDialog.ui.xminValue.setText("{0:.1f}".format(xlims[0]))
                self.mainDialog.ui.xmaxValue.setText("{0:.1f}".format(xlims[1]))
                self.mainDialog.ui.yminValue.setText("{0:.1f}".format(ylims[0]))
                self.mainDialog.ui.ymaxValue.setText("{0:.1f}".format(ylims[1]))
            elif self.mainDialog.impw.ui.xyz.isChecked() and self.ax == self.mainDialog.axdyn:
                self.mainDialog.ui.xminValue.setText("{0:.1f}".format(xlims[0]))
                self.mainDialog.ui.xmaxValue.setText("{0:.1f}".format(xlims[1]))
            elif self.mainDialog.impw.ui.xyz.isChecked() and self.ax == self.mainDialog.axspec:
                self.mainDialog.ui.yminValue.setText("{0:.1f}".format(xlims[0]))
                self.mainDialog.ui.ymaxValue.setText("{0:.1f}".format(xlims[1]))
class TabWindow(QTabWidget):
    def __init__(self, app):
        super().__init__()
        self.apptemp=[] #Necessary when closing temporary application during copying the figure
        self.wndws=[]        
        self.app = app
        #self.setDocumentMode(True) #Experimental
        #self.setMinimumSize(QtCore.QSize(600, 720))
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tablayout = QtWidgets.QGridLayout(self)
        self.tablayout.setContentsMargins(1, 1, 1, 1)
        self.tablayout.setSpacing(0)
        self.wdg=AppWindow(self.app)
        self.addTab(self.wdg,'Home')
        self.setTabText(self.currentIndex(),self.wdg.ui.listprefs_main.currentText())
        self.tabBar().setTabButton(0, self.tabBar().LeftSide,None)
        
        #Keyboard shortcuts for tabs:
        #QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(self.newBtn)
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(self.closeTab)
        
        #Signals
        self.tabCloseRequested.connect(lambda index: self.removeTab(index))
        self.wdg.addTab.triggered.connect(self.newBtn)
        self.wdg.loadAction.triggered.connect(self.renameTab)
        self.wdg.impw.ui.listprefs.currentTextChanged.connect(self.renameTab_Main)
        self.wdg.fitter.triggered.connect(lambda wdg: self.addfitwdg(wdg=self.wdg.fitw))
        #self.currentChanged.connect(self.tabChanged) #Experimental
        self.lastaddedtab=self.wdg
        self.wndws.append(self.wdg)
        self.show()
    def newBtn(self):
        temwdg=AppWindow(self.app)
        temwdg.addTab.triggered.connect(self.newBtn)
        temwdg.impw.ui.listprefs.currentTextChanged.connect(self.renameTab)
        temwdg.fitter.triggered.connect(lambda wdg: self.addfitwdg(wdg=temwdg.fitw))
        self.lastaddedtab=temwdg
        self.addTab(self.lastaddedtab,self.lastaddedtab.impw.ui.listprefs.currentText())
        self.setCurrentIndex(self.count()-1)
    def closeTab(self):
        if not self.currentIndex()==0: #To avoid to close initial tab
            self.removeTab(self.currentIndex())
        else:
            pass
    def renameTab(self):
        self.setTabText(self.currentIndex(),self.lastaddedtab.impw.ui.listprefs.currentText())
        #self.setTabText(self.currentIndex(),':'.join([self.lastaddedtab.impw.ui.listprefs.currentText(),self.lastaddedtab.impw.ui.bgmode.checkedButton().text()]))
    def renameTab_Main(self):
        self.setTabText(self.currentIndex(),self.wdg.impw.ui.listprefs.currentText())
    def addfitwdg(self,wdg):
        self.insertTab(self.currentIndex()+1,wdg,'fit')
        self.setCurrentIndex(self.currentIndex()+1)
    # def closeEvent(self,event):
    #     if self.wdg.apptemp!=[]:
    #         self.wdg.apptemp=QApplication([])
    #         clipboard = self.wdg.apptemp.clipboard()
    #         event = QtCore.QEvent(QtCore.QEvent.Clipboard)
    #         QApplication.sendEvent(clipboard, event)
    #         self.wdg.apptemp.quit()
    #     else:
    #         QApplication.quit()
    def tabChanged(self):
        self.currentWidget().resizewhenTabChanged() #To change size when tab changed, experimental

class MainWindow(QMainWindow):
    screenChanged = QtCore.pyqtSignal(QScreen, QScreen)
    def __init__(self, app):
        super().__init__()
        
        desktop = QApplication.desktop()
        screenRect = desktop.screenGeometry()
        height = screenRect.height()
        width = screenRect.width()
        
        self.resize(int(width/2.5),int(height/2))
        self.setWindowTitle('Graphx-y-z')
        self.app = app
        
        global uisize_main
        uisize_main=self.geometry()
        
        self.tbw = TabWindow(self.app)
        self.setCentralWidget(self.tbw)
        
        # This will get saved settings values:
        self.getSettingsValues()
        height = self.settingWindow.value('window_height')
        width = self.settingWindow.value('window_width')
        #print(width,height)
        try:
            self.resize(width,height) #Crashes during initial run
        except Exception as Argument:
            self.tbw.wdg.genLogforException(Argument) #This handles crash for initial run
        
        self.mbar=self.menuBar()
        self.mbar.setNativeMenuBar(True)
        self.file=self.mbar.addMenu("File")
        
        self.newWindowAction = self.file.addAction("New Window")
        self.newWindowAction.setShortcut(QKeySequence("Ctrl+N"))
        self.file.addSeparator()
        openAction = self.file.addAction("Open...")
        openAction.triggered.connect(self.loadasProject)
        openAction.setShortcut(QKeySequence("Ctrl+Shift+O"))
        openDefAction = self.file.addAction("Open Default")
        openDefAction.setShortcut(QKeySequence("Ctrl+O"))
        openDefAction.triggered.connect(self.loadDefProject)
        recentFiles=self.file.addMenu("Recents")
        self.file.addSeparator()
        saveCurAction = self.file.addAction("Save")
        saveCurAction.setShortcut(QKeySequence("Ctrl+Shift+S"))
        saveCurAction.triggered.connect(self.saveCurProject)
        
        saveDefAction = self.file.addAction("Save Default")
        saveDefAction.setShortcut(QKeySequence("Ctrl+D"))
        saveDefAction.triggered.connect(self.saveDefProject)
        
        saveasAction = self.file.addAction("Save as...")
        saveasAction.triggered.connect(self.saveasProject)
        
        helps = self.mbar.addMenu("Graphxyz")
        aboutMe = helps.addAction(" About Graphxyz")
        aboutMe.triggered.connect(self.aboutMenuPop)
        #aboutMe.setMenuRole(QAction.AboutRole)
        checkUpdate = helps.addAction(" Check for Update...")
        checkUpdate.triggered.connect(self.updateChecker)
        #checkUpdate.setMenuRole(QAction.AboutRole)
        
        self.screenChanged.connect(lambda oldScreen,newScreen: self.tbw.wdg.resizeUI(oldScreen,newScreen))
        
        self.show()
        
        if not appVersionText == latestVersion:
            self.tbw.wdg.showPopInfo(''.join(['New ', latestVersion.lower(),' is available']),color = 'blue',durationToShow = 1,widgetToShowOn=self.mbar)
    def getSettingsValues(self):
        self.settingWindow = QSettings('Graphxyz', 'Window Size')
    def closeEvent(self,event):
        # if self.wdg.apptemp!=[]:
        #     self.wdg.apptemp=QApplication([])
        #     clipboard = self.wdg.apptemp.clipboard()
        #     event = QtCore.QEvent(QtCore.QEvent.Clipboard)
        #     QApplication.sendEvent(clipboard, event)
        #     self.wdg.apptemp.quit()
        # else:
        #     QApplication.quit()
        self.settingWindow.setValue('window_height',self.rect().height())
        self.settingWindow.setValue('window_width',self.rect().width())
    def moveEvent(self, event):
        oldScreen = QtWidgets.QApplication.screenAt(event.oldPos())
        newScreen = QtWidgets.QApplication.screenAt(event.pos())

        if not oldScreen == newScreen:
            self.screenChanged.emit(oldScreen, newScreen)

        return super().moveEvent(event)
    def aboutMenuPop (self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgText = ''.join(["<FONT COLOR='#800000'>Graphx-y-z</FONT>"," <br> A tool for rapid scientific plots and analysis",'<br><br>Version: ',appVersion,"<br><br> Copyright © 2020-",datetime.now(). strftime("%Y"),'<br><br> All rights reserved by Dovletgeldi Seyitliyev','<br> Distributed under <a href="https://opensource.org/licenses/MIT"> MIT licence </a>'])
        msgBox.setText(msgText)
        msgBox.setWindowTitle("Warning!")
        msgBox.exec()
    def saveProject(self,fileloc):
        projectArray = []
        for i in range(self.tbw.count()):
            projectArray.append(self.tbw.widget(i).saveBtn(needSaved = False))
        np.savez(fileloc, *projectArray[:len(projectArray)]) #Saves all of the tabs as archived array npz
    def saveasProject(self):
        try:
            projectArray = []
            filter=''.join(['npz','(*','.npz',')'])
            qfdlg=QFileDialog()
            #qfdlg.setFileMode(QFileDialog.AnyFile)
            npzSave = qfdlg.getSaveFileName(self, None, "Create New File",filter)
            for i in range(self.tbw.count()):
                projectArray.append(self.tbw.widget(i).saveBtn(needSaved = False))
            if not npzSave[0]=='':
                np.savez(npzSave[0], *projectArray[:len(projectArray)]) #Saves all of the tabs as archived array npz
            self.curProjLoc = npzSave[0]
        except Exception as Argument:
            self.tbw.wdg.genLogforException(Argument)
    def saveDefProject(self):
        try:
            projectArray = []
            fileloc = getResourcePath('npys')
            fileloc = self.makeFolderinDocuments('Saved Projects')
            fileloc = fileloc/'default'
            for i in range(self.tbw.count()):
                projectArray.append(self.tbw.widget(i).saveBtn(needSaved = False))
            np.savez(fileloc, *projectArray[:len(projectArray)]) #Saves all of the tabs as archived array npz
        except Exception as Argument:
            self.tbw.wdg.genLogforException(Argument)
    def saveCurProject(self):
        try:
            projectArray = []
            for i in range(self.tbw.count()):
                projectArray.append(self.tbw.widget(i).saveBtn(needSaved = False))
            np.savez(self.curProjLoc, *projectArray[:len(projectArray)]) #Saves all of the tabs as archived array npz
        except Exception as Argument:
            self.tbw.wdg.genLogforException(Argument)
    
    def loadProject(self, datatoload):
        projectLoaded = np.load(datatoload, allow_pickle=True)
        for i in range(len(projectLoaded)):
            self.tbw.currentWidget().loadBtn(projectLoaded[''.join(['arr_',str(i)])],arrayLoadMode = True)
            try:
                self.tbw.currentWidget().submitButtonPushed()
            except Exception as Argument:
                self.genLogforException(Argument)
            
            if i<len(projectLoaded)-1:
                self.tbw.newBtn()
    def loadDefProject(self):
        try:
            #datatoload = getResourcePath('npys')
            datatoload = self.makeFolderinDocuments('Saved Projects')
            datatoload = datatoload/'default.npz'
            projectLoaded = np.load(datatoload, allow_pickle=True)
            for i in range(len(projectLoaded)):
                self.tbw.currentWidget().loadBtn(projectLoaded[''.join(['arr_',str(i)])],arrayLoadMode = True)
                try:
                    self.tbw.currentWidget().submitButtonPushed()
                except Exception as Argument:
                    self.tbw.wdg.genLogforException(Argument)
                
                if i<len(projectLoaded)-1:
                    self.tbw.newBtn()
        except Exception as Argument:
            self.tbw.wdg.genLogforException(Argument)
    def loadasProject(self):
        try:
            #datatoload = getResourcePath('npys')
            file_dialog = QFileDialog()
            #filter=''.join([self.impw.ui.dendwith.currentText(),'(*',self.impw.ui.dendwith.currentText(),')'])
            #print(filter)
            filter = '.npz(*.npz)'
            file_dialog.setNameFilters([filter])
            #file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
            file_view = file_dialog.findChild(QListView, 'listView')
            if file_view:
                file_view.setSelectionMode(QAbstractItemView.MultiSelection)
            f_tree_view = file_dialog.findChild(QTreeView)
            if f_tree_view:
                f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)
            if file_dialog.exec():
                folderLoc = file_dialog.selectedFiles()
            self.curProjLoc = folderLoc[0]
            projectLoaded = np.load(folderLoc[0], allow_pickle=True)
            for i in range(len(projectLoaded)):
                self.tbw.currentWidget().loadBtn(projectLoaded[''.join(['arr_',str(i)])],arrayLoadMode = True)
                try:
                    self.tbw.currentWidget().submitButtonPushed()
                except Exception as Argument:
                    self.tbw.wdg.genLogforException(Argument)
                
                if i<len(projectLoaded)-1:
                    self.tbw.newBtn()
        except Exception as Argument:
            self.tbw.wdg.genLogforException(Argument)
    def makeFolderinDocuments(self, foldName):
        foldDir = getResourcePath(os.path.expanduser('~'))/'Documents'/'Graphxyz'
        os.makedirs(foldDir, exist_ok = True)
        foldDir = foldDir / foldName
        os.makedirs(foldDir, exist_ok = True)
        return foldDir
    def updateChecker(self):
        if not appVersionText == latestVersion:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgText = ''.join(['Current version is ',appVersion,'. <br><br> <FONT COLOR="Green">',latestVersion,'</FONT> is now available.'])
            msgBox.setText(msgText)
            msgBox.setWindowTitle("Warning!")
            msgBox.exec()
        else:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgText = "Graphxyz is up to date!"
            msgBox.setText(msgText)
            msgBox.setWindowTitle("Warning!")
            msgBox.exec()

# class SplashScreen(QWidget):
#     def __init__(self):
#         super().__init__()
#         DataDir = getResourcePath("uis")
#         uiPath = DataDir / 'splash.ui'
#         self.ui = uic.loadUi(uiPath,self)
        
#         self.counter = 0
#         self.n = 300
        
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.loading)
#         self.timer.start()
#     def loading(self):
#         self.progressBar.setValue(self.counter)

#         if self.counter == int(self.n * 0.3):
#             self.ui.labelDescription.setText('<strong>Working...</strong>')
#         elif self.counter == int(self.n * 0.6):
#             self.ui.labelDescription.setText('<strong>Still working...</strong>')
#         elif self.counter >= self.n:
#             self.timer.stop()
#             self.close()

#             time.sleep(1)
#             self.myApp = MainWindow()
#             self.myApp.show()

#         self.counter += 1

# def openNewWindowApp(checked,app):
#     #app = QApplication(sys.argv)
#     wnd = MainWindow(app = app) #app parameter is needed for the copy figure to clipboard to work
#     #wnd.newWindowAction.triggered.connect(lambda checked: openNewWindowApp(checked,app))
#     wnd.raise_()
#     #sys.exit(app.exec())
    
class higherMainWindow(QWidget): #This window allows to make multiple instances of the same app
    def __init__(self,app):
        super().__init__()
        self.app = app
        self.myApps = []
        self.myApp = MainWindow(app=self.app)
        
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(self.myApp.tbw.closeTab)
        #QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(self.myApp.tbw.newBtn)
        
        self.myApp.newWindowAction.triggered.connect(self.newWindowOpen)
        self.myApps.append(self.myApp)
        self.myApp.raise_()
    def newWindowOpen(self):
        tempApp = MainWindow(app=self.app)
        tempApp.newWindowAction.triggered.connect(self.newWindowOpen)
        self.myApps.append(tempApp)
        tempApp.raise_()
    def closeEvent(self,event):
        QApplication.quit()

if __name__=='__main__':
    app = QApplication(sys.argv)
    wnd = higherMainWindow(app = app) #app parameter is needed for the copy figure to clipboard to work
    #wnd.newWindowAction.triggered.connect(lambda checked: openNewWindowApp(checked,app))
    wnd.raise_()
    sys.exit(app.exec())
    
    
#Notes on where I left:
    # Code needs lots of clean up
    # I am omitting multiple fit option for now. I will work on it later
    # Save currentproject button seems to have issues
    # Need to add splash screen
    # Add a way to save fits also add a way to compare  models of the fits
    # Handle the exception when app throws when changed from xy mode to xyz and accidentally trying to plot on that mode
    # The app now works, I think exceptions keeps it from running, because I need to use pathlib to generate log to txt
    # Sizing issues needs to be very well refined, very buggy
    # I removed save load tab buttons,they are now in a menu, however, actions needs to be connected
    # No need checkboxes in list menu
    # I can probably combine multiple functions with lambda function and connect
    # Urgent: in windows, tabs overalap with menubar. This needs to be fixed by using correct hierarchy between widgets. QTabWidget needs to be inside QMainWindow and then QDialog needs to be inside that
    # Fix fit menu scaling as the main one
    # Problem: When contour plot, x has to be number of columns in z. you cant arbitrarily flip axes, fix this
    # Saving needs to be more elegant
    # Make user save all tabs' conditions,including fit conditions, not just only one tab,
    # Note that UI change/update should not break the saved updates from old versions of the app
    # Semilogx and semilogy does not work as expected, for time being they just get log of real data instead of changing axes behavior
    # Modify the toolbar for my needs,created new class and override as needed
    # When choosing location of files to add, allow to auto switch of preset add mode
    # Consider saving "everything" to npy file including whether fitting or not. Save presets seperately to csv.
    # Add an option to save graph data to csv files
    # Solve issue with custom legends, fontsize does not update when clicked refine
    # Find a way to shorten a legend and add the rest to title
    # Add ability to be able to work with multiple fit with multiple plots at the same time
    # Ultimate goal would be to automate fit procedure, make it so that it finds its own initial variables
    # Now all legends are shortened, implement so that user can choose whether to do that or not
    # Note that I am removing all dT/T conversion stuff. It needs to be fixed
    # I made it work to be able to analyze multiple data as 3D data, whats left is to clean up and to be able to export data so that it can be re-used
    # Remove yave lineedit and merge it with yslice to have averages of multiple.
    # Remove graph controls and merge them with one button click
    # I am working on the ability to be able to manipulate all x y and z axes with arbitrary functions
    # I need to optimize for RAM management and eliminate any bad memory usage
    # Add graph control option to contral x y limits on graphs
    # There is a bug I could not fix yet: This is the bug I could not fix yet. When I initialize slider, this function is called unnecessarily
    # Implement Python functions to the functions that can be written
    # Make the getting started easier, its very hard now to get started with new type of data, refine the import options menu
    # Make line position adjust accordingly when x axis is modified
    # Note that I have automated data import more. Now user just needs to define where x and y and z starts. Program automatically removes nonnumerics. Proper backups taken if any issue happen
    # Refine and font change buttons needs to be refined in xy mode
    # Refine the fit menu
    # Note that xlim is broken when data is linked, from minor adjustment, fix it
    # Think about smarter ways to hold current graph, maybe only hold when pressed submit but make it so that it can be cleared later
    # Consider linking multiple data properly, link instead plotting them seperately
    # Fonts need to update with screen size, and also when monitor is changed, I think this is important
    # Add a predefined functions to fit menu
    # ax.ticklabel_format(axis='y',style='scientific',scilimits=(-2,2)) , this method only works with scalar formatter???
    # self.ui.sliderx.setMinimum(int(self.ui.xminValue.text())*10) ValueError: invalid literal for int() with base 10: '0.5'
    # Make a GUI to collect plots and combine them after, it will be seperate GUI that serves as a "plotter"
    # Sometimes line edit cursors loose fous, why??
    # Add predefined functions from origin
    # Fit menu can guess the initial parameters and use those?
    # Make list menu more interactable, use scroll bars, make so that when scrolling,data list stays on the left and make the rest scrollable
    # Add capability to take only one data
    # Capability to add error bars to fits
    # There is some issue with 3D maker when adding and removing certain data pints, it seems like not accurate
    # Add an option to be able to fit multiple plots fit in the same window and add decorating option to avoid leaving fitting screen in order to decorate fits
    # Check Model View Controller programming for PyQt5
    # I need to understand how scaling work for this app. I am having hard time to hace consistent UI with consistent font size
    
#Bugs Fixed are below:
    # Have the option to autolimit button when data is changed. Loading does it, but adding does not
    # Add an option to choose and add/delete multiple  sources/data from the list
    # Plotting xy and xyz mode at the same time, multiple presets at the same currently does not work, needs to be refineds
    # Make font adjusting button adjust only the font, not x y z label, adjust those labels with checkbox or additional button
    # I am planning to add functionality to be able to add multiple data files from multiple locations, to be able to save that state and load that state
    # I started converting simple text input for folder locations into combobox, that way I can iterate multiple locations and data in them with their own presets
    # There is a new bug, legend does not disappear when unchecked
    # Use blit with matplotlib to make updating figure faster, set y data was fast enough, I used blit when updating contour, made it  faster
    # Note that system loads default.npy file in the beginning, so user can set their own default before closing the app
    # Need to fix scaling issues asap - DONE
    # Major problem: Menubar items does not connect with each tab. Does not make sense DONE using seperate menubars for each tab
    # Urgent: in windows, tabs overalap with menubar. This needs to be fixed by using correct hierarchy between widgets. QTabWidget needs to be inside QMainWindow and then QDialog needs to be inside that, fixed

    