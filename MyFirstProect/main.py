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



# Initialize motors
left_motor = Motor(Port.A)
right_motor = Motor(Port.D)

robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=90)

# Constants
forward_distance = 100.62

# Move forward
# robot.straight(forward_distance)

robot.turn(-30)

robot.straight(forward_distance*10)


# robot.turn(-180)

# Turn left
robot.stop()

# Move left
# robot.straight(left_distance)


# left_motor.run_angle(500, 90) 
# right_motor.run_angle(500, -90) 
robot.stop()

# End of program
# brick.sound.beep()




