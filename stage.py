import stepperControl
import conexControl


class Stage():

    ## functions depending on absolute move may not work due to TP (number of steps command) not functioning properly

    ''' 
    Initialization function used to set the type of stage
        Type == 1: Sample stage, no seperate feedback for the x and y linear motors
        Type == 2: Sample stage, seperate feedback for the x and y linear motors
        Type == 3: Holder stage
    '''

    def __init__(self, type, agController=None):
        self.agController   = agController
        self.jogSpeed       = 'slow'
        self.stopFlag       = -1
        self.currMotor      = None
        self.currIndex      = -1

        if (type == '1'):
            self._initSample(False, agController)
        elif (type == '2'):
            self._initSample(True, agController)
        elif (type == '3'):
            self._initHolder(agController)

    ''' 
    Initialization function used for the sample stage. Has the additional input to use overloading. Has x y z and r
    control, Z is a stepper motor and r is a rotation piezo stage. 
        feedback:       if the feedback is closed (False) or open (True) ie: if the x and y motor are
                        connected to their own controllers (True), if everything is connected to UC8 (False)
        agController:   controller object for the agilis controller UC8 
    '''

    def _initSample(self, feedback, agController):
        self.name           = 'Sample Stage'
        self.start          = [3,3,0,0]
        self.stride         = [2000,2000,30,500]
        self.feedback       = feedback

        # Edit channels back to in order, changed since the controller is not working

        if (feedback == True):
            # Check these com ports
            print("Setting up Motors")
            self.x = conexControl.Controller('COM6')
            self.y = conexControl.Controller('COM7')

            self.x.Init()
            self.y.Init()

            self.x.AbsMove(self.start[0])
            self.y.AbsMove(self.start[1])

            self.x.waitReady()
            self.y.waitReady()
        else:
            self.x = agController.addDevice(channel='1', axis='1')
            self.y = agController.addDevice(channel='2', axis='1')
            # self.x = agController.addDevice(channel='1', axis='2')
            # self.y = agController.addDevice(channel='2', axis='2')

#        self.r = agController.addDevice(channel='4', axis='1')
        self.z = stepperControl.StepperMotor('COM3')
#        self.z = agController.addDevice(channel='3', axis='1')
        
        self.motors = { 'piezo': [self.x, self.y],
                           'stepper': [self.z], 
                           'xyzr': [self.x, self.y, self.z] }

    '''
    Initialization function used for the holder stage. Has x y and z control all piezo motors. 
        agController:   controller object for the agilis controller UC8 
    '''
    def _initHolder(self, agController):
        self.name           = 'Holder Stage'
        self.start          = [0, 0, 0]
        self.stride         = [2000,2000,2000]

        # Edit channels back to in order, changed since the controller is not working

        self.x = agController.addDevice(channel='1', axis='1')
        self.y = agController.addDevice(channel='2', axis='1')
#        self.z = agController.addDevice(channel='4', axis='1')

        # Add back z motor when controller is fixed
        self.motors = { 'piezo': [self.x, self.y],
                        'stepper': [],
                        'xyzr': [self.x, self.y]  }


#======================================================== INQUIRY AND SETTING FUNCTIONS ======================================================== 

    '''
    Returns the x and y motors for use with closed feedback.
    '''                   
    def getConex(self):
        return self.x, self.y

    '''
    Returns the position of all the motors in the stage in the order of [x, y, z, r]; r will not
    be included in the case that there is no rotation axis for the stage so list will either be
    of length 3 or length 4.
    '''

    # Could possibly be wrong due to faulty controller mixing up information !!!!!

    def currentPos(self):
        return [motor.CurrentPos() for motor in self.motors['xyzr']]


    '''
    Sets the speed that all motors will jog at (either slow - 100 steps/s, medium - 666steps/s, or 
    fast - 1700).
        speed: either 'medium', 'slow', 'fast', or 'stop'
    '''
    def setJogSpeed(self, speed):
        self.jogSpeed = speed
        
    '''
    Returns the state of all of the motors up to the index specified. The states are returned in a list
    in the order of [x,y,z,r]. If no index is specified, the function will only return [x,y]
        ind: index with which to return the specified motors. Ind should be less than 3 or 4 depending
            on the stage type (whether it has an r motor). If an invalid index is given, returns the whole
            list
    ''' 
    def getState(self,ind=2):
        try:
            return [motor.GetState() for motor in self.motors['piezo'][:ind]]
        except IndexError:
            return [motor.GetState() for motor in self.motors['piezo']]
    
    '''
    Closes the communication between the conex x and y motors
    '''
    def close(self):
        try:
            if (self.feedback):
                self.x.CloseSerial()
                self.y.CloseSerial()
        except IndexError:
            print("Can only close Conex Controlled Motors")


#======================================================== MOVEMENT FUNCTIONS ======================================================== 

    '''
    sets the stage to the initial position given by the self.start variable. The z stepper motor
    is not moved due to it being a stepper and must be set on its own. The rotation stage is set 
    to go to the zero position. Initialization of piezo's may take significant amount of time
    (up to two minutes, as it must hit both limit switches). At this time, do not put a sample on 
    the stage.
    '''

    # Test this, it does not work, could possibly be due to faulty controller mixing up information !!!!!

    def initPos(self):
        print('Moving ' + self.name + ' to the starting position...')

        for motor in self.motors['piezo']:
            motor.Init()
            
        self.moveAbs(self.start)


    '''
    moves the three motors to the positions specified by loc = [x,y,z,r]. Note that about 2000
    steps is 1 mm for piezo linears motors, ___stepper_____needs to be checked______, and about 500 steps 
    is 1 degree for r.
    
        loc:    [x_move, y_move, z_move, r_move], for the holder stage r_movedegree does 
                not need to be included. 
    '''

    # THIS ONE DOES NOT WORK SINCE THE CURRENT POSITION FUNCTION ON CONTROLLER IS NOT WORKING
    # POSSIBLY DUE TO FAULTY CONTROLLER. JOG AND MOVEREL DO WORK, USE THOSE INSTEAD

    def moveAbs(self, loc):
        try:
            for index, motor in enumerate(self.motors['xyzr']): 
                motor.moveAbs(loc[index])
        except AttributeError:
            print('Missing specified locations, please re-specify using 0 for no movement')


    '''
    moves the three motors by the amount specified by steps = [x,y,z,r]. Note that about 2000
    steps is 1 mm for piezo linear motors, ___stepper_____needs to be checked______, and about 500 steps 
    is 1 degree for r.

        steps:   [x_move, y_move, z_move, r_move], for the holder stage r_movedegree does 
                not need to be included. 
    '''
    def moveRel(self, steps):
        try: 
            for index, motor in enumerate(self.motors['xyzr']): 
                motor.RelMove(steps[index])
        except AttributeError:
            print('Missing specified locations, please re-specify using 0 for no movement')

    
    '''
    Sets the given motors to jog. Note that the controller does not allow you to jog more than one motor
    at a time. The jogging algorithm will already handle stopping the moving motor when switching directions. 
    Also note that it works in such a way that the motors in the front of the list will jog before the motors 
    in the back of the list if more than one motor is being told to jog at the same time, ie: if the dir [1,0,0,1]
    is sent through, motor1 will move, but motor4 will not. To move motor4 the command dir = [0,0,0,1]  or 
    dir = [0,0,0,1] must be sent through. 
        Dir:    should be specified as a list of directions matching the amount of motors. -1 means go backwards, 
                0 means stop, and +1 means go forwards.
    '''
    def jogMotors(self, dir):

        if (len(dir) == len(self.motors['xyzr'])):
            try:
                if not ( (1 in dir) or (-1 in dir)):
                    self.currMotor.jog('stop', 0)

                else:

                    for index, motor in enumerate(self.motors['xyzr']):

                        direc = dir[index]

                        if ( direc != 0 ):
                            if (self.currIndex != index):
                                try:
                                    self.currMotor.jog('stop', 0)
                                except AttributeError:
                                    pass
                                self.currMotor = motor 
                                self.currIndex = index
                                motor.jog(self.jogSpeed, direc)
                            else:
                                motor.jog(self.jogSpeed, direc)
                            break
            except AttributeError:
                pass




