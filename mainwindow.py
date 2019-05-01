# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!
import sys,os
from PyQt5.QtWidgets import QWidget,QTableWidget, QApplication, QMainWindow, QFileDialog, QPushButton,QHeaderView,QTableWidgetItem
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
    filepath = '/home/sivaroot/CG_Project/77654033_19950903/DICOMDIR'
    print('Path to the DICOM directory: {}'.format(filepath))
    dicom_dir = read_dicomdir(filepath)
    base_dir = dirname(filepath)        
    patient_selected = None
    study_selected = None


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(1152, 648)


        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.button = QPushButton('Open DICOM', self.centralwidget)
        self.button.setToolTip('Open the DICOM file or DICOMDIR')
        self.button.move(15, 15)
        self.button.clicked.connect(self.setPatienTable)

        self.patienTable = QtWidgets.QTableWidget(self.centralwidget)
        self.patienTable.setColumnCount(2)     
        self.patienTable.setHorizontalHeaderLabels(['Patient ID',"Name"])
        self.patienTable.setColumnWidth(0, 80)
        self.patienTable.setColumnWidth(1, 220)
        self.patienTable.setGeometry(QtCore.QRect(15, 50, 300, 100))
        self.patienTable.setObjectName("patienTable")
        self.patienTable.cellClicked.connect(self.setStudyTable)


        self.studyTable = QtWidgets.QTableWidget(self.centralwidget)
        self.studyTable.setColumnCount(3)     
        self.studyTable.setHorizontalHeaderLabels(["Study ID","Study Date", "Description"])
        self.studyTable.setColumnWidth(0, 70)
        self.studyTable.setColumnWidth(1, 90)
        self.studyTable.setColumnWidth(2, 140)
        self.studyTable.setGeometry(QtCore.QRect(15, 160, 300, 150))
        self.studyTable.setObjectName("studyTable")
        self.studyTable.cellClicked.connect(self.setSerieTable)

        self.serieTable = QtWidgets.QTableWidget(self.centralwidget)
        self.serieTable.setColumnCount(1)  
        self.serieTable.setHorizontalHeaderLabels(['Image'])
        self.serieTable.setColumnWidth(0,300)
        self.serieTable.setGeometry(QtCore.QRect(15, 320, 300, 300))
        self.serieTable.setObjectName("serieTable")
        self.serieTable.cellClicked.connect(self.setDicomView)
        self.dicomView = QtWidgets.QLabel(self.centralwidget)
        self.dicomView.setGeometry(QtCore.QRect(330, 15, 512, 512))
        self.dicomView.setObjectName("dicomView")
        #self.dicomView.cellClicked.connect(self.setSerieTable)

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

    
    

    def setPatienTable(self):
        self.patienTable.setRowCount(len(self.dicom_dir.patient_records))       
        for patient in range(len(self.dicom_dir.patient_records)):
            self.patienTable.setItem(patient, 0, QTableWidgetItem(self.dicom_dir.patient_records[patient].PatientID))
            self.patienTable.setItem(patient, 1, QTableWidgetItem(str(self.dicom_dir.patient_records[patient].PatientName).replace('^',' ')))


    def setStudyTable(self,row):
        self.patient_selected = row
        print ("Click on " , str(row)," ",self.dicom_dir.patient_records[row].PatientName)
        studies = self.dicom_dir.patient_records[self.patient_selected].children
        self.studyTable.setRowCount(len(studies))       

        for study_record in range(len(studies)):
            for col in range(3):
                if(col == 0):
                    self.studyTable.setItem(study_record, col, QTableWidgetItem(studies[study_record].StudyID))
                elif(col == 1):
                    date_str = str(studies[study_record].StudyDate)
                    date_format = "%s/%s/%s" % (date_str[0:4],date_str[4:6],date_str[6:8])
                    self.studyTable.setItem(study_record, col, QTableWidgetItem(date_format))
                elif(col == 2):
                    self.studyTable.setItem(study_record, col, QTableWidgetItem(studies[study_record].StudyDescription))
    
    def PILimageToQImage(pilimage):
        imageq = ImageQt(pilimage) #convert PIL image to a PIL.ImageQt object
        qimage = QImage(imageq) #cast PIL.ImageQt object to QImage object -that´s the trick!!!
        return qimage

    def setSerieTable(self,row):
        print("Reading images...")
        self.study_selected = row
        all_series = self.dicom_dir.patient_records[self.patient_selected].children[row].children
        print("Series count : %d"%len(all_series))

        #for series in all_series:
        image_records = all_series[0].children
        image_filenames = [join(self.base_dir, *image_rec.ReferencedFileID)for image_rec in image_records]
        dataset = pydicom.dcmread(image_filenames[10])
          
            #  for image_rec in image_filenames:
                #  print(image_rec)
        self.serieTable.setRowCount(len(image_filenames))  
        for image_filename_index in range(len(image_filenames)):      
            print(str(image_filenames[image_filename_index]))
            self.serieTable.setItem(image_filename_index, 0, QTableWidgetItem(str(image_filenames[image_filename_index])))

        print(len(image_filenames),'\n')
                #pprint(image_filenames[0], indent=12)
        if 'PixelData' in dataset:
            rows = int(dataset.Rows)
            cols = int(dataset.Columns)
            print("Image size.......: {rows:d} x {cols:d}, {size:d} bytes".format(
                rows=rows, cols=cols, size=len(dataset.PixelData)))
            if 'PixelSpacing' in dataset:
                print("Pixel spacing....:", dataset.PixelSpacing)
            print("Slice location...:", dataset.get('SliceLocation', "(missing)"))
            #plt.imshow(dataset.pixel_array)
            #plt.show()
            self.dicomView.setPixmap(QPixmap( QImage(ImageQt(get_PIL_image(dataset)))))
            #show_PIL(dataset)

    def setDicomView(self,row):
        all_series = self.dicom_dir.patient_records[self.patient_selected].children[self.study_selected].children
        image_records = all_series[0].children
        image_filenames = [join(self.base_dir, *image_rec.ReferencedFileID)for image_rec in image_records]
        dataset = pydicom.dcmread(image_filenames[row])
        self.dicomView.setPixmap(QPixmap( QImage(ImageQt(get_PIL_image(dataset)))))



