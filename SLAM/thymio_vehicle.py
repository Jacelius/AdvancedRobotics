from breezyslam.vehicles import WheeledVehicle
import time
import csv
import os
import math

lastTimeStamp = time.time()


class CSVLogger:
    def __init__(self, filename):
        self.filename = filename
        # Check if file exists to decide header writing
        self.write_header = not os.path.exists(self.filename)

    def write(self, data):
        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            if self.write_header:
                writer.writerow(["lastTimeStamp", "Timestamp", "delta_time", "leftWheelSpeed", "rightWheelSpeed",
                                 "LeftWheelDegrees", "RightWheelDegrees"])  # header
                self.write_header = False
            writer.writerow(data)


class ThymioVehicle(WheeledVehicle):

    def __init__(self, wheelRadiusMillimeters, halfAxleLengthMillimeters, csv_filename=None):
        super().__init__(wheelRadiusMillimeters, halfAxleLengthMillimeters)
        self.logger = None
        self.leftWheelDegreesPrev = 0
        self.rightWheelDegreesPrev = 0
        if csv_filename:
            self.logger = CSVLogger(csv_filename)

    def extractOdometry(self, timeStamp, leftWheelSpeed, rightWheelSpeed):
        global lastTimeStamp
        delta_time = timeStamp - lastTimeStamp

        leftWheelChangeInRadians = leftWheelSpeed / 100 * delta_time * (math.pi) / 4.1
        rightWheelChangeInRadians = rightWheelSpeed / 100 * delta_time * (math.pi) / 4.1

        if self.logger:
            self.logger.write((lastTimeStamp, timeStamp, delta_time, leftWheelSpeed, rightWheelSpeed,
                               leftWheelChangeInRadians, rightWheelChangeInRadians))

        lastTimeStamp = timeStamp

        return timeStamp, leftWheelChangeInRadians, rightWheelChangeInRadians

    def computePoseChange(self, timestamp, leftWheelOdometry, rightWheelOdometry):
        '''
        Computes pose change based on odometry.

        Parameters:

            timestamp          time stamp, in whatever units your robot uses
            leftWheelOdometry  odometry for left wheel, in wheel velocity
            rightWheelOdometry odometry for right wheel, in wheel velocity

        Returns a tuple (dxyMillimeters, dthetaDegrees, dtSeconds)

            dxyMillimeters     forward distance traveled, in millimeters
            dthetaDegrees change in angular position, in degrees
            dtSeconds     elapsed time since previous odometry, in seconds
        '''
        dxyMillimeters = 0
        dthetaDegrees = 0
        dtSeconds = 0

        timestampSecondsCurr, leftWheelChangeRadians, rightWheelChangeRadians = \
            self.extractOdometry(timestamp, leftWheelOdometry, rightWheelOdometry)

        if self.timestampSecondsPrev != None:
            dxyMillimeters = self.wheelRadiusMillimeters * \
                             (leftWheelChangeRadians + rightWheelChangeRadians)

            dthetaDegrees = (float(self.wheelRadiusMillimeters) / self.halfAxleLengthMillimeters) * \
                            (math.degrees(leftWheelChangeRadians) - math.degrees(rightWheelChangeRadians))

            dtSeconds = timestampSecondsCurr - self.timestampSecondsPrev

        # Store current odometry for next time
        self.timestampSecondsPrev = timestampSecondsCurr

        # Return linear velocity, angular velocity, time difference
        return dxyMillimeters, dthetaDegrees, dtSeconds

