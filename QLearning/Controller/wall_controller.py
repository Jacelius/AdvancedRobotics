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
import numpy as np
import shapely
from shapely.geometry import LinearRing, LineString, Point
from numpy import sin, cos, pi, sqrt
from random import random
from tdmclient import ClientAsync


class ThymioController:
    action_size = 3
    state_size = 3
    temperature = 1
    min_temperature = 0.1
    cooling_rate = 0.001
    q_matrix = np.zeros((action_size, state_size))
    
    actions = [
        (-300, -300), #too close
        (300, 300), # too far
        (0, 0) # good distance
    ]

    # Learning parameters
    lr = 0.1  # Learning rate
    gamma = 0.9  # Discount factor
    
    prox_max = 3000
    prox_min = 1500

    def __init__(self):
        

        def get_state(self, prox_values):
            """
            3 states. Too close to wall, good distance and too far
            """
            front_sensor_prox = prox_values[2]

            if front_sensor_prox > self.prox_max:
                return 0
            elif front_sensor_prox < self.prox_min:
                return 1
            else:
                return 2

        def update_q_value(self, state,action,prox_values):
            pass

        def get_reward(self, state):
            if state == 0:
                return -500
            elif state == 1:
                return -50
            else:
                return 500

        def Q_learning(self, state):
            if np.random.uniform(0, 1) < self.temperature:
                action = np.random.randint(0, self.action_size)
            else:
                action = self.q_matrix[state].argmax()
                print(action, state, self.temperature)
            return action

        def update_q(self, state, action, new_state, reward):
            self.q_matrix[state, action] = (1 - self.lr) * self.q_matrix[state, action] + \
                self.lr * (reward + self.gamma * np.max(self.q_matrix[new_state, :]))

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

                    await node.wait_for_variables({"prox.horizontal"})

                    node.send_set_variables({"leds.top": [0, 0, 32]})
                    print("Thymio started successfully!")
                    while True:
                        prox_values = node.v.prox.horizontal

                        if sum(prox_values) > 25000:
                            break

                        state = get_state(self, prox_values)
                        if self.temperature > self.min_temperature:
                            self.temperature -= self.cooling_rate


                        action = Q_learning(self, state)

                        speeds = self.actions[action]

                        node.v.motor.left.target = speeds[0]
                        node.v.motor.right.target = speeds[1]

                        node.flush()  # Send the set commands to the robot.

                        await client.sleep(0.1)
                        

                        prox_values = node.v.prox.horizontal
                        new_state = get_state(self, prox_values)
                        reward_val = get_reward(self, new_state)

                        update_q(self, state, action, new_state, reward_val)

                        await client.sleep(0.1)

                    # Once out of the loop, stop the robot and set the top LED to red.
                    print("Thymio stopped successfully!")
                    node.v.motor.left.target = 0
                    node.v.motor.right.target = 0
                    node.v.leds.top = [0, 32, 0]
                    node.flush()

            # Run the asynchronous function to control the Thymio.
            client.run_async_program(prog)


if __name__ == "__main__":
    # Instantiate the ThymioController class, which initializes and starts the robot's behavior.
    ThymioController()
