from tdmclient import ClientAsync
import cv2
import numpy as np

# "seeker" or "avoider"
tag_type = ""


while (tag_type != "seeker" and tag_type != "avoider"):
    tag_type = input("Do you want to be seeker or avoider? ")


print(tag_type)

seeker_program = """
var send_interval = 200  # time in milliseconds
timer.period[0] = send_interval

leds.top = [32, 0, 0]
leds.bottom.left = [32, 0, 0]
leds.bottom.right = [32, 0, 0]

call prox.comm.enable(1)
onevent timer0
    prox.comm.tx = 1
"""

avoider_program = """
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

actions = [
    (300, 150),  # Left detected
    (300, 300),  # Middle detected
    (150, 300)  # Right detrected
    (150, -150)  # None detected
]

states = [
    "left",
    "middle",
    "right",
    "none"
]

temperature = 1
min_temperature = 0.1
cooling_rate = 0.001
actions_size = len(actions)
states_size = len(states)
q_matrix = np.zeros((actions_size, states_size))

lr = 0.1  # Learning rate
gamma = 0.9  # Discount factor


def get_tag_type(tag: str):
    if (tag == "seeker"):
        return seeker_program
    elif (tag == "avoider"):
        return avoider_program
    else:
        return None


def stop_thymio(node):
    print("Thymio stopped successfully!")
    node.v.motor.left.target = 0
    node.v.motor.right.target = 0
    node.v.leds.top = [32, 0, 0]
    node.flush()


def get_blue_position(cap):
    _, frame = cap.read()

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    cv2.imshow('frame', frame)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    blue_lower = np.array([78, 158, 124])
    blue_upper = np.array([138, 255, 255])
    mask = cv2.inRange(hsv, blue_lower, blue_upper)

    blue_detected_pixels = np.where(mask == 255)
    if len(blue_detected_pixels[1]) > 0:
        avg_x = int(np.mean(blue_detected_pixels[1]))

        if avg_x < width / 3:
            print("Blue is on the left side.")
            return "left"
        elif avg_x > 2 * width / 3:
            print("Blue is on the right side.")
            return "right"

        else:
            print("Blue is in the middle.")
            return "middle"
    print("Nothing detected")
    return "none"


def get_action(action: int):
    return actions[action]


def get_state(reading: str):
    if reading == "left":
        return 0
    elif reading == "middle":
        return 1
    elif reading == "right":
        return 2
    elif reading == "none":
        return 3


def get_reward(state):
    if state == 0:
        return 500
    elif state == 1:
        return 1000
    elif state == 2:
        return 500
    elif state == 3:
        return 0


def Q_learning(state):
    if np.random.uniform(0, 1) < temperature:
        action = np.random.randint(0, actions_size)
    else:
        action = q_matrix[state].argmax()
        print(action, state, temperature)
    return action


def update_q(state, action, new_state, reward):
    q_matrix[state, action] = (1 - lr) * q_matrix[state, action] + \
        lr * (reward + gamma * np.max(q_matrix[new_state, :]))


with ClientAsync() as client:
    async def prog():
        # Lock the node representing the Thymio to ensure exclusive access.
        with await client.lock() as node:
            # Compile and send the program to the Thymio.
            error = await node.compile(get_tag_type(tag_type))
            if error is not None:
                print(f"Compilation error: {error['error_msg']}")
            else:
                error = await node.run()
                if error is not None:
                    print(f"Error {error['error_code']}")

            # Wait for the robot's proximity sensors to be ready.
            await node.wait_for_variables({"prox.horizontal"})
            print("Thymio started successfully!")

            if tag_type == "seeker":  # seeker behavior
                cap = cv2.VideoCapture(0)

                if not cap.isOpened():
                    print("Error: Couldn't open the camera.")
                    return

                while True:
                    # get the values of the proximity sensors
                    prox_values = node.v.prox.horizontal
                    state = get_state(get_blue_position(cap))

                    action = Q_learning(state)

                    speeds = get_action(action)

                    node.v.motor.left.target = speeds[0]
                    node.v.motor.right.target = speeds[1]

                    message = node.v.prox.comm.rx
                    print(f"message from Thymio: {message}")

                    if sum(prox_values) > 20000:
                        break

                    node.flush()  # Send the set commands to the robot.

                    # Pause for 0.3 seconds before the next iteration.
                    await client.sleep(0.1)

                    new_state = get_state(get_blue_position(cap))
                    reward_val = get_reward(new_state)

                    update_q(state, action, new_state, reward_val)

                    await client.sleep(0.1)
            elif tag_type == "avoider":  # avoider behavior
                pass
            else:
                print(
                    f"Behavior not recognized because tag_type is {tag_type}")

            stop_thymio(node)

    # Run the asynchronous function to control the Thymio.
    client.run_async_program(prog)
