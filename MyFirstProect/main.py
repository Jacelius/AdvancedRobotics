#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks import ev3brick as brick


# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.

def target1():
    forward_distance = 100.52
    robot.turn(-26.57)
    robot.straight(forward_distance*10)
    robot.turn(-140)

def target1Reverse():
    forward_distance = 100.52
    robot.turn(140)
    robot.straight(-(forward_distance*10))
    robot.turn(26.57)

def target2():
    forward_distance = 107
    robot.straight(forward_distance*10)

def target2Reverse():
    forward_distance = 107
    robot.straight(-(forward_distance*10))


def target3():
    forward_distance = 100
    robot.straight(forward_distance*10)
    robot.turn(90)
    robot.straight(45*10)

def target3Reverse():
    robot.straight(-(45*10))
    robot.turn(-90)
    robot.straight(-(100*10))

def flexprogram():
    target1()
    target1Reverse()
    target2()
    target2Reverse()
    target3()
    target3Reverse()

def pause():
    robot.drive(0,0)

def maze():
    while True:
        if isCorner():
            if should_turn_left():
                robot.turn(-5)
            if should_turn_right():
                robot.turn(5)
            brick.sound.beep()
        elif isIntersection():
            # pause()
            brick.sound.beep()
            straight()
        else:
            straight()

def isIntersection():
    if left_light.reflection() < 15 and right_light.reflection() < 15:
        return True
    else:
        return False

def isCorner():
    if (left_light.reflection() < 15 and right_light.reflection() > 15) or (right_light.reflection() < 15 and left_light.reflection() > 15):
        return True
    else:
        return False

def should_turn_left():
    if left_light.reflection() < 15:
        return True
    else:
        return False
    
def should_turn_right():
    if right_light.reflection() < 15:
        return True
    else:
        return False

def straight():
    robot.drive(100, 0)

def turn_right():
    robot.turn(90)
    straight()


def turn_left():
    robot.turn(-90)        
    straight()

# Initialize motors
left_motor = Motor(Port.A)
right_motor = Motor(Port.D)

# Initialize the lightsensors
left_light = ColorSensor(Port.S4)
right_light = ColorSensor(Port.S1)

robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=90)

# Constants


# Move forward
# robot.straight(forward_distance)

#flexprogram()
#lightsensorRun()
#target1()
#target2()
# target3()

maze()


##use the speaker too beep  
#

robot.stop()




