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

from tdmclient import ClientAsync
from paho.mqtt import client as mqtt_client
import time


class ThymioController:
    def __init__(self):
        # Use the ClientAsync context manager to handle the connection to the Thymio robot.
        with ClientAsync() as client:

            async def prog():
                """
                Asynchronous function controlling the Thymio's behavior.
                """
                # Lock the node representing the Thymio to ensure exclusive access.
                with await client.lock() as node:
                    node.v.leds.top = [0, 0, 32]
                    node.flush()

            # Run the asynchronous function to control the Thymio.
            client.run_async_program(prog)


if __name__ == "__main__":
    # Instantiate the ThymioController class, which initializes and starts the robot's behavior.
    ThymioController()
