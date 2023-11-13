import cv2
import numpy as np

def capture_and_save_image(file_path):
    # Number 0 indicates that we want to capture from the first available camera.
    # If you have more than one camera, you can select the next by replacing 0 with 1, and so forth.
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Couldn't open the camera.")
        return

    width = 500
    height = 400


    cv2.startWindowThread()
    blueDetected = False
    while True:
        ret, frame = cap.read()
        cv2.imshow('frame', frame)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        blue_lower = np.array([90, 50, 50])
        blue_upper = np.array([120, 255, 255])
        mask = cv2.inRange(hsv, blue_lower, blue_upper)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        cv2.imshow('Original     Image', cv2.resize(frame, (width, height)))
        cv2.imshow('Blue Mask', cv2.resize(mask, (width, height)))
        cv2.imshow('Result', cv2.resize(result, (width, height)))

        if cv2.waitKey(1) == ord('q'):
            break
        if blueDetected == True:
            print("Blue Detected")

    if ret:
        # Save the image on disk
        cv2.imwrite(file_path, frame)
        print(f"Image captured and saved at {file_path}")
    else:
        print("Error: Couldn't grab the frame from the camera.")

    # Release the camera resource
    cap.release()

# Call the function specifying the path where you want to save the image
capture_and_save_image('captured_image.jpg')
