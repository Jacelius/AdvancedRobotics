import numpy as np
import cv2


def is_safe_zone(values):
    print("Safe zone values", values)
    # grey value is below 400?
    if values > 400:
        print("Safe")
        return True
    else:
        print("NOT SAFE")
        return False


def get_sum_values(ground_reflected):
    return sum(ground_reflected)


def change_colour(tag_type, ground_values, node):
    if tag_type == "seeker":
        if not is_safe_zone(ground_values):
            node.v.leds.top = [255, 0, 0]
        else:
            node.v.leds.top = [255, 165, 0]
    elif tag_type == "avoider":
        if not is_safe_zone(ground_values):
            node.v.leds.top = [0, 0, 255]
        else:
            node.v.leds.top = [0, 255, 0]
    else:
        print(f"TYPE UNKNOWN FOR: {tag_type}")
    node.flush()


def check_tagged(message, node):
    if message == 1:  # ladies and gentlemen, we have been tagged :(
        has_been_tagged = True
        node.v.leds.top = [0, 0, 255]  # set to purple
        node.v.motor.left.target = 0
        node.v.motor.right.target = 0
        node.flush()
    elif message == 2:
        pass
        # now we have to leave the orange zone
        # and disable transmission of "2" for 5 seconds


def should_break_loop(prox_values):
    if sum(prox_values) > 20000:
        return True
    else:
        return False


def is_outside_arena(ground_prox_values):
    wall_value = 10
    if ground_prox_values[0] < wall_value or ground_prox_values[1] < wall_value:
        return True
    else:
        return False


def get_seeker_program():
    return """
var send_interval = 200  # time in milliseconds
timer.period[0] = send_interval

leds.top = [32, 0, 0]
leds.bottom.left = [32, 0, 0]
leds.bottom.right = [32, 0, 0]

call prox.comm.enable(1)
onevent timer0
    prox.comm.tx = 1
"""


def get_avoider_program():
    return """
var send_interval = 200  # time in milliseconds
timer.period[0] = send_interval
call prox.comm.enable(1)
leds.top = [0, 32, 0]

timer.period[0] = send_interval

onevent timer0
    prox.comm.tx = 2
    
onevent prox.comm
    if prox.comm.rx == 1 then
        leds.top = [32, 0, 32]
        leds.bottom.left = [32, 0, 32]
        leds.bottom.right = [32, 0, 32]
    end
    
"""


def get_tag_type(tag: str):
    if (tag == "seeker"):
        return get_seeker_program()
    elif (tag == "avoider"):
        return get_avoider_program()
    else:
        return None


async def navigate_back_to_arena(node, client):
    node.v.motor.left.target = -400
    node.v.motor.right.target = -100
    node.flush()

    await client.sleep(0.2)


def get_enemy_position(cap, lower_bound, upper_bound, debug=False):
    ret, frame = cap.read()
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frame = cv2.flip(frame, 0)
    frame = cv2.flip(frame, 1)

    frame[:int(0.3 * height), :] = 0

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Make non-black pixels white
    _, result_binary = cv2.threshold(result, 1, 255, cv2.THRESH_BINARY)
    result_binary = cv2.cvtColor(result_binary, cv2.COLOR_BGR2GRAY)

    # Find contours
    contours, _ = cv2.findContours(
        result_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    min_contour_size = 250

    # Filter contours based on minimum size
    valid_contours = [
        cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_size]

    # Draw the filtered contours on a new binary image
    result_filtered = np.zeros_like(result_binary)
    cv2.drawContours(result_filtered, valid_contours, -
                     1, (255), thickness=cv2.FILLED)

    if debug:
        if ret:
            cv2.imwrite("img1.jpg", mask)
            cv2.imwrite("img2.jpg", frame)
            cv2.imwrite("result_filtered.jpg", result_filtered)

    detected_pixels = np.where(result_filtered == 255)
    if len(detected_pixels[1]) > 0:
        avg_x = int(np.mean(detected_pixels[1]))

        if avg_x < width / 3:
            print("LEFT")
            return "left"
        elif avg_x > 2 * width / 3:
            print("RIGHT")
            return "right"

        else:
            print("MIDDLE")
            return "middle"
    # print("Nothing detected")
    return "none"


def avoid_behaviour(node, enemyposition):
    if enemyposition == "left":
        node.v.motor.left.target = 100
        node.v.motor.right.target = -100
    elif enemyposition == "right":
        node.v.motor.left.target = -100
        node.v.motor.right.target = 100
    elif enemyposition == "middle":
        node.v.motor.left.target = 100
        node.v.motor.right.target = -100
    else:
        node.v.motor.left.target = 200
        node.v.motor.right.target = -200
    node.flush()