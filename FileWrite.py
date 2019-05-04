import numpy as np
import pydicom
from ImageTools import *

def writeMetaimage(datasets):
    slices = []
    for dataset in datasets:
        imageArr = pydicom.dcmread(dataset)
        imgArray = convertPIL2Array(get_PIL_image(imageArr))
        BGR = convertArray2BGR(imgArray)
        imageGray = convertBGR2Blur2GRAY(BGR)
        ret,thresh1 = segmentThreshold(imageGray,195)
        slices.append(thresh1)
    
    slices = np.array(slices).transpose(2,1,0) 
    writeMHA('FullHead.mha',datasets,slices.shape)
    slices = slices.flatten('F').astype('short')
    slices.tofile('FullHead.raw')

def writeMHA(fn,datasets,dimSize):
		
    dataset = pydicom.dcmread(datasets[0])
    sliceThickness = dataset.SliceThickness
    spacing = dataset.PixelSpacing
    print(dimSize)

   
    if fn.endswith('.mha'):
        f=open(fn, 'w')
        f.write('ObjectType = Image\n')
        print("ObjectType = Image")
        f.write('NDims = 3\n')
        print("NDims = 3")
        f.write('BinaryData = True\n')
        print("BinaryData = True")
        f.write('BinaryDataByteOrderMSB = False\n')
        print("BinaryDataByteOrderMSB = False")
        f.write('CompressedData = False\n')
        print("CompressedData = False")
        f.write('TransformMatrix = -1 0 0 0 1 0 0 0 -1\n')
        print("TransformMatrix = -1 0 0 0 1 0 0 0 -1")
        f.write('Offset = 0 0 0\n')
        print("Offset = 0 0 0")
        f.write('CenterOfRotation = 0 0 0\n')
        print("CenterOfRotation = 0 0 0")
        f.write('AnatomicalOrientation = LAS\n')
        print("AnatomicalOrientation = LAS")
        f.write('ElementSpacing = %.4f %.4f %.1f\n'%(spacing[0],spacing[1],sliceThickness))
        print('ElementSpacing = %.4f %.4f %.1f'%(spacing[0],spacing[1],sliceThickness))
        f.write('ITK_InputFilterName = MetaImageIO\n')
        print("ElementType = MET_SHORT")
        f.write('DimSize = %d %d %d\n'%(dimSize[0],dimSize[1],dimSize[2]))
        print('DimSize = %d %d %d'%(dimSize[0],dimSize[1],dimSize[2]))
        f.write('ElementType = MET_SHORT\n')
        print("ElementType = MET_SHORT")
        f.write('ElementDataFile = %s\n'%fn.replace('.mha','.raw'))
        print('ElementDataFile = %s'% fn.replace('.mha','.raw'))
        f.close()
    elif not fn.endswith('.mha'): ## File extension is not ".mha"
        raise NameError('The input file name is not a mha file!')