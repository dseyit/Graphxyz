
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
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QDesktopWidget, QWidget, QActionGroup, QMainWindow, QMenu, QMenuBar, QTableView, QMessageBox, QDialog, QApplication,QFileDialog, QPushButton, QSlider, QFrame, QLabel, QLineEdit, QCheckBox, QComboBox, QListWidget, QRadioButton, QTabWidget, QListView,QAbstractItemView,QTreeView, QColorDialog, QListWidgetItem
from PyQt5 import QtWidgets
import matplotlib
import pandas as pd
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, uic
from PyQt5.QtCore import QEasingCurve, pyqtSignal, QMimeData, QUrl, Qt, QAbstractTableModel, QPoint, QObject, QSettings, QTimer,QPropertyAnimation
from PyQt5.QtGui import QFont, QColor, QScreen, QPixmap, QIcon 
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
#This script is for test purposes only, does not serve any other purpose in this project

ttorem = 'TAS'
test = ['TAS,PL-Mightex-csv,Abs-181,xycol,PL-PLE,abs_ade,3dmaker,xyrow,Ares_So,TRPL-ours,PPMS,PPMS_kumah,TAS_single_spec,THz,new_preset', 'row,1,2,1,col,2,1,1,comma,csv,xyz,2,2,not-flipped,Delay(ps),Wavelength(nm),${\\Delta}T/T$,x-Exist,y-Exist', 'col,1,2,1,col,1,3,1,comma,csv,xy,0,0,flipped,Wavelength(nm),Intensity(a.u.),Intensity(a.u.),x-Exist,y-Exist', 'col,3,1,1,col,3,2,1,comma,csv,xy,0,0,flipped,Wavelength(nm),Absorption(O.D.),Intensity(a.u.),x-Exist,y-Exist', 'col,1,1,1,col,1,2,1,comma,csv,xy,0,0,not-flipped,Wavelength(nm),Intensity(a.u.),Intensity(a.u.),x-Exist,y-Exist', 'col,2,1,1,col,2,2,1,comma,txt,xy,0,0,not-flipped,Wavelength(nm),Intensity(a.u.),Intensity(a.u.),x-Exist,y-Exist', 'col,1,1,1,col,1,2,1,comma,csv,xy,2,2,flipped,Wavelength_(nm),Absorption_(O.D.),Intensity(a.u.),x-Exist,y-Exist', 'row,1,2,1,col,2,1,1,comma,csv,xyz,2,2,not-flipped,Delay(x$10^1$$^2$_photons/s),Wavelength(nm),Intensity_(a.u.),x-Exist,y-Exist', 'row,1,1,1,row,2,1,1,comma,csv,xy,0,0,not-flipped,Wavelength(nm),Intensity(a.u.),Intensity(a.u.),x-Exist,y-Exist', 'none,1,2,1,row,1,1,1,space,txt,xyz,2,1,not-flipped,Angle_(deg),Wavelength(nm),Intensity_(a.u.),z-row,y-Exist', 'none,1,2,0.004,col,4,1,1,space,dat,xy,2,2,not-flipped,Delay(ns),Intensity_(a.u.),${\\Delta}T/T$,y-row/col,y-Exist', 'col,1,3,1,col,1,10,1,comma,dat,xy,2,2,not-flipped,Temperature(K),Resistivity(ohm/cm),Intensity_(a.u.),x-Exist,y-Exist', 'col,1,1,1,col,1,2,1,space,txt,xy,2,2,flipped,Temperature(K),Resistance(ohm),${\\Delta}T/T$,x-Exist,y-Exist', 'col,1,1,1,col,1,2,1,comma,csv,xy,0,0,not-flipped,Wavlength(ps),${\\Delta}T/T$,None,x-Exist,y-Exist', 'row,1,1,1,row,2,1,1,comma,csv,xy,2,2,not-flipped,Delay(ps),Intensity(a.u.),None,x-Exist,y-Exist', 'row,1,1,1,row,2,1,1,comma,csv,xy,0,0,not-flipped,Wavelength(nm),Intensity(a.u.),Intensity(a.u.),x-Exist,y-Exist']
ttitles = test[0].split(',')
indtorem = ttitles.index(ttorem)
del ttitles[indtorem]
ttitles=','.join(ttitles)
del test[indtorem+1]
test[0] = ttitles

impw_list = test

labelToShow='this is information'
durationToShow = 4
locationToShow = [500,500]

start = time.time()
testlabel = QLabel()
testlabel.setStyleSheet("QLabel { background-color : white; color : green; }")
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
a.setDuration(durationToShow*1000*3)
a.setStartValue(1)
a.setEndValue(0)
a.setEasingCurve(QEasingCurve.OutBack)
a.start(QPropertyAnimation.DeleteWhenStopped)

testlabel.move(locationToShow[0],locationToShow[1])
testlabel.show()
testlabel.raise_()

while time.time()-start<=durationToShow:
    QApplication.processEvents()

testlabel.close()

# # in pyqt5 it needs to be PyQt5.QtWidgets
# msg=QMessageBox() # create an instance of it
# msg.setIcon(QMessageBox.Information) # set icon
# msg.setText("This is a message box") # set text
# msg.setInformativeText("This is additional information") # set information under the main text
# msg.setWindowTitle("MessageBox demo") # set title
# msg.setDetailedText("The details are as follows:") # a button for more details will add in
# msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel) # type of buttons associated
# #msg.buttonClicked.connect(myfunc) # connect clicked signal
# return_value =msg.exec_() # get the return value
# print("value of pressed message box button:", str(return_value)) # print result