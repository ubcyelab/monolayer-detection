# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 15:21:46 2018

@author: microscope
"""

import stepperControl

stepper=stepperControl.StepperMotor('COM3')

def repStep(size,reps):
    for i in range(reps):
        stepper.Step(size)
        if i % 50 ==0:
            print(i)
    print('Stepped '+str(size)+' steps ' +str(reps) +' times')

def step(steps):
    stepper.Step(steps)

def stutter(size,reps):
    for i in range(reps):
        stepper.Step(size)
        stepper.Step(-size)
        if i % 50 ==0:
            print(i)
    print('stuttered '+str(size)+' steps ' +str(reps) +' times')
    
def release(stepper):
    stepper.CloseSerial()
    stepper = stepper.StepperMotor('COM3')
    return stepper

#%%
    
step(-5000)
repStep(100,50)