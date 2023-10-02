#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, ColorSensor,)
from pybricks.parameters import Port
from pybricks.robotics import DriveBase

ev3 = EV3Brick()


def maze_3_sensor(instruction_set):
    while len(instruction_set) > 0:
        if is_corner():
            execute_instruction(instruction_set[0])
            instruction_set.pop(0)
            print("corner \n")
        elif should_correct():
            correct_robot()
            print("correct \n")
        else:
            straight()

        ev3.speaker.beep()


def execute_instruction(instruction):
    robot.straight(nudge_dist + 50)
    instruction()
    ev3.speaker.beep()


def is_intersection():
    return is_on_center_line() and is_on_left_line() and is_on_right_line()


def is_corner():
    if (is_on_left_line() and is_on_center_line()) or (is_on_right_line() and is_on_center_line()):
        return True
    else:
        return False


def is_on_left_line():
    return left_light.reflection() < reflection_rate


def is_on_right_line():
    return right_light.reflection() < reflection_rate


def is_on_center_line():
    return center_light.reflection() < reflection_rate


def should_correct():
    return not is_on_center_line()


def correct_robot():
    if is_on_left_line():
        turn_left_amount(10)
    elif is_on_right_line():
        turn_right_amount(10)
    else:
        print("going backwards \n")
        robot.straight(10)
        if is_on_left_line():
            robot.straight(-5)
            turn_left_amount(20)
        elif is_on_right_line():
            robot.straight(-5)
            turn_right_amount(20)


def straight():
    robot.drive(speed, drive_angle)


def turn_right_amount(degrees):
    robot.turn(degrees)


def turn_right():
    robot.turn(turn_radius)


def turn_left_amount(degrees):
    robot.turn(-degrees)


def turn_left():
    robot.turn(-turn_radius)


# Initialize motors
left_motor = Motor(Port.A)
right_motor = Motor(Port.D)

# Initialize the lightsensors
left_light = ColorSensor(Port.S4)
right_light = ColorSensor(Port.S1)
center_light = ColorSensor(Port.S2)

robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=90)

# Constants
speed = 100
drive_angle = 0
turn_radius = 100
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


maze_3_sensor(instructions)

robot.stop()
