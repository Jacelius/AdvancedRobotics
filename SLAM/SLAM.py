import time
from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from rplidar import RPLidar as Lidar
from thymio_vehicle import ThymioVehicle
from visualize_thymio_file import visualizer
from paho.mqtt import client as mqtt_client
import multiprocessing
from multiprocessing import Pipe
import asyncio
import json

MAP_SIZE_PIXELS = 250
MAP_SIZE_METERS = 15
LIDAR_DEVICE = '/dev/ttyUSB0'
wheel_radius_mm = 21
half_axl_length_mm = 45

class LidarController:
    def __init__(self, device, slam_obj, thymio_vehicle_obj):
        self.lidar = Lidar(device)
        self.slam = slam_obj
        self.thymio = thymio_vehicle_obj
        self.viz = visualizer()
        self.pose = [0, 0, 0]

        # Create an RMHC SLAM object with a laser model and optional robot model
        self.mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
        self.MIN_SAMPLES = 50

        # Create an iterator to collect scan data from the RPLidar
        self.iterator = self.lidar.iter_scans()

        # Connect to MQTT broker
        self.mqtt_client = self.connect_mqtt()
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.loop_start()

    def on_message(self, client, userdata, msg):
        try:
            message = msg.payload.decode('utf-8')
            print("got message")
            if message == "True":
                print("FOUND SILVER MINE. SENDING COORDS: " + str(self.pose[0]) + " " + str(self.pose[1]))
                pos_x_coord = self.pose[0] / 15000 * 250
                pos_y_coord = self.pose[1] / 15000 * 250
                orientation = self.pose[2]
                if (orientation < 0):
                    orientation = 360 + orientation
                print("x: " + str(pos_x_coord)+", y: " + str(pos_y_coord)+", o: "+str(orientation))
                client.publish(topic="silver_coordinates_MAGLEVA/", payload=json.dumps({"x_coord": str(pos_x_coord), "y_coord": str(pos_y_coord), "orientation": str(orientation)}))
                self.viz.publish(json.dumps({"x_coord": str(self.pose[0]), "y_coord": str(self.pose[1]), "orientation": str(self.pose[2]), "silver_mine": "True"}))
        except Exception as e:
            print(f"Error processing message: {e}")

    def connect_mqtt(self):
        broker = "res85.itu.dk"
        port = 1883
        client_id = f'python-mqtt-{"MAGLEVA_SLAM"}'
        username = 'advanced2023'
        password = 'theowlsarenot1992'

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!") 
                self.mqtt_client.subscribe(topic="silver_mine_MAGLEVA/")           
            else:
                print(f"Failed to connect, return code {rc}")

        client = mqtt_client.Client(client_id)
        client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client

    

    def check_obstacle_behind(self, behind_angle_range_degrees, threshold_distance):
        for item in next(self.iterator):
            angle = item[1]
            distance = item[2]
            if angle >= behind_angle_range_degrees[0] and angle <= behind_angle_range_degrees[1]:
                if distance < threshold_distance:
                    print("Object detected in front!")
                    return True
        return False

    async def update(self):
        previous_distances = None
        previous_angles = None

        next(self.iterator)
        while True:  # Keep this infinite for demonstration

            # Extract (quality, angle, distance) triples from current scan
            items = [item for item in next(self.iterator)]
            distances = [item[2] for item in items]
            angles = [item[1] for item in items]

            # todo mack function that gets the speed from the thymio ( left_speed, left_speed)
            left_speed = 0
            right_speed = 0

            poses = self.thymio.computePoseChange(
                time.time(), left_speed, right_speed)

            # Update SLAM with current Lidar scan and scan angles if adequate
            if len(distances) > self.MIN_SAMPLES:
                self.slam.update(distances, pose_change=poses,
                                 scan_angles_degrees=angles)
                previous_distances = distances.copy()
                previous_angles = angles.copy()
            elif previous_distances is not None:
                self.slam.update(previous_distances,
                                 scan_angles_degrees=previous_angles)
            # Get current robot position
            self.pose[0], self.pose[1], self.pose[2] = self.slam.getpos()
            # print(self.pose[0], self.pose[1], self.pose[2])

            # Get current map bytes as grayscale
            self.slam.getmap(self.mapbytes)

            await asyncio.sleep(0.03)

    def publish(self):

        self.viz.publish(self.mapbytes)
        self.viz.publish(
            json.dumps({"x_coord": str(self.pose[0]), "y_coord": str(self.pose[1]), "orientation": str(self.pose[2])}))

    def get_info(self):
        return self.lidar.get_info()

    def get_health(self):
        return self.lidar.get_health()

    def stop(self):
        self.lidar.stop()

    def disconnect(self):
        self.lidar.disconnect()


Running = True

FRONT_ANGLE = (170, 190)


async def mainLoop(lidar, delay):
    task = asyncio.create_task(lidar.update())
    while Running:
        lidar.publish()

        # Check for obstacle behind (angle range: 150 to 210 degrees, distance threshold: 1000 mm)
        if lidar.check_obstacle_behind(FRONT_ANGLE, 300):
            # lidar.mqtt_client.publish(
            #     topic="shouldturn_MAGLEVA/", payload="True")
            o = lidar.pose[2]
            if (o < 0):
                o = 360 + o
            lidar.mqtt_client.publish(
                topic="shouldturn_MAGLEVA/", payload=(json.dumps({"x_coord": str(lidar.pose[0]), "y_coord": str(lidar.pose[1]), "orientation": str(o), "should_turn": "True"})))
        else:
            # lidar.mqtt_client.publish(
            #     topic="shouldturn_MAGLEVA/", payload="False")
            o = lidar.pose[2]
            if (o < 0):
                o = 360 + o
            lidar.mqtt_client.publish(
                topic="shouldturn_MAGLEVA/", payload=(json.dumps({"x_coord": str(lidar.pose[0]), "y_coord": str(lidar.pose[1]), "orientation": str(o), "should_turn": "False"})))

        await asyncio.sleep(delay)
    lidar.stop()
    lidar.disconnect()
    await task

if __name__ == "__main__":
    try:
        thymio = ThymioVehicle(wheel_radius_mm, half_axl_length_mm, None)
        slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)
        lidar = LidarController(LIDAR_DEVICE, slam, thymio)
        loop = asyncio.run(mainLoop(lidar, 0.1))
    except KeyboardInterrupt:
        Running = False
        lidar.stop()
        lidar.disconnect()
