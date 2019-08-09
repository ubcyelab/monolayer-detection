import time
import serial.tools.list_ports
import sys

import stepperControl
import agilisControl
import stage
import joystick

def get_ports():
    
    ports = ['COM%s' % (i + 1) for i in range(256)]

    serial_ports = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            serial_ports.append(port)
        except (OSError, serial.SerialException):
            pass

    return serial_ports


if __name__ == '__main__':

#    agController = agilisControl.Controller('COM5')
#    print(" \n\n =============== Connecting to Motors ===============")
#    sampleStage = stage.Stage('2', agController)
#    holderStage = stage.Stage('3', agController)
#
#    print(" \n\n =============== Initializing Please Wait ===============")
#    sys.stdout.flush()
#    time.sleep(2)
#    print("\n Ready to Begin")
#
#    joy = joystick.joyControl(sampleStage, holderStage)
#    joy.move()

    z = stepperControl.StepperMotor('COM3')
    z.AbsMove(5000)

