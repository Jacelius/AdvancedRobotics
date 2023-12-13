import numpy as np
import cv2

wall_value = 300
safe_zone_value = 900
arena_value = 1400

def is_safe_zone(values):
    print("Safe zone values", values)
    # grey value is below 400?
    if values > safe_zone_value and values < arena_value:
        print("Safe")
        return True
    else:
        return False

def is_outside_arena(values):
    if values < wall_value:
        print("Outside arena")
        return True
    else:
        return False


def get_sum_values(ground_reflected):
    return sum(ground_reflected)

def color(node, rgb_arr):
    node.v.leds.top = rgb_arr
    node.v.leds.bottom.left = rgb_arr
    node.v.leds.bottom.right = rgb_arr


def change_colour(tag_type, ground_values, node):
    if tag_type == "seeker":
        if not is_safe_zone(ground_values):
            color(node, [32, 0, 0])
        else:
            color(node, [32, 10, 0])
    elif tag_type == "avoider":
        if not is_safe_zone(ground_values):
            color(node, [0, 0, 32])
        else:
            color(node, [0, 32, 0])
    else:
        print(f"TYPE UNKNOWN FOR: {tag_type}")
    node.flush()


def check_tagged(message, node):
    if message == "1":  # ladies and gentlemen, we have been tagged :(
        # node.v.leds.top = [0, 0, 32]  # set to purple MISSING
        node.v.motor.left.target = 0
        node.v.motor.right.target = 0
        node.flush()
        return True
    elif message == "2":
        pass
        # now we have to leave the orange zone
        # and disable transmission of "2" for 5 seconds


def should_break_loop(prox_values):
    if sum(prox_values) > 20000:
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


def get_enemy_position(cap, lower_bound, upper_bound, contour_size=250, debug=False):
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

    min_contour_size = contour_size

    # Filter contours based on minimum size
    valid_contours = [
        cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_size]

    # Draw the filtered contours on a new binary image
    result_filtered = np.zeros_like(result_binary)
    cv2.drawContours(result_filtered, valid_contours, -
                     1, (255), thickness=cv2.FILLED)

    # cv2.imwrite("live.jpg", frame)
    # cv2.imwrite("live_filtered.jpg", result_filtered)

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
        node.v.motor.left.target = -400
        node.v.motor.right.target = -100
    elif enemyposition == "right":
        node.v.motor.left.target = -100
        node.v.motor.right.target = -400
    elif enemyposition == "middle":
        node.v.motor.left.target = -400
        node.v.motor.right.target = -400
    else:
        node.v.motor.left.target = 200
        node.v.motor.right.target = -200
    node.flush()
