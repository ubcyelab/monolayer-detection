import sys
import time
import serial

DEBUG = True

class Controller():

    def __init__(self, portName):
        self.channels = {'1':{'1':None,'2':None},
                         '2':{'1':None,'2':None},
                         '3':{'1':None,'2':None},
                         '4':{'1':None,'2':None}, }

        self.currentChannel = None
        self.activeChannels = []

        for i in range(5):
            self.port = self.connectPort(portName)
            ver = self.sendString('VE')
            if not 'AG-UC8' in ver:
                print('Connection to Agilis Controller failed. Retrying...')
            else:
                print('Connected to Agilis Controller ' + ver[:-5])
                break
            if i == 4:
                raise('Connection to Agilis Controller failed')
        
        self.sendString('MR')

    def addDevice(self, channel, axis):
        try:
            if not (channel in self.activeChannels):
                self.activeChannels.append(channel)
                self.channels[channel]['1'] = AgilisDevice(channel, '1', self)
                self.channels[channel]['2'] = AgilisDevice(channel, '2', self)

            return self.channels[channel][axis]
        except ValueError as e:
            print("I could not add the Agilis Device: ", channel, axis)
            return None

    def connectPort(self, portName = None):
        if (portName == None):
            ## @var AGPort.soul
            self.soul = None
            return None
        try:
            port = serial.Serial(portName,921600,serial.EIGHTBITS,serial.PARITY_NONE,serial.STOPBITS_ONE, timeout=None)
            self.soul = 'p'
            #self.input_buffer_log = []
            time.sleep(0.1)
            return port
        except Exception as e:
            print('I could not find or open the port you specified: {0}'.format(portName))
            self.soul = None
            return None

    def checkNullPort(self):
        return self.soul is None

    def sendString(self, command):
        command += '\r\n'

        sys.stdout.flush()
        bCommand = command.encode()
        self.waitDone()
        self.port.write(bCommand)
        time.sleep(0.01)

        if self.isAquery(command):
            self.port.flush()
            response = self.port.readline()
            sys.stdout.flush()
            return response.decode()

    def waitDone(self):
        while (self.port.inWaiting() != 0):
            pass

    def isAquery(self,command):    
        if self.checkNullPort():
            return False
        queryOnly=["?","PH","TE","TP","TS","VE"]
        command = command.upper()
        for q in queryOnly:
            if command.find(q) != -1:
                return True
        return False
    
    def checkSetChannel(self, channel):
        try:
            currentChannel = self.sendString('CC?')[2:]
            
            if (currentChannel != channel):
    
                while (int(currentChannel) != int(channel)):
                    self.sendString('CC'+channel)
                    currentChannel = self.sendString('CC?')[2:]
                time.sleep(0.1)
                self.currentChannel = channel
        except ValueError:
             self.sendString('CC' + channel)

#    def checkSetChannel(self, channel):
#        currentChannel = self.sendString('CC?')[2:]
#        # if (currentChannel != channel):
#        #     self.sendString('CC'+channel)
#
#        # try: 
#        while (int(currentChannel) != int(channel)):
#            self.sendString('CC'+channel)
#            currentChannel = self.sendString('CC?')[2:]
#        # except ValueError:
#        #     self.sendString('CC' + channel)
#        time.sleep(0.1)
#        self.currentChannel = channel

'''
    # Be careful, not sure it works 
    def reset(self):
        self.controller.sendString('RS')
        self.controller.sendString('MR')

        for i in range(1,5):
            channel = str(i)
            self.channels[channel]['1'] = AgilisDevice(channel, '1', self)
            self.channels[channel]['2'] = AgilisDevice(channel, '2', self)


    # DEBUG THIS
    def finishTask(self):
        while (self.axisBusy()):
            print("stuck in loop ")
            sys.stdout.flush()
            pass

    def axisBusy(self):
        print(self.sendString('1TS')[3:], self.sendString('2TS')[3:])
        return not ((int(self.sendString('1TS')[3:]) == 0) and (int(self.sendString('2TS')[3:]) == 0))

    def getType(self):
        return "agilis"
'''

'''
############################################################################################################### 
############################################# AGILIS DEVICE CLASS ############################################# 
############################################################################################################### 
'''

class AgilisDevice():

    def __init__(self, channel, axis, controller, stepAmp = 50, rate = 750):
        if ((int(channel) not in range(1,5)) or (int(axis) not in range(1,3))):
            raise(ValueError('Please check channel or axis'))
        self.channel    = channel
        self.axis       = axis 
        self.rate       = rate
        self.controller = controller
        self.stepAmp    = str(stepAmp) if (0 < int(stepAmp) <= 50) else str(50)
        self.pos        = 0
        self.prevMove   = 0

        self.states = {'0': 'RDY',
                        '1': 'MOV',
                        '2': 'JOG',
                        '3': 'LIM'}

        # Fast jog makes high-pitched sound
        self.jogs = {  'slow':      2,
                       'medium':    4,
                       'fast':      3,
                       'stop':     0}

        self.send('SU+', self.stepAmp)
        self.send('SU-', self.stepAmp)

        print(self.channel + self.axis, "Axis Object initialized")
        self.__lastOp__ = 'opened'

    def send(self, command, value = None):
        string = (self.axis + command) if (value == None) else (self.axis + command + str(value))
        self.controller.checkSetChannel(self.channel)
        return self.controller.sendString(string)

#======================================================== MOVEMENT FUNCTIONS ======================================================== 

# Add limit control and detection 

    def Init(self):
        # self.reset()
        self.send('PA', 0)

    # Tested 
    def RelMove(self, steps):
        if steps == 0:
            return False

        print("Trying to Move ", self.channel, self.axis)

        self.__lastOp__ = 'moved: ' + str(steps)
        self.send('PR'+str(int(steps)))
        self.send('TP')

    # Test these in conjungtion 
    def home(self):
        curr = self.CurrentPos()
        self.RelMove(-curr)

    # Add safety for limits 
    def AbsMove(self,pos):
        curr = self.CurrentPos()
        rel = pos - curr
        print(pos, curr, rel)
        self.RelMove(rel)

    # Tested
    def stop(self):
        self.send('ST') 


    def jog(self,jogSpeed,dir):
        speed = self.jogs[jogSpeed]*dir

        if ( speed != self.prevMove ):
            self.send('JA', str(speed))
            self.prevMove = speed


#======================================================== INQUIRY FUNCTIONS ======================================================== 

    # CHECK IF THIS TRY AND CATCH IS OKAY
    # CURRENTLY DOES NOT WORK CONTROLLER WILL SAY THAT THE NEXT CURRENT POS
    # IS THE SAME AS WHAT THE LAST ONE WAS SENT TO, MOVE TO SOFTWARE CONTROLLED
    # ABSOLUTE MOVE IN CASE NEW CONTROLLER ALSO DOESN'T WORK
    def CurrentPos(self):
        try:
            return int(self.send('TP')[3:])
        except ValueError:
            return 0

    # Tested
    def GetState(self):
        return self.states[self.send('TS')[3:4]]

    # Tested
    def checkError(self):
        return self.controller.sendString('TE')

    def checkLimit(self):
        return self.controller.sendString('PH')[2:]

    def checkAxisBusy(self):
        return self.send('TS')

    def setZeroPos(self):
        self.send('ZP')

    # def TargetPos(self):
    #     self.Controller.write(encodeMessage('1TH'+endchar))
    #     p = self.Controller.readline().decode()
    #     pos = float(p[3:-2])
    #     return pos
