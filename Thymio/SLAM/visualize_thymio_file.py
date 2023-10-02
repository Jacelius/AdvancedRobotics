from paho.mqtt import client as mqtt_client


class visualizer:

    broker = "res85.itu.dk"
    client_id = "myid43236"  # Make your own client ID
    username = 'advanced2023'
    password = 'theowlsarenot1992'
    port = 1883
    topic = "mapdata/"  # note: give it your own name so you wont communicate with other robots


    global client

    def connect_mqtt(self):
        def on_connect(sclient, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        username = 'advanced2023'
        password = 'theowlsarenot1992'
        client = mqtt_client.Client(self.client_id)
        client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client

    def publish(self, arr):

        result = self.client.publish(self.topic, payload=arr)
        # print(arr)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print("message sent")
        else:
            print(f"Failed to send message")

    def __init__(self):
        self.client = self.connect_mqtt()
        print("initialized visualizer connection")
        self.client.loop_start()

    def loop(self):
        self.client.loop_start()

