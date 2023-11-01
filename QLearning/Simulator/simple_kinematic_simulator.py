import numpy as np
import shapely
from shapely.geometry import LinearRing, LineString, Point
from numpy import sin, cos, pi, sqrt
from random import random

# A prototype simulation of a differential-drive robot with one sensor

# Constants
###########
R = 0.042  # radius of wheels in meters
L = 0.0935  # distance between wheels in meters

W = 2.0  # width of arena
H = 2.0  # height of arena

num_steps = 10_000  # number of simulation steps

robot_timestep = 0.1        # 1/robot_timestep equals update frequency of robot
# timestep in kinematics sim (probably don't touch..)
simulation_timestep = 0.01

# the world is a rectangular arena with width W and height H
world = LinearRing([(W/2, H/2), (-W/2, H/2), (-W/2, -H/2), (W/2, -H/2)])

# Variables
###########

x = 0.0   # robot position in meters - x direction - positive to the right
y = 0.0   # robot position in meters - y direction - positive up
q = 0.0   # robot heading with respect to x-axis in radians

distance_to_sensor_offset = 0.08

left_wheel_velocity = random()   # robot left wheel velocity in radians/s
right_wheel_velocity = random()  # robot right wheel velocity in radians/s

action_size = 3
state_size = 3
temperature = 0.2
q_matrix = np.zeros((action_size, state_size))

# Learning parameters
lr = 0.1  # Learning rate
gamma = 0.9  # Discount factor

# Kinematic model
#################
# updates robot position and heading based on velocity of wheels and the elapsed time
# the equations are a forward kinematic model of a two-wheeled robot - don't worry just use it


def simulationstep():
    global x, y, q

    # step model time/timestep times
    for step in range(int(robot_timestep/simulation_timestep)):
        v_x = cos(q)*(R*left_wheel_velocity/2 + R*right_wheel_velocity/2)
        v_y = sin(q)*(R*left_wheel_velocity/2 + R*right_wheel_velocity/2)
        omega = (R*right_wheel_velocity - R*left_wheel_velocity)/(2*L)

        x += v_x * simulation_timestep
        y += v_y * simulation_timestep
        q += omega * simulation_timestep


def rotate_point(x, y, degrees):
    # Convert angle to radians
    radians = np.radians(degrees)

    # Create a column vector for the point
    point_vector = np.array([x, y])

    # Create the rotation matrix
    rotation_matrix = np.array([[np.cos(radians), -np.sin(radians)],
                                [np.sin(radians), np.cos(radians)]])

    # Apply the rotation matrix to the point
    rotated_point_vector = np.dot(rotation_matrix, point_vector)

    # Extract the new coordinates
    x_new, y_new = rotated_point_vector

    return x_new, y_new


def write_to_trajectory(q, color):
    global x, y
    file.write(str(x) + ", " + str(y) + ", " +
               str(cos(q)*0.2) + ", " + str(sin(q)*0.2) + ", " + color + "\n")


def write_trajectories(directions):
    for i in range(len(directions)):
        if i % 6 == 0:
            write_to_trajectory(directions[i], "0x00D8FF")
        elif i % 6 == 5:  # the rear
            write_to_trajectory(directions[i], "0xFF0000")
        else:
            write_to_trajectory(directions[i], "0x000000")


def get_line_string(q):
    global x, y
    return LineString(
        [(x, y), (x+cos(q)*2*(W+H), (y+sin(q)*2*(W+H)))])


def get_line_strings(qs):
    rays = []

    for q in qs:
        rays.append(get_line_string(q))

    return rays


def turn_angle(degrees):
    global q
    return q + np.radians(degrees)


def turn_on_distance(distance, distance_threshold):
    global left_wheel_velocity, right_wheel_velocity, distance_to_sensor_offset
    if (distance < (distance_threshold + distance_to_sensor_offset)):
        left_wheel_velocity = 0.4
        right_wheel_velocity = -0.4
        return True
    else:
        left_wheel_velocity = 0.4
        right_wheel_velocity = 0.4
        return False


def Q_learning(state):
    global action_size, state_size, temperature, q_matrix
    if np.random.uniform(0, 1) < temperature:
        action = np.random.randint(0, action_size)
    else:
        action = np.argmax(q_matrix[state, :])
        print(action)
    return action


def update_q(state, action, new_state, reward):
    global q_matrix, lr, gamma
    q_matrix[state, action] = (1 - lr) * q_matrix[state, action] + \
        lr * (reward + gamma * np.max(q_matrix[new_state, :]))


def reward(state):  # should return a number
    if (state < 0.04):
        return 0
    elif (state > 0.06):
        return 0
    else:  # between 0.04 and 0.06
        return 10


# Simulation loop
#################
file = open("trajectory.dat", "w")

for cnt in range(num_steps):
    # simple single-ray sensor
    # a line from robot to a point outside arena in direction of q
    q_left = turn_angle(40)
    # q_left_half = turn_angle(20)
    q_right = turn_angle(-40)
    # q_right_half = turn_angle(-20)
    # q_rear = turn_angle(180)

    qs = [q,
          q_left,
          # q_left_half,
          q_right,
          # q_right_half,
          # q_rear
          ]
    rays = get_line_strings(qs)

    # Use front sensor distance
    state = turn_on_distance(world.distance(Point(x, y)), 0.05)
    action = Q_learning(state)

    # Take the action (update left and right wheel velocity)
    if action == 0:
        left_wheel_velocity = -0.4
        right_wheel_velocity = -0.4
    elif action == 1:
        left_wheel_velocity = 0.0
        right_wheel_velocity = 0.0
    elif action == 2:
        left_wheel_velocity = 0.4
        right_wheel_velocity = 0.4

    # for ray in rays:
    #     index = rays.index(ray)

    #     s = world.intersection(ray)
    #     distance = sqrt((s.x-x)**2+(s.y-y)**2)

    #     if (index == 0):  # front sensor
    #         if (turn_on_distance(distance, 0.05)):
    #             break
    #     else:  # any other sensor
    #         if (turn_on_distance(distance, 0.03)):
    #             break
        # distance to wall

    # step simulation
    simulationstep()

    if world.distance(Point(x, y)) < L / 2:
        print(f"Went outside of the arena :(, step: {cnt}, x: {x}, y: {y}")
        break

    # Calculate the new state and reward
    new_state = turn_on_distance(world.distance(
        Point(x, y)), 0.05)  # Use front sensor distance
    reward_value = reward(new_state)

    # Update the Q matrix
    update_q(state, action, new_state, reward_value)

    if cnt % 50 == 0:
        write_trajectories(qs)

file.close()
