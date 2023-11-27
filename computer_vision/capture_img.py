import cv2
import numpy as np

def capture_and_save_image(file_path, filepath2):
    # Number 0 indicates that we want to capture from the first available camera.
    # If you have more than one camera, you can select the next by replacing 0 with 1, and so forth.
    cap = cv2.VideoCapture(0)



    if not cap.isOpened():
        print("Error: Couldn't open the camera.")
        return

    # Read the current frame from the video capture
    ret, frame = cap.read()

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


    frame = cv2.flip(frame, 0)

    frame[:int(0.3 * height), :] = 0


    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    blue_lower = np.array([78, 158, 0])
    blue_upper = np.array([138, 255, 255])
    mask = cv2.inRange(hsv, blue_lower, blue_upper)
    result = cv2.bitwise_and(frame, frame, mask=mask)

    if ret:
        # Save the image on disk
        cv2.imwrite(file_path, result)
        cv2.imwrite(filepath2, frame)
        print(f"Image captured and saved at {file_path}")
    else:
        print("Error: Couldn't grab the frame from the camera.")

    # Release the camera resource
    cap.release()

# Call the function specifying the path where you want to save the image
capture_and_save_image('captured_image_mask.jpg', "captured_image.jpg")
