import cv2
import numpy as np


def get_where_is_blue(cap):
    ret, frame = cap.read()

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    cv2.imshow('frame', frame)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # blue_lower = np.array([78, 158, 124])
    # blue_upper = np.array([138, 255, 255])
    blue_lower = np.array([78, 158, 124])
    blue_upper = np.array([138, 255, 255])
    mask = cv2.inRange(hsv, blue_lower, blue_upper)
    result = cv2.bitwise_and(frame, frame, mask=mask)

    cv2.namedWindow('Original Image', cv2.WINDOW_NORMAL)

    # cv2.imshow('Original Image', cv2.resize(frame, (width, height)))
    cv2.imshow('Blue Mask', cv2.resize(mask, (width, height)))
    cv2.imshow('Result', cv2.resize(result, (width, height)))

    # detect contours in the mask and give a position where they are

    blue_detected_pixels = np.where(mask == 255)
    if len(blue_detected_pixels[1]) > 0:
        avg_x = int(np.mean(blue_detected_pixels[1]))

        # Draw bars on the image
        bar_width = 10

        # Calculate the position of the bars based on the detected blue region
        left_bar_position = max(0, avg_x - bar_width // 2)
        right_bar_position = min(width, avg_x + bar_width // 2)

        cv2.rectangle(frame, (left_bar_position, 0), (left_bar_position +
                                                      bar_width, height), (0, 0, 255), -1)  # Left bar
        cv2.rectangle(frame, (right_bar_position - bar_width, 0),
                      (right_bar_position, height), (0, 0, 255), -1)  # Right bar

        if avg_x < width / 3:
            print("Blue is on the left side.")
            cv2.rectangle(frame, (0, 0), (width // 3, height),
                          (0, 255, 0), -1)  # Highlight left section
        elif avg_x > 2 * width / 3:
            print("Blue is on the right side.")
            # Highlight right section
            cv2.rectangle(frame, (2 * width // 3, 0),
                          (width, height), (0, 255, 0), -1)
        else:
            print("Blue is in the middle.")
            # Highlight middle section
            cv2.rectangle(frame, (width // 3, 0),
                          (2 * width // 3, height), (0, 255, 0), -1)

    cv2.imshow('Annotated Image', cv2.resize(frame, (width, height)))


def capture_and_save_image(file_path):
    # Number 0 indicates that we want to capture from the first available camera.
    # If you have more than one camera, you can select the next by replacing 0 with 1, and so forth.
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Couldn't open the camera.")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    cv2.startWindowThread()
    while True:
        ret, frame = cap.read()
        cv2.imshow('frame', frame)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # blue_lower = np.array([78, 158, 124])
        # blue_upper = np.array([138, 255, 255])
        blue_lower = np.array([78, 158, 124])
        blue_upper = np.array([138, 255, 255])
        mask = cv2.inRange(hsv, blue_lower, blue_upper)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        cv2.namedWindow('Original Image', cv2.WINDOW_NORMAL)

        # cv2.imshow('Original Image', cv2.resize(frame, (width, height)))
        cv2.imshow('Blue Mask', cv2.resize(mask, (width, height)))
        cv2.imshow('Result', cv2.resize(result, (width, height)))

        # detect contours in the mask and give a position where they are

        blue_detected_pixels = np.where(mask == 255)
        if len(blue_detected_pixels[1]) > 0:
            avg_x = int(np.mean(blue_detected_pixels[1]))

            # Draw bars on the image
            bar_width = 10

            # Calculate the position of the bars based on the detected blue region
            left_bar_position = max(0, avg_x - bar_width // 2)
            right_bar_position = min(width, avg_x + bar_width // 2)

            cv2.rectangle(frame, (left_bar_position, 0), (left_bar_position +
                          bar_width, height), (0, 0, 255), -1)  # Left bar
            cv2.rectangle(frame, (right_bar_position - bar_width, 0),
                          (right_bar_position, height), (0, 0, 255), -1)  # Right bar

            if avg_x < width / 3:
                print("Blue is on the left side.")
                cv2.rectangle(frame, (0, 0), (width // 3, height),
                              (0, 255, 0), -1)  # Highlight left section
            elif avg_x > 2 * width / 3:
                print("Blue is on the right side.")
                # Highlight right section
                cv2.rectangle(frame, (2 * width // 3, 0),
                              (width, height), (0, 255, 0), -1)
            else:
                print("Blue is in the middle.")
                # Highlight middle section
                cv2.rectangle(frame, (width // 3, 0),
                              (2 * width // 3, height), (0, 255, 0), -1)
        else:
            print("No blue detected")

        cv2.imshow('Annotated Image', cv2.resize(frame, (width, height)))

        if cv2.waitKey(1) == ord('q'):
            break

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
