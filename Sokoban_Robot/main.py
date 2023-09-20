#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
# from pybricks.tools import wait, StopWatch, DataLog
from pybricks.tools import wait
from pybricks.robotics import DriveBase
# from pybricks.media.ev3dev import SoundFile, ImageFile

# Create your objects here.
ev3 = EV3Brick()
# Initialize motors
right_motor = Motor(Port.A)
left_motor = Motor(Port.D)

# Initialize the lightsensors
center_sensor = ColorSensor(Port.S2)
right_sensor = ColorSensor(Port.S4)
left_sensor = ColorSensor(Port.S1)

# Initialize the drivebase
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=120)

# Global variables
SPEED = 100
REFLECTION_RATE = 10
TURN_RADIUS = 95
CORRECTION_ANGLE = 10
# Calculate the light threshold. Choose values based on your measurements.
BLACK = 5
WHITE = 100
threshold = (BLACK + WHITE) / 2

# Set the drive speed at 100 millimeters per second.
DRIVE_SPEED = 100

# Set the gain of the proportional line controller. This means that for every
# percentage point of light deviating from the threshold, we set the turn
# rate of the drivebase to 1.2 degrees per second.

# For example, if the light value deviates from the threshold by 10, the robot
# steers at 10*1.2 = 12 degrees per second.
PROPORTIONAL_GAIN = 1.2
INSTRUCTIONS = ["right", "straight", "turn_around_without_box",
                "left", "left", "left", "straight", "straight"]

# Write your program here.


def run():
    while len(INSTRUCTIONS) > 0:
        if is_intersection():
            print("intersection")
            run_instruction()
        elif right_on_line():
            print("right corner")
            run_instruction()
        elif left_on_line():
            print("left corner")
            run_instruction()
        else:
            go_straight()


def get_direction():
    angle = robot.angle() % 360

    if angle > 330 or angle < 30:
        return "front"
    elif angle > 60 and angle < 120:
        return "right"
    elif angle > 150 and angle < 210:
        return "back"
    elif angle > 240 and angle < 300:
        return "left"
    else:
        return "Unknown angle: " + str(angle) + " degrees"


def run_instruction():
    instruction = INSTRUCTIONS.pop(0)

    straight_distance = 0
    if len(INSTRUCTIONS) > 0:
        straight_distance = 80

    print("Instruction: " + instruction)
    if instruction == "straight":
        robot.straight(straight_distance)
    elif instruction == "right":
        robot.straight(straight_distance)
        turn_right()
        robot.straight(20)
    elif instruction == "left":
        robot.straight(straight_distance)
        turn_left()
        robot.straight(20)
    elif instruction == "turn_around":
        turn_around()
    elif instruction == "turn_around_without_box":
        turn_around_without_box()
    elif instruction == "turn_360":
        turn_360()


def turn_around_without_box():
    robot.straight(-70)
    turn_around()


def turn_around():
    robot.turn(200)


def turn_360():
    robot.turn(360)


def is_intersection():
    return right_on_line() and left_on_line()


def is_corner():
    return right_on_line() or left_on_line()


def right_on_line():
    return right_sensor.reflection() < REFLECTION_RATE


def left_on_line():
    return left_sensor.reflection() < REFLECTION_RATE


def turn_right():
    robot.turn(TURN_RADIUS)


def turn_left():
    robot.turn(-TURN_RADIUS)


def turn_right_amount(degrees):
    robot.turn(degrees)


def turn_left_amount(degrees):
    robot.turn(-degrees)


def go_straight():
    # Calculate the deviation from the threshold.
    deviation = center_sensor.reflection() - threshold

    # Calculate the turn rate.
    turn_rate = PROPORTIONAL_GAIN * deviation

    # Set the drive base speed and turn rate.
    robot.drive(DRIVE_SPEED, turn_rate)

    # You can wait for a short time or do other things in this loop.
    wait(10)


print(get_direction())
turn_left()
print(get_direction())
turn_left()
print(get_direction())
turn_left()
print(get_direction())
turn_left()
print(get_direction())
turn_left()
