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


class ThymioController:
    def __init__(self):
        self.broker = "res85.itu.dk"
        self.port = 1883
        self.topic = "shouldturn_MAGLEVA/"
        self.client_id = f'python-mqtt-{"MAGLEVA_Controller"}'
        self.username = 'advanced2023'
        self.password = 'theowlsarenot1992'

        self.client = mqtt.Client(self.client_id)
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.connect_to_broker()

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
            return [300, 300]

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

                        if is_silver_mine(node.v.prox.ground.reflected):
                            # Change color to green
                            node.v.leds.top = [0, 32, 0]
                            node.v.motor.left.target = 0
                            node.v.motor.right.target = 0
                            node.flush()
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
            message = msg.payload.decode('utf-8')
            if message == "True":
                self.should_turn = True
            elif message == "False":
                self.should_turn = False
            else:
                print("Invalid message received. Expecting 'True' or 'False'.")
            print("on_message: ", message)
            print("new Should_turn: " + str(self.should_turn))
        except Exception as e:
            print(f"Error processing message: {e}")

    def connect_to_broker(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def disconnect_from_broker(self):
        self.client.disconnect()


if __name__ == "__main__":
    # Instantiate the ThymioController class, which initializes and starts the robot's behavior.
    ThymioController()
