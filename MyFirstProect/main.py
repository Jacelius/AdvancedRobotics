#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

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

def lightsensorRun():
    while True:
        if lightsensor.reflection() > 20:
            robot.drive(100,0)
        else:
            robot.stop()


# Initialize motors
left_motor = Motor(Port.A)
right_motor = Motor(Port.D)

robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=90)
#lightsensor = ColorSensor(Port.S1)

# Constants


# Move forward
# robot.straight(forward_distance)

#flexprogram()
#lightsensorRun()
#target1()
#target2()
target3()

robot.stop()




