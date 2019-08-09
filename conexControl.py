# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 16:47:01 2018

@author: microscope
"""

import serial
import time

endchar = '\r\n'
stateError = 'Controller not in the correct state. Current state is '
DEBUG = False

def encodeMessage(message):
    return (str(message)+endchar).encode()

class Controller():
    def __init__(self, address):
        self.ControllerAddress = address
        self.Controller = serial.Serial(address, 921600, xonxoff=True, timeout=0.5)
        print("CONEX-AGP communication open")
        self.stride = 0.56926
        self.lastJS = 'stop'

    def getType(self):
        return "conex"
    
    def CloseSerial(self):
        self.Controller.close()
        print("CONEX-AGP communication closed")
        return

    def sendCommand(self,command,value=None):
        while (self.GetState() != 'RDY'):
            pass

        string = ('1' + command + '\r\n') if (value == None) else ('1' + command + str(value) + '\r\n')
        self.Controller.write(encodeMessage(string))

        try:
            return float(self.Controller.readline().decode()[3:-2])
        except ValueError:
            return None
            
    def GetState(self):
        state = ''
        self.Controller.write(encodeMessage('1TS'))
        p = self.Controller.readline().decode()
        a = p[7]
        b = p[8]
        if a=='0':
            state = 'NRF'
        if a=='1' and b=='0':
            state = 'NRF'
        if a=='1' and b=='4':
            state = 'CON'
        if a=='1' and b=='E':
            state = 'HOM'
        if a=='2':
            state = 'MOV'
        if a=='3' and (b=='2' or b=='3' or b=='4'):
            state = 'RDY'
        if a=='3' and (b=='C' or b=='D'):
            state = 'DIS'
        return state

    def Init(self):
        self.Reset()
        self.HomeSearch()

        while (self.GetState() != 'RDY'):
            pass
    
    def HomeSearch(self):
        state = self.GetState()
        if state=='NRF': 
            self.Controller.write(encodeMessage('1OR'))
        else:
            if DEBUG:
                print(stateError+state+'-HS')
            
    def RelMove(self,dist):
        state = self.GetState()
        if state == 'RDY':
            self.Controller.write(encodeMessage('1PR'+str(dist)+endchar))
        else:
            if DEBUG:
                print(stateError+state)
    
    def AbsMove(self,dist):
        state = self.GetState()
        if state == 'RDY':
            self.Controller.write(encodeMessage('1PA'+str(dist)+endchar))
        else:
            if DEBUG:
                print(stateError+state+' AM')
    
    def CurrentPos(self):
        self.Controller.write(encodeMessage('1TP'+endchar))
        p=self.Controller.readline().decode()
        pos = float(p[3:-2])
        return pos

    def TargetPos(self):
        self.Controller.write(encodeMessage('1TH'+endchar))
        p = self.Controller.readline().decode()
        pos = float(p[3:-2])
        return pos

    def Reset(self):
        self.Controller.write(encodeMessage('1RS'+endchar))
        time.sleep(0.5)
        print('Controller reset')

    def jog(self,jogspeed,dir):
        if ( (jogspeed == 'stop') and (self.lastJS != 'stop') ):
            self.Controller.write(encodeMessage('1ST'+endchar))
            self.lastJS = 'stop'
        elif ( jogspeed != 'stop'):
            self.lastJS = jogspeed
            if(jogspeed == 'medium'):
                self.RelMove(dir*0.56926)
            elif(jogspeed == 'slow'):
                self.RelMove(dir*0.56926/2)
            elif(jogspeed == 'fast'):
                self.RelMove(dir*7)

    def waitReady(self):
        while (self.GetState() != 'RDY'):
            if DEBUG:
                print("\n In Ready loop \n")
    
