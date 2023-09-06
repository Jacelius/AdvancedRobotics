#!/usr/bin/env pybricks-micropython
import random
import time
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
    robot.drive(0, 0)


def maze(instructionset):
    while len(instructionset) > 0:
        if is_intersection():
            print("Intersection")
            execute_instruction(instructionset[0])
            instructionset.pop(0)
        elif should_correct():
            corrections, turn_state = 0, 0
            while should_correct():
                turn_state += correct_robot()
                print("Turn state: " + str(turn_state))
                corrections += 1
                if corrections > max_num_corrections:
                    print("Is corner, turning: " + str(turn_state))
                    robot.turn(turn_state*1.5)
                    execute_instruction(instructionset[0])
                    instructionset.pop(0)

        else:
            straight()

    brick.sound.beep()


def execute_instruction(instruction):
    # while is_on_atleast_one_line():
    #     straight()
    robot.straight(nudge_dist + 50)
    instruction()
    brick.sound.beep()


def is_on_atleast_one_line():
    if left_light.reflection() < reflection_rate or right_light.reflection() < reflection_rate:
        return True
    else:
        return False


def is_intersection():
    if left_light.reflection() < reflection_rate and right_light.reflection() < reflection_rate:
        return True
    else:
        return False


def should_correct():
    if (left_light.reflection() < reflection_rate and right_light.reflection() > reflection_rate) or (right_light.reflection() < reflection_rate and left_light.reflection() > reflection_rate):
        return True
    else:
        return False


def correct_robot():
    if should_turn_left():
        robot.turn(angle)
        return -angle
    if should_turn_right():
        robot.turn(-angle)
        return angle


def should_turn_left():
    if left_light.reflection() < reflection_rate:
        return True
    else:
        return False


def should_turn_right():
    if right_light.reflection() < reflection_rate:
        return True
    else:
        return False


def straight():
    robot.drive(speed, drive_angle)


def turn_right():
    robot.turn(turn_radius)
    straight()


def turn_left():
    robot.turn(-turn_radius)
    straight()


def is_on_center_line():
    if center_light.reflection() < reflection_rate:
        return True
    else:
        return False


# Initialize motors
left_motor = Motor(Port.A)
right_motor = Motor(Port.D)

# Initialize the lightsensors
left_light = ColorSensor(Port.S4)
right_light = ColorSensor(Port.S1)

robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=90)

# Constants
speed = 100
drive_angle = 0
turn_radius = 90
angle = 5
reflection_rate = 15
max_num_corrections = 2
nudge_dist = 10

# Move forward
# robot.straight(forward_distance)

# flexprogram()
# lightsensorRun()
# target1()
# target2()
# target3()

instructions = [turn_right, turn_left, turn_left,
                straight, turn_right, turn_right, straight, straight, turn_right, straight, turn_right, straight]

simple_instructions = [turn_right, turn_right, straight,
                       straight, turn_right, straight, turn_right]

# maze(instructions)


robot.stop()
