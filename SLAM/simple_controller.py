"""
Thymio Obstacle Avoidance Controller

This project utilizes the tdmclient library to control a Thymio robot. Specifically,
it makes use of the asynchronous client provided by the library to handle real-time reactions and non-blocking behaviors of the robot.

Important:
- The tdmclient library offers multiple ways of interacting with Thymio robots, both synchronously and asynchronously.
- The library provides capabilities to execute code both on the Thymio robot itself and on external platforms like a Raspberry Pi.
- This current implementation is based on polling the sensors continuously.
    However, for more advanced use-cases, users might want to design the code to be event-driven, reacting to specific triggers or states,
     which can offer more efficient and responsive behaviors.

Setup:
1. Ensure the Thymio robot is connected and powered on.
2. Ensure all required dependencies, including the tdmclient library, are installed.
3. Before running this script, make sure to start the Thymio device manager by executing the following command in the terminal:
    flatpak run --command=thymio-device-manager org.mobsya.ThymioSuite
4. Once the device manager is running, execute this script to initiate the obstacle avoidance behavior of the Thymio robot.
"""

import random
from tdmclient import ClientAsync
from SLAM import LidarController, mainLoop  # Import the LidarController class
import time
from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from rplidar import RPLidar as Lidar
from thymio_vehicle import ThymioVehicle
from visualize_thymio_file import visualizer
import multiprocessing
from multiprocessing import Pipe
import asyncio
import json
import threading


MAP_SIZE_PIXELS = 250
MAP_SIZE_METERS = 15
LIDAR_DEVICE = '/dev/ttyUSB0'
wheel_radius_mm = 21
half_axl_length_mm = 45


class ThymioController:
    def __init__(self):

        thymio = ThymioVehicle(wheel_radius_mm, half_axl_length_mm, None)
        slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)
        # Replace with appropriate arguments
        lidar_controller = LidarController(LIDAR_DEVICE, slam, thymio)
        lidar_thread = threading.Thread(
            target=mainLoop, args=(lidar_controller, 1))
        lidar_thread.start()

        def is_silver_mine(prox_ground_values):
            left_val = prox_ground_values[0]
            right_val = prox_ground_values[1]

            if (left_val > 800 or right_val > 800):
                return True
            return False

        # Use the ClientAsync context manager to handle the connection to the Thymio robot.
        with ClientAsync() as client:

            async def prog():
                """
                Asynchronous function controlling the Thymio's behavior.
                """

                # Lock the node representing the Thymio to ensure exclusive access.
                with await client.lock() as node:

                    # Wait for the robot's proximity sensors to be ready.
                    await node.wait_for_variables({"prox.horizontal"})

                    node.send_set_variables({"leds.top": [0, 0, 32]})
                    print("Thymio started successfully!")
                    while True:
                        if (is_silver_mine(node.v.prox.ground.reflected)):
                            node.v.leds.top = [0, 255, 0]
                            lidar_controller.stop()
                            lidar_controller.disconnect()
                            lidar_thread.join()
                            break

                        if lidar_controller.check_obstacle_in_front((150, 210), 1000):
                            print("Object detected in front!")

                        # speeds = behaviorOA(prox_values)
                        # node.v.motor.left.target = speeds[1]
                        # node.v.motor.right.target = speeds[0]
                        node.flush()  # Send the set commands to the robot.

                        # Pause for 0.3 seconds before the next iteration.
                        await client.sleep(1)

                    # Once out of the loop, stop the robot and set the top LED to red.
                    print("Thymio stopped successfully!")
                    node.v.motor.left.target = 0
                    node.v.motor.right.target = 0
                    node.flush()

            # Run the asynchronous function to control the Thymio.
            client.run_async_program(prog)


if __name__ == "__main__":
    # Instantiate the ThymioController class, which initializes and starts the robot's behavior.
    ThymioController()
