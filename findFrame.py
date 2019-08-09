#%%
import numpy as np
import datetime
import serial.tools.list_ports
import conexControl
# from imgUtil import rotateCrop

# CONFIGURATION

# length per step:
# X & Y see below
# Z degree per step = 360 / 2048 = 0.175
today = datetime.datetime.now()
todayStr = today.strftime('%Y_%m_%d')
imgFolderPath = '../Pictures/%s/' % todayStr

# px -> length -> step
# 50x
#  pxPerStep={'X+':6.154, 'X-':6.094, 'Y+':5.844, 'Y-':6.205}  #stage motion
# lenPerPx = 0.085070183

# 20x & 1920
pxPerStep={'X+':0.934 ,'X-':0.953, 'Y+':0.858, 'Y-':0.903}
lenPerPx = 0.56926/1000 #unit = mm

# for sample stage movement, adjustable
XstridePx = 1000
YstridePx = 1000
Zstride = 30

Xstride = XstridePx*lenPerPx
Ystride = YstridePx*lenPerPx

pxSize = 900*lenPerPx

windowName = "Remote Live View window"

comlist = serial.tools.list_ports.comports()
connected = [port.device for port in serial.tools.list_ports.comports()]
print("Connected COM ports: " + str(connected))

#stepper = stepperControl.StepperMotor('COM3')
#agController = agilisControl.Controller('COM5')
sampleStageX = conexControl.Controller('COM6')
sampleStageY = conexControl.Controller('COM7')

#%%

def initPosition():
    print('Moving to the starting position...')
    sampleStageX.Reset()
    sampleStageY.Reset()

    sampleStageX.HomeSearch()
    sampleStageY.HomeSearch()
    
    while not (sampleStageX.GetState()=='RDY' and sampleStageY.GetState()=='RDY'):
        pass
    #Start bottom right scan corner at 3,3 mm 
    sampleStageX.AbsMove(3)
    sampleStageY.AbsMove(3)

def findSlope(TR, BR):
    x1, y1, z1 = TR
    x2, y2, z2 = BR
    dzdx = (y2 * z1 - y1 * z2) / (y2 * x1 - y1 * x2)     # Zstep per px along X
    dzdy = (x2 * z1 - x1 * z2) / (x2 * y1 - x1 * y2)
    return dzdx,dzdy    
    
def calLoc(ind,dzdx,dzdy):  # takes a tuple as input
    X = pxSize * (ind[1] - 1)
    Y = pxSize * (ind[0] - 1)         # Unit: mm
    Z = round(dzdx * X + dzdy * Y)  # Unit: step
    new = np.array([X, Y, Z])
    return new

def findLoc():
    ind = ''
    while ind != ' ':
        ind = input("Enter image row,column number (Example: 20,12) or space to end: ")
        if ind == ' ':
            break
        ind = ind.split(',')
    
        for i in range(len(ind)):
            ind[i]=int(ind[i])
    
        loc = calLoc(ind,dzdx,dzdy)

        print('Moving to '+str(ind))
    
        sampleStageX.AbsMove(TL[0]-loc[0])
        sampleStageY.AbsMove(TL[1]-loc[1])
        #stepper.Step(loc[2]-TL[2])
    
    print('Finished')
#%%
    
initPosition()

TR = input("Enter TR values separated by commas: ")
BR = input("Enter BR values separated by commas: ")

TR = TR.split(',')
BR = BR.split(',')
TL = BR

for i in range(len(TR)):
    TR[i]=float(TR[i])
    BR[i]=float(BR[i])
   
 
dzdx,dzdy = findSlope(TR,BR)
    
TL[0]=TL[0]+3
TL[1]=TL[1]+3



#print('Moving to first frame')
#
#sampleStageX.RelMove(TL[0])
#sampleStageY.RelMove(TL[1])
#stepper.Step(-TL[2])
ind = ''
while ind != ' ':
    ind = input("Enter image row,column number (Example: 20,12) or space to end: ")
    if ind == ' ':
        break
    ind = ind.split(',')
    
    for i in range(len(ind)):
        ind[i]=int(ind[i])
    
    loc = calLoc(ind,dzdx,dzdy)

    print('Moving to '+str(ind))
    
    sampleStageX.AbsMove(TL[0]-loc[0])
    sampleStageY.AbsMove(TL[1]-loc[1])
    #stepper.Step(loc[2]-TL[2])
    
print('Finished')

#stepper.CloseSerial()
sampleStageX.CloseSerial()
sampleStageY.CloseSerial()



