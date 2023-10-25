import cv2

def capture_and_save_image(file_path):
    # Number 0 indicates that we want to capture from the first available camera.
    # If you have more than one camera, you can select the next by replacing 0 with 1, and so forth.
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Couldn't open the camera.")
        return

    # Read the current frame from the video capture
    ret, frame = cap.read()

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
