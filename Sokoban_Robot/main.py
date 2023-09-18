#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
# from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
# from pybricks.media.ev3dev import SoundFile, ImageFile

# Create your objects here.
ev3 = EV3Brick()
# Initialize motors
right_motor = Motor(Port.A)
left_motor = Motor(Port.D)

# Initialize the lightsensors
center_light = ColorSensor(Port.S2)
right_light = ColorSensor(Port.S1)
left_light = ColorSensor(Port.S4)

# Initialize the drivebase
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=94)

# Global variables
SPEED = 100
REFLECTION_RATE = 20
TURN_RADIUS = 100
CORRECTION_ANGLE = 10
INSTRUCTIONS = ["straight", "straight", "right", "right", "right", "right"]

# Write your program here.


def run():
    while len(INSTRUCTIONS) > 0:
        if is_on_center_line():
            if is_intersection():
                print("intersection \n")
                run_instruction()
            elif is_corner():
                print("corner \n")
                run_instruction()
            else:
                straight()
        else:
            print("Correcting \n")
            correct_robot()
    print("Done \n")


def warning_beep():
    robot.stop()
    ev3.speaker.beep(1, 500)


def run_instruction():
    def go_over_line():
        robot.straight(60)
    instruction = INSTRUCTIONS.pop(0)
    if instruction == "straight":
        print("straight \n")
        go_over_line()
        straight()
        robot.straight(20)
    elif instruction == "right":
        print("right \n")
        go_over_line()
        turn_right()
        robot.straight(20)
    elif instruction == "left":
        print("left \n")
        go_over_line()
        turn_left()
        robot.straight(20)
    elif instruction == "turn_around":
        turn_around()
    elif instruction == "turn_around_without_box":
        turn_around_without_box()
    elif instruction == "turn_360":
        turn_360()
    else:
        warning_beep()
    ev3.speaker.beep()


def correct_robot():
    if is_on_left_line():
        turn_right_amount(10)
    elif is_on_right_line():
        turn_left_amount(5)
    else:
        print("Not on left or right \n")
        while not is_on_center_line():
            turn_left_amount(10)
            if is_on_center_line():
                return
            print("Left not fit \n")
            print("Turning right \n")
            turn_right_amount(40)
            if is_on_center_line():
                return
            print("Neither fit \n")


def is_on_left_line():
    return left_light.reflection() < REFLECTION_RATE


def is_on_right_line():
    return right_light.reflection() < REFLECTION_RATE


def is_on_center_line():
    return center_light.reflection() < REFLECTION_RATE


def is_intersection():
    return is_on_left_line() and is_on_right_line() and is_on_center_line()


def is_corner():
    if is_on_center_line() and is_on_right_line():
        robot.straight(30)
        if is_on_center_line() and is_on_right_line():
            robot.straight(-30)
            print("right corner \n")
            return True
        else:
            robot.straight(-30)
            print("not right corner \n")
            turn_right_amount(30)
            return False
    elif is_on_center_line() and is_on_left_line():
        if is_on_center_line() and is_on_left_line():
            robot.straight(-30)
            print("left corner \n")
            return True
        else:
            robot.straight(-30)
            print("not left corner \n")
            turn_left_amount(30)
            return False
    else:
        return False


def is_right_corner():
    if is_on_center_line() and is_on_right_line():
        return True
    else:
        return False


def is_left_corner():
    if is_on_center_line() and is_on_left_line():
        return True
    else:
        return False


def turn_right():
    robot.turn(TURN_RADIUS)


def turn_left():
    robot.turn(-TURN_RADIUS)


def turn_around():
    robot.turn(180)


def turn_around_without_box():
    robot.straight(-110)
    turn_around()


def turn_360():
    robot.turn(360)


def turn_right_amount(degrees):
    robot.turn(degrees)


def turn_left_amount(degrees):
    robot.turn(-degrees)


def straight():
    robot.drive(SPEED, 0)


run()

# ev3.speaker.beep()
