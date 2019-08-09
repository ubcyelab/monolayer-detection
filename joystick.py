import pygame

import stage 
import agilisControl
import time


class joyControl(): 

    def __init__(self, sample, disabled = None):
        self.jogSpeed = 0
        self.thresh = 0.1
        self.stopButton = 7
        self.sampleStage = sample
#        self.holderStage = holder
        self.initialized = False
        

        # 1 - 666steps/s; 2 - 1700; 0 - 100 steps/s
        self.mode = {   0: 'medium',
                        1: 'slow',
                        2: 'fast', 
                        3: 'stop'}

        self._pygameStart()

    '''
    Starts pygame so that the joystick cannot control all of the motors
    '''
    def _pygameStart(self):
        pygame.init()
        pygame.joystick.init() 
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.initialized = True
        
    '''
    Quits pygame so that the joystick cannot control anything 
    '''
    def _pygameStop(self):
        self.initialized = False
        pygame.quit()
        
    def _inThreshold(self, val):
        if (abs(val) > self.thresh):
            return int (val/abs(val))
        else:
            return 0

    '''
    Buttons and axes in the list they are recieved by get_button(i), get_axis(i), and get_hat(i) respectively 
        A       0   Medium Speed    |    LX      0  X_1    |   HATX    0    Z_1
        B       1   Slow Speed      |    LY      1  Y_1    |   HATY    1    Z_2
        X       2   Fast Speed      |    LR2     2  R      |
        Y       3   -               |    RX      3  X_1    |
        L1      4   -               |    RY      4  X_2    |
        L2      5   -               |
        R1      6   -               |
        SELECT  7   -               |
        START   8   Quit            |

    '''
    def move(self):

        if not self.initialized:
            self._pygameStart()

        while True:
            for event in pygame.event.get():
                pass

            if (self.joystick.get_button(self.stopButton)):
                self._pygameStop()
                time.sleep(0.05)
                break

            # i = 0 --> A = medium, i = 1 --> B = slow, i = 2 --> X = fast, i = 3 --> Y = stop
            for i in range(0, 4):
                if (self.joystick.get_button(i)):
                    self.sampleStage.setJogSpeed(self.mode[i])
#                    self.holderStage.setJogSpeed(self.mode[i])
            
            LX = self._inThreshold(self.joystick.get_axis(0))
            LY = self._inThreshold(self.joystick.get_axis(1))
#            TR = self._inThreshold(self.joystick.get_axis(2))
#            RX = self._inThreshold(self.joystick.get_axis(3))
#            RY = self._inThreshold(self.joystick.get_axis(4))
            HY = self.joystick.get_hat(0)[1]

            self.sampleStage.jogMotors([-1*LX, -1*LY, HY])
#            self.holderStage.jogMotors([RX, RY])


# Use for testing 
if __name__ == '__main__':

    agController = agilisControl.Controller('COM5')
    sampleStage = stage.Stage('1', agController)
    holderStage = stage.Stage('3', agController)

    time.sleep(3)

    print("Starting Motors")

    joy = joyControl(sampleStage, holderStage)
    joy.move()