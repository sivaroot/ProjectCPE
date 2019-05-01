# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!
import sys,os
from PyQt5.QtWidgets import QWidget,QTableWidget, QApplication, QMainWindow, QFileDialog, QPushButton,QHeaderView,QTableWidgetItem,QListView
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon,QPixmap,QImage
import numpy as np
from os.path import dirname, join
from pprint import pprint
from pydicom_PIL import show_PIL,get_PIL_image
from PIL import Image
from PIL.ImageQt import ImageQt

import pydicom,cv2
from pydicom.data import get_testdata_files
from pydicom.filereader import read_dicomdir

import matplotlib.pyplot as plt
class Ui_MainWindow(object):
    #filepath = get_testdata_files('DICOMDIR')[0]
    filepath = '/home/sivaroot/CG_Project/98890234_20030505_MR/DICOMDIR'
    print('Path to the DICOM directory: {}'.format(filepath))
    dicom_dir = read_dicomdir(filepath)
    base_dir = dirname(filepath)        
    patient_selected = None
    study_selected = None
    serie_selected = None
    image_selected = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(1152, 648)


        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.button = QPushButton('Open DICOM', self.centralwidget)
        self.button.setToolTip('Open the DICOM file or DICOMDIR')
        self.button.move(15, 15)
        self.button.clicked.connect(self.setPatientView)

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
        self.dicomView.setGeometry(QtCore.QRect(330, 15, 320, 320))
        self.dicomView.setObjectName("dicomView")
      
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Computer Engineering Project I - Dicom processing"))

    def openDialog(self):
        file_name = QFileDialog.getExistingDirectory()
        # Just for checking
        print(file_name)

    def setPatientView(self):
        self.patientModel.clear()
        for patient in range(len(self.dicom_dir.patient_records)):
            ID = self.dicom_dir.patient_records[patient].PatientID
            NAME = str(self.dicom_dir.patient_records[patient].PatientName).replace('^',' ')
            it = QtGui.QStandardItem("%s\t%s"%(ID,NAME))
            self.patientModel.appendRow(it)

    def setStudyView(self,index):
        self.studyModel.clear()
        selectRow = self.patientModel.itemFromIndex(index).index().row()
        self.patient_selected = selectRow
        print ("Click on " , str(selectRow)," ",str(self.dicom_dir.patient_records[selectRow].PatientName).replace('^',' '))
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
        for img in image_filenames:
            it = QtGui.QStandardItem(img)
            self.imagesModel.appendRow(it)

   
    def setDicomView(self,index):
        all_series = self.dicom_dir.patient_records[self.patient_selected].children[self.study_selected].children
        selectRow = self.imagesModel.itemFromIndex(index).index().row()
        image_records = all_series[self.serie_selected].children
        image_filenames = [join(self.base_dir, *image_rec.ReferencedFileID)for image_rec in image_records]
        dataset = pydicom.dcmread(image_filenames[selectRow])
        print("Slice location...:", dataset.get('SliceLocation', "(missing)"))
        self.dicomView.setPixmap(QPixmap(QImage(ImageQt(get_PIL_image(dataset).resize((320, 320),Image.ANTIALIAS)))))



