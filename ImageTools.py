
try:
    import cv2
    import numpy
    from PyQt5.QtGui import QPixmap,QImage
    from PIL.ImageQt import ImageQt
    from DatasetTools import *
 
except ImportError:
    print('Import error')

def convertArray2BGR(imgArray):
    return cv2.cvtColor(numpy.array(imgArray), cv2.COLOR_RGB2BGR)

def convertBGR2Blur2GRAY(imgBgr):
    return cv2.cvtColor(cv2.blur(imgBgr,(3,3)),cv2.COLOR_BGR2GRAY)    

def segmentThreshold(grayImg,threshold):
    ret,thresh = cv2.threshold(grayImg,threshold,255,cv2.THRESH_BINARY)
    return ret,thresh
    
def getQPixmap(dataset):
    imgQt = ImageQt(DatasetTools.get_PIL_image(dataset))
    qImg = QImage(imgQt)
    return QPixmap(qImg)
    
def convertPIL2Array(PIL_Image):
    return numpy.array(PIL_Image)

def resizePILImage(PIL_Image,width,height):
    return PIL_Image.resize((width, height),Image.ANTIALIAS)

def convertPIL2Pixmap(PIL_Image):
    return QPixmap(QImage(ImageQt(PIL_Image)))