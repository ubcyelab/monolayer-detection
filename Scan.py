import datetime
import sys
import time
import os
import numpy as np
import threading 
import warnings


import stage
import joystick
import EOSwindowControl
import monoDetecting

warnings.filterwarnings("error")
    
    
class Scan():
    
    def __init__(self):
        
        print("\n\n=============== Initializing Please Wait ===============")
        
#        self.agController = agilisControl.Controller('COM5')
        self.sampleStage = stage.Stage('2')
#        self.holderStage = stage.Stage('3', self.agController)
        
        sys.stdout.flush()
        time.sleep(1)
        
        print("\nButton List: [A -> medium move], [B -> slow move], [X -> fast move], [Start -> enter info]")
        print("Motor List: [xs -> LX], [ys -> LY], [zs -> HATY], [rs -> LR], [xh -> RX], [yh -> RY], [zh -> HATX]\n")

        # Eventually change this when controller can handle both stages
#        self.joystick = joystick.joyControl(self.sampleStage, self.holderStage)
        self.joystick = joystick.joyControl(self.sampleStage)
        
        # Unit is in mm
        self.pxSize = 900 * 0.56926 / 1000 
        
        self.scanList = []
        
        # Set up camera and picture saving
        today = datetime.datetime.now()
        todayStr = today.strftime('%Y_%m_%d')
        self.nowStr = today.strftime('%Y%m%d%H%M')
        self.imgFolderPath = '../Pictures/%s/' % todayStr
        self.DetectingPath = r"C:\Users\microscope\Desktop\Pictures\%s" % todayStr
        self.ResFolderPath = '../MonolayerResult/%s/' % self.nowStr
          
        self.windowName = "Remote Live View window"
        # Do we need the camwindow object at all, or do we just need to instantiate it?
        EOSwindowControl.setUpEOS(self.windowName)
        
    
        
        print("\n=============== Ready to Begin ===============\n")
    
    
    '''
    Moves the stage with reference to the lens
    '''
    def moveLens(self,From,To):
        self.sampleStage.moveRel([From[0]-To[0], From[1]-To[1], From[2]-To[2]])
#        self.sampleStage.moveRel([From[0]-To[0], From[1]-To[1], To[2]-From[2], 0])
                
        while not ('RDY' in self.sampleStage.getState()):
            pass

    '''
    Internal function,  set the corner limits to get the full area of the scan
    '''
    def setLim(self):
        print("Please find an Empty background and press Start when ready")
        self.joystick.move()
        EOSwindowControl.captureImage(self.windowName)
        time.sleep(3)
        self.backname = os.listdir(self.imgFolderPath)[-1]
        filename = self.nowStr + "(background).jpg"
        os.rename(self.imgFolderPath + self.backname, self.imgFolderPath + filename)
        self.backname = filename
        
        while True:
           
            print('Please go to the Bottom Right corner and focus. Use the joystick, press Start to enter location')  
            self.joystick.move()
            BR = self.sampleStage.currentPos()
            
            print(BR)
            
            print('Please go to the Top Right corner and focus')
            self.joystick.move()
            TR = self.sampleStage.currentPos()
            
            print(TR)
            
            print('Please go to the Top Left corner and focus')
            self.joystick.move()
            TL = self.sampleStage.currentPos()
            
            print(TL)
            
            try:
                
                self.TR = np.array(TL[:3])-np.array(TR[:3])
                self.BR = np.array(TL[:3])-np.array(BR[:3])
                
                x1, y1, z1 = self.TR
                x2, y2, z2 = self.BR
            
                self.numRows = int(y2 // self.pxSize) + 1                               # num pics along Y   
                self.numCols = int(max(x1, x2) // self.pxSize) + 1                      # num pics along X
                self.dzdx = (y2 * z1 - y1 * z2) / (y2 * x1 - y1 * x2)                   # Zstep per px along X
                self.dzdy = (x2 * z1 - x1 * z2) / (x2 * y1 - x1 * y2)                   # Zstep per px along Y
                
                self.totNum = self.numRows * self.numCols
                self.log = {'size': (self.numRows, self.numCols, self.pxSize), 'trace':[]}
                
                if (input("Would you like to respecify the corners? Type y or n\n") == 'n'):
                    break
            # Check what error it actually throws
            except RuntimeWarning:
                print("Corners improperly specified. Please retry.")
            
    '''
        Internal function, calculates the location needed for scanning
    '''     
    def _calcLoc(self, ind):
        X = self.pxSize * (ind[1] - 1)
        Y = self.pxSize * (ind[0] - 1)
        Z = round(self.dzdx * X + self.dzdy * Y)
        
        return np.array([X, Y, Z])

    
    '''
        Scan along the entire area of the sample (x rows and y columns)
    '''
    def fullScan(self):
        
        self.setLim()
            
        EOSwindowControl.focusWindow(self.windowName)
        time.sleep(0.1)
        
        # record old files
        try:
            self.originalFileList = os.listdir(self.imgFolderPath)
        except FileNotFoundError:
            os.mkdir(self.imgFolderPath)
            self.originalFileList = []
            
        ori = len(self.originalFileList)
        
        # create the result folder
        try:
          os.mkdir(self.ResFolderPath)
        except OSError:
          print("Creation of the directory %s failed" % self.ResFolderPath)
        else:
          print("Successfully created the directory %s " % self.ResFolderPath)
        
        f = open(self.ResFolderPath + self.nowStr + '_summary.txt', "w+")
        
        # calculate the scanList
        for j in range(1, self.numRows+1):
            for i in range(1, self.numCols+1):
                if (j % 2 == 0): 
                    self.scanList.append((j, self.numCols - i + 1))
                else:
                    self.scanList.append((j, i))           
        
        # Beginning of scanning, will auto move and take pictures
        for ind in range(len(self.scanList) + 1):
            start = time.time()
            if ind == 0:
               self._moveToNext(ind,self.scanList[ind])
               
            elif ind > 0 and ind < len(self.scanList):
               filename = os.listdir(self.imgFolderPath)[ori+ind-1]
               sys.stdout.flush()
               # Move and take picture
               t1 = threading.Thread(target=self._moveToNext, args=(ind,self.scanList[ind],))
               # Process picture for monolayers
               t2 = threading.Thread(target=monoDetecting.monoDetect, args=(self.DetectingPath + "\%s" % self.backname, self.DetectingPath + "\%s" % filename, self.ResFolderPath, self.log['size'],
                                                     self.scanList[ind-1], self.nowStr, f, ))
               t1.start()
               t2.start()
               t1.join()
               t2.join()
               
            elif ind == len(self.scanList):
               monoDetecting.monoDetect(self.DetectingPath + "\%s" % self.backname, self.DetectingPath + "\%s" % filename, self.ResFolderPath, self.log['size'],
                                                     self.scanList[ind-1], self.nowStr,f)
               
            print("Threading time:", time.time() - start)
            
        f.close()        
            

        
            
         
    def _moveToNext(self,ind,loc):
        EOSwindowControl.captureImage(self.windowName)
        current = self._calcLoc(loc)
        info = (loc, current)
        self.log['trace'].append(info)
        print(('%d / %d ' + str(info)) % (ind + 1, self.totNum))
        try:
            new = self._calcLoc(self.scanList[ind + 1])
            self.moveLens(current, new)
            time.sleep(0.1) #avoid blurring
        except IndexError:
            pass
        
     
    def summary(self):
        # rename the files
        # eg. 201808231001_3x4_1_3
        numPhotos = self.log['size'][0] * self.log['size'][1]
        newFileList = os.listdir(self.imgFolderPath)
        for i in range(5):
            if len(newFileList) != len(self.originalFileList) + numPhotos:
                if i != 4:
                    newFileList = os.listdir(self.imgFolderPath)
                    time.sleep(1)
                else:
                    print('!!  Number of photos doesnt match. Please check.')
            else:
                break
    
        # rename (or crop) the files
        count = 0
        for file in newFileList:
            if file not in self.originalFileList:
                location = self.log['trace'][count][0]
                filename = '%s_%dx%d_%d_%d.jpg' % (
                    self.nowStr, self.log['size'][0], self.log['size'][1], location[0], location[1])
                # croppedImg = rotateCrop(imgFolderPath+file, pxSize+offset, output= imgFolderPath+filename)
                os.rename(self.imgFolderPath + file, self.imgFolderPath + filename)
                count += 1
    
        f = open(self.imgFolderPath + self.nowStr + '_settings.txt', "w+")
        f.write('TR coord ' + str(self.TR) + '\r\n')
        f.write('BR coord ' + str(self.BR) + '\r\n')
        f.write('pxSize ' + str(self.pxSize) + '\r\n')
        f.write('XStride 0.56926 \r\n')
        f.write('YStride 0.56926 \r\n')
        f.close()
        
        print('\nScanning Complete')
                    
        

if __name__ == "__main__":
    
    start = time.time()
    scanObj = Scan()
    scanObj.fullScan()
    scanObj.summary()
    end = time.time()
    print(end-start)
    print(datetime.datetime.now())
    
    



    
    
    
    
    
    