# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!
import sys,os

from PyQt5.QtWidgets import QWidget,QTableWidget, QApplication, QMainWindow, QFileDialog, QPushButton,QHeaderView,QTableWidgetItem,QListView
from PyQt5 import QtCore, QtGui, QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import *
from PyQt5.QtGui import QIcon,QPixmap,QImage
import numpy as np
from os.path import dirname, join
from PIL import Image
from PIL.ImageQt import ImageQt
import numpy
import pydicom,cv2
from pydicom.filereader import read_dicomdir

from DatasetTools import *
#from ImageTools import *
from FileWrite import *
from VolumeRendering import *
from FileDialog import *
from Constants import *


class Ui_MainWindow(object):
    #filepath = get_testdata_files('DICOMDIR')[0]
    filepath = ''
    dicom_dir = None
    base_dir = None         
    patient_selected = None
    study_selected = None
    serie_selected = None
    image_selected = None
    datasets = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(1152, 648)


        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.button = QPushButton('Open DICOM', self.centralwidget)
        self.button.setToolTip('Open the DICOM file or DICOMDIR')
        self.button.setFixedSize(100, 25)
        self.button.move(15, 15)
        self.button.clicked.connect(self.setPatientView)

        self.btnMetafile = QPushButton('Gen Metaimage', self.centralwidget)
        self.btnMetafile.setToolTip('Generate Metaimage')
        self.btnMetafile.setFixedSize(190, 50)
        self.btnMetafile.move(945, 461)
        self.btnMetafile.clicked.connect(self.writeMetaimage)

        self.patientView = QtWidgets.QListView(self.centralwidget)
        self.patientView.setGeometry(QtCore.QRect(15, 50, 300, 70))
        self.patientView.setObjectName("patientView")
        self.patientModel = QtGui.QStandardItemModel()
        self.patientView.setModel(self.patientModel)
        self.patientView.clicked[QtCore.QModelIndex].connect(self.setStudyView)

        self.studyView = QtWidgets.QListView(self.centralwidget)
        self.studyView.setGeometry(QtCore.QRect(15, 130, 300, 120))
        self.studyView.setObjectName("studyView")
        self.studyModel = QtGui.QStandardItemModel()
        self.studyView.setModel(self.studyModel)
        self.studyView.clicked[QtCore.QModelIndex].connect(self.setSeriesView)

        self.seriesView = QtWidgets.QListView(self.centralwidget)
        self.seriesView.setGeometry(QtCore.QRect(15, 260, 300, 150))
        self.seriesView.setObjectName("seriesView")
        self.seriesModel = QtGui.QStandardItemModel()
        self.seriesView.setModel(self.seriesModel)
        self.seriesView.clicked[QtCore.QModelIndex].connect(self.setImagesView)


        self.imagesView = QtWidgets.QListView(self.centralwidget)
        self.imagesView.setGeometry(QtCore.QRect(15,420,300,210))
        self.imagesView.setObjectName("imagesView")
        self.imagesModel = QtGui.QStandardItemModel()
        self.imagesView.setModel(self.imagesModel)
        self.imagesView.clicked[QtCore.QModelIndex].connect(self.setDicomView)

        self.dicomView = QtWidgets.QLabel(self.centralwidget)
        self.dicomView.setGeometry(QtCore.QRect(330, 50, 396, 396))
        self.dicomView.setObjectName("dicomView")

        self.segmentView = QtWidgets.QLabel(self.centralwidget)
        self.segmentView.setGeometry(QtCore.QRect(741,50,396,396))
        self.segmentView.setObjectName('segmentView')

        self.logView = QtWidgets.QListView(self.centralwidget)
        self.logView.setGeometry(QtCore.QRect(330,461,600,172))
        self.logView.setObjectName("imagesView")
        self.logModel = QtGui.QStandardItemModel()
        self.logView.setModel(self.logModel)
        #self.logView.clicked[QtCore.QModelIndex].connect(self.setLogView)
      
        self.vtkWidget = QVTKRenderWindowInteractor(self.centralwidget)
        self.vtkWidget.setGeometry(QtCore.QRect(741,50,396,396))

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Computer Engineering Project I - Dicom processing"))

    def setPatientView(self):
        self.patientModel.clear()
        dialog = FileDialog()
        self.filepath = dialog.openFileNameDialog(title="Open DICOMDIR",typeFile=CS_DICOMDIR)
        if self.filepath:
            self.base_dir = dirname(self.filepath)
            self.dicom_dir = read_dicomdir(self.filepath)
            for patient in range(len(self.dicom_dir.patient_records)):
                ID = self.dicom_dir.patient_records[patient].PatientID
                NAME = str(self.dicom_dir.patient_records[patient].PatientName).replace('^',' ')
                it = QtGui.QStandardItem("%s\t%s"%(ID,NAME))
                self.patientModel.appendRow(it)
            
    def setStudyView(self,index):
        self.studyModel.clear()
        selectRow = self.patientModel.itemFromIndex(index).index().row()
        self.patient_selected = selectRow
        studies = self.dicom_dir.patient_records[selectRow].children

        for study in range(len(studies)):
            StudyID = studies[study].StudyID
            StudyDescription = studies[study].StudyDescription
            it = QtGui.QStandardItem("%s\t%s"%(StudyID,StudyDescription))
            self.studyModel.appendRow(it)
    
    def setSeriesView(self,index):
        self.seriesModel.clear()
        selectRow = self.studyModel.itemFromIndex(index).index().row()
        self.study_selected = selectRow
        all_series = self.dicom_dir.patient_records[self.patient_selected].children[selectRow].children

        for serie in all_series:
            image_count = len(serie.children)
            plural = ('', 's')[image_count > 1]
            if 'SeriesDescription' not in serie:
                serie.SeriesDescription = "N/A"
            it = QtGui.QStandardItem("Series {}: {}: {} ({} image{})".format(
                serie.SeriesNumber, serie.Modality, serie.SeriesDescription,
                image_count, plural))
            self.seriesModel.appendRow(it)

    def setImagesView(self,index):
        self.imagesModel.clear()
        selectRow = self.seriesModel.itemFromIndex(index).index().row()
        self.serie_selected = selectRow
        image_records = self.dicom_dir.patient_records[self.patient_selected] \
            .children[self.study_selected] \
            .children[selectRow] \
            .children
        
        image_filenames = [join(self.base_dir, *image_rec.ReferencedFileID)for image_rec in image_records]
        self.datasets = sortSliceLocation(image_filenames)

        for img in self.datasets:
            it = QtGui.QStandardItem(img)
            self.imagesModel.appendRow(it)

   
    def setDicomView(self,index):
        all_series = self.dicom_dir.patient_records[self.patient_selected].children[self.study_selected].children
        selectRow = self.imagesModel.itemFromIndex(index).index().row()
        dataset = pydicom.dcmread(self.datasets[selectRow])
        print(dataset.pixel_array.shape)
        print("Slice location...:", dataset.PixelSpacing)
        Q_image = QImage(ImageQt(get_PIL_image(dataset).resize((396, 396),Image.ANTIALIAS)))
        self.dicomView.setPixmap(QPixmap(Q_image))
        self.setGrayScaleView(PIL_image=get_PIL_image(dataset))
    
    def setGrayScaleView(self,PIL_image):
        imgArray = convertPIL2Array(PIL_image)
        BGR = convertArray2BGR(imgArray)
        imageGray = convertBGR2Blur2GRAY(BGR)
        ret,thresh1 = segmentThreshold(imageGray,195)
        image_PIL = Image.fromarray(thresh1).resize((396, 396),Image.ANTIALIAS)
        self.segmentView.setPixmap(convertPIL2Pixmap(image_PIL))
    
    def writeMetaimage(self):
        writeMetaimage(self.datasets)
        setVtkWidget(self.vtkWidget)

    def openFileNameDialog(self):
        dialog = App()
    
   





