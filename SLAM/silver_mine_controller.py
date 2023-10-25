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
import paho.mqtt.client as mqtt
import time
import math
import json


class ThymioController:
    def __init__(self):
        self.broker = "res85.itu.dk"
        self.port = 1883
        self.topic = "shouldturn_MAGLEVA/"
        self.client_id = f'python-mqtt-{"MAGLEVA_CONTROLLER"}'
        self.username = 'advanced2023'
        self.password = 'theowlsarenot1992'

        self.client = mqtt.Client(self.client_id)
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.connect_to_broker()

        self.x_coord = 7500
        self.y_coord = 7500
        self.orientation = 0

        self.should_turn = False

        def is_silver_mine(prox_values):
            # print(prox_values)
            left_value = prox_values[0]
            right_value = prox_values[1]
            if left_value > 800 or right_value > 800:
                return True
            else:
                return False

        def behavior():
            # If we should turn we turn otherwise we go straight
            if self.should_turn:
                return [300, -300]
            return [500, 500]

        def ir_wall_follow(prox_values):
            """
            Obstacle avoidance behavior function.
            Given the proximity sensor values, it determines the Thymio's motion.
            """

            # If an object is detected in front
            if prox_values[2] > 1500:
                return -100, -100
            # If an object is detected on the left
            elif prox_values[0] > 1000:
                return -100, 100
            # If an object is detected on the right
            elif prox_values[4] > 1000:
                return 100, -100
            # If no object is detected, move forward
            else:
                return 100, 100

        def get_angle_to_original_coords(x_current, y_current, orientation_current_deg):
            # Calculate the angle between the current position and the original position
            # original coords is x: 7500, y: 7500
            angle_rad = math.atan2(7500 - y_current, 7500 - x_current)

            # Convert the angle from radians to degrees
            angle_deg = math.degrees(angle_rad)

            # Calculate the new orientation that points towards the original coordinates
            new_orientation_deg = angle_deg - orientation_current_deg

            # returns degrees in negative, so take abs
            return abs(new_orientation_deg)

        async def point_towards_original(client, node, orientation):
            # twist until we're 10 degrees within the original orientation
            # with speed 300 and time 0.3 should be about 20 degrees
            delta_original = orientation

            
            while delta_original < 10:
                print(f"delta_original is: {str(delta_original)}")
                if (delta_original > 180):
                    # turn right
                    l_speed, r_speed = turn_right()
                    set_speeds(node, l_speed, r_speed)
                    await client.sleep(0.3)
                    node.v.motor.left.target = 0
                    node.v.motor.right.target = 0
                    node.flush()
                    delta_original = get_angle_to_original_coords(self.x_coord, self.y_coord, self.orientation)
                elif (delta_original < 180):
                    # turn left
                    l_speed, r_speed = turn_left()
                    set_speeds(node, l_speed, r_speed)
                    await client.sleep(0.3)
                    node.v.motor.left.target = 0
                    node.v.motor.right.target = 0
                    node.flush()
                    delta_original = get_angle_to_original_coords(self.x_coord, self.y_coord, self.orientation)
                else:
                    print(
                        "Error: delta_original is not between 0 and 360. Delta_original: " + str(delta_original))

        def set_speeds(node, left_speed, right_speed):
            node.v.motor.left.target = left_speed
            node.v.motor.right.target = right_speed
            node.flush()  # Send the set commands to the robot.

        def turn_left():
            print("turn left")
            return [-300, 300]

        def turn_right():
            print("turn right")
            return [300, -300]

        def is_on_original_coords(x_current, y_current):
            # max difference the robot can be off by
            difference = 10
            max_difference = 7500 + difference
            min_difference = 7500 - difference
            print(x_current, y_current)
            if ((min_difference < x_current < max_difference) and (min_difference < y_current < max_difference)):
                print("is on coords: "+ str(x_current) + " " + str(y_current))
                return True
            else:
                print("is not on coords: "+ str(x_current) + " " + str(y_current))
                return False

        async def go_straight(node, client, time):
            node.v.motor.left.target = 500
            node.v.motor.right.target = 500
            node.flush()  # Send the set commands to the robot.
            await client.sleep(time)

        # Use the ClientAsync context manager to handle the connection to the Thymio robot.
        with ClientAsync() as client:

            async def prog():
                """
                Asynchronous function controlling the Thymio's behavior.
                """
                # Lock the node representing the Thymio to ensure exclusive access.
                with await client.lock() as node:
                    await node.wait_for_variables({"prox.horizontal"})

                    node.send_set_variables({"leds.top": [0, 0, 32]})
                    print("Thymio started successfully!")

                    while True:
                        # Check if we're on the silver mine
                        if is_silver_mine(node.v.prox.ground.reflected):
                            # Change color to green
                            self.client.publish(
                                topic="silver_mine_MAGLEVA/", payload="True")
                            print("Found silver mine on coords: " + str(self.x_coord) + " " +
                                  str(self.y_coord) + " " + str(self.orientation))

                            while not is_on_original_coords(self.x_coord, self.y_coord):
                                # return to original position
                                # get difference in orientation between current and original
                                delta_original = get_angle_to_original_coords(
                                    self.x_coord, self.y_coord, self.orientation)
                                print("Delta original: " + str(delta_original))

                                await point_towards_original(client, node, delta_original)

                                # go straight until object is detected in front
                                while not self.should_turn:
                                    await go_straight(node, client, 0.5)

                                    # check if we're off course and break out of loop if we are to go onto course again. We can be off by 20 degrees
                                    # this might fail as it should probably be the delta to the original orientation
                                    # if (self.orientation > 10 and self.orientation < 350):
                                    #     break

                                    # possible fix:
                                    delta_original = get_angle_to_original_coords(
                                        self.x_coord, self.y_coord, self.orientation)
                                    
                                    if (delta_original > 10 and delta_original < 350):
                                        break

                                # corregate course by turning left or right or do wall following behavior. Maybe go a bit backwards first?
                                # t_end = time.time() + 20
                                # while time.time() < t_end:
                                #     l_speed, r_speed = ir_wall_follow(
                                #         node.v.prox.horizontal)
                                #     set_speeds(node, l_speed, r_speed)
                                #     await client.sleep(0.3)
                            break

                        # print("This is shouldturn: " + str(self.should_turn))
                        speeds = behavior()
                        node.v.motor.left.target = speeds[0]
                        node.v.motor.right.target = speeds[1]

                        node.flush()  # Send the set commands to the robot.

                        # Pause for 0.3 seconds before the next iteration.
                        await client.sleep(0.3)

                    # Once out of the loop, stop the robot and set the top LED to red.
                    print("Thymio stopped successfully!")
                    node.flush()

            # Run the asynchronous function to control the Thymio.
            client.run_async_program(prog)

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        self.client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        try:
            json_str = msg.payload.decode('utf-8')
            message = json.loads(json_str)
            if message["should_turn"] == "True":
                self.should_turn = True
            elif message["should_turn"] == "False":
                self.should_turn = False
            else:
                print("Invalid message received. Expecting 'True' or 'False'.")

            self.x_coord = float(float(message["x_coord"]))
            self.y_coord = float(float(message["y_coord"]))
            self.orientation = float(float(message["orientation"]))

        except Exception as e:
            print(f"Error processing message: {e}")

    def connect_to_broker(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def disconnect_from_broker(self):
        self.client.disconnect()


if __name__ == "__main__":
    try:
        ThymioController()
    except KeyboardInterrupt:
        pass
