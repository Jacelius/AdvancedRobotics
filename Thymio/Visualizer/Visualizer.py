# Example file showing a basic pygame "game loop"
import pygame
import time
import json
from paho.mqtt import client as mqtt_client
import numpy as np


broker = "res85.itu.dk"
port = 1883
topic = "mapdata_magleva/"
client_id = f'python-mqtt-{"MAGLEVA"}'
username = 'advanced2023'
password = 'theowlsarenot1992'


screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()
running = True
mapbytes = bytearray(250 * 250)
pos_x_coord = 250
pos_y_coord = 250
orientation = 0


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


FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60


def on_disconnect(client, userdata, rc):
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


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        if (len(msg.payload) < 200):
            try:
                json_str = msg.payload.decode('utf-8')
                if ("x_coord" in json_str):
                    doc = json.loads(json_str)
                    global pos_x_coord
                    pos_x_coord = float(float(doc["x_coord"]) / 15000 * 250)
                    global pos_y_coord
                    pos_y_coord = float(float(doc["y_coord"]) / 15000 * 250)
                    global orientation
                    orientation = float(doc["orientation"])
                    if (orientation < 0):
                        orientation = 360 + orientation
                    print("x: " + str(pos_x_coord)+", y: " +
                          str(pos_y_coord)+", o: "+str(orientation))
            except:
                print("deserialization of json failed")
        else:
            global mapbytes
            mapbytes = msg.payload

    # this only runs the first time to setup callback
    client.subscribe(topic)
    client.on_message = on_message


client = connect_mqtt()
client.on_disconnect = on_disconnect
subscribe(client)

# pygame setup
pygame.init()
sprite = pygame.image.load('arrow.gif')

while running:
    # poll for events
    client.loop()
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # these are used, but this is how you can transform the bytearray to a matrix
    try:
        mapimg = np.reshape(np.frombuffer(
            mapbytes, dtype=np.uint8), (250, 250))

    except:
        print("skipping this one")
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    # RENDER YOUR GAME HERE
    # pygame.draw.rect(screen, "black", pygame.Rect(50, 50, 1000, 1000), width=5)
    for i in range(len(mapimg)):
        for j in range(len(mapimg[0])):
            y_cord = i * 2
            x_cord = j * 2
            value = mapimg[i][j]
            pygame.draw.rect(screen, (255 - int(value), 255 - int(value), 255 - int(value), 255),
                             pygame.Rect(x_cord, y_cord, 2, 2))

    rot_image = pygame.transform.rotate(sprite, 270 - orientation)
    screen.blit(rot_image, ((pos_x_coord) * 2, (pos_y_coord) * 2))
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(30)  # limits FPS to 30

pygame.quit()
