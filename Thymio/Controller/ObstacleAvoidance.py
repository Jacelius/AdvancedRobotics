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

        broker="res85.itu.dk"
        port = 1883
        topic = "shouldturn_MAGLEVA/"
        client_id = f'python-mqtt-{"MAGLEVA"}'
        username = 'advanced2023'
        password = 'theowlsarenot1992'

        should_turn = False
        client = connect_mqtt()
        client.on_disconnect = on_disconnect
        subscribe(client)

        def connect_mqtt():
            def on_connect(client, userdata, flags, rc):
                if rc == 0:
                    print("Connected to MQTT Broker!")
                else:
                    print("Failed to connect, return code %d\n", rc)

            # Set Connecting Client ID
            client = mqtt_client.Client(client_id)
            client.username_pw_set(username, password)
            client.on_connect = on_connect
            client.connect(broker, port)
            return client
        
        def subscribe(client: mqtt_client):
            def on_message(msg):
                try:
                    message = msg.payload.decode('utf-8')
                    if message == "True":
                        self.should_turn = True
                    elif message == "False":
                        self.should_turn = False
                    else:
                        print("Invalid message received. Expecting 'True' or 'False'.")
                except Exception as e:
                    print(f"Error processing message: {e}")

            # this only runs the first time to setup callback
            client.subscribe(topic)
            client.on_message = on_message

        def on_disconnect(client, userdata, rc):
            FIRST_RECONNECT_DELAY = 1
            RECONNECT_RATE = 2
            MAX_RECONNECT_COUNT = 12
            MAX_RECONNECT_DELAY = 60
            print("Disconnected with result code: %s", rc)
            reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
            while reconnect_count < MAX_RECONNECT_COUNT:
                print("Reconnecting in %d seconds...", reconnect_delay)
                time.sleep(reconnect_delay)

                try:
                    client.reconnect()
                    print("Reconnected successfully!")
                    return
                except Exception as err:
                    print("%s. Reconnect failed. Retrying...", err)

                reconnect_delay *= RECONNECT_RATE
                reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
                reconnect_count += 1
            print("Reconnect failed after %s attempts. Exiting...", reconnect_count)


        def is_silver_mine(prox_values):
            left_value = prox_values[0]
            right_value = prox_values[4]
            if left_value > 800 or right_value > 800:
                return True
            else:
                return False
            
        def behavior():
            #If we should turn we turn otherwise we go straight
            if self.should_turn:
                return [100, -100]
            return [100, 100]

        # Use the ClientAsync context manager to handle the connection to the Thymio robot.
        with ClientAsync() as client:

            async def prog():
                """
                Asynchronous function controlling the Thymio's behavior.
                """ 
                # Lock the node representing the Thymio to ensure exclusive access.
                with await client.lock() as node:
                    while True: 
                    
                        if isSilverMine(node.v.prox.ground.reflected):
                            #Change color to green
                            node.v.leds.top = [0, 32, 0]
                            node.v.motor.left.target = 0
                            node.v.motor.right.target = 0
                            node.flush()
                            break

                        speeds = behavior()
                        node.v.motor.left.target = speeds[1]
                        node.v.motor.right.target = speeds[0]



                        node.flush()  # Send the set commands to the robot.

                        await client.sleep(0.3)  # Pause for 0.3 seconds before the next iteration.

                    # Once out of the loop, stop the robot and set the top LED to red.
                    print("Thymio stopped successfully!")
                    node.v.motor.left.target = 0
                    node.v.motor.right.target = 0
                    node.v.leds.top = [0, 0, 32]
                    node.flush()

            # Run the asynchronous function to control the Thymio.
            client.run_async_program(prog)


if __name__ == "__main__":
    # Instantiate the ThymioController class, which initializes and starts the robot's behavior.
    ThymioController()
