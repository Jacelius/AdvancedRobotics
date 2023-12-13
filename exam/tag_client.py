"""
RUN THIS:
flatpak run --command=thymio-device-manager org.mobsya.ThymioSuite

"""

from tdmclient import ClientAsync
import cv2
import numpy as np
from helpers import *
from q_learning import *

# "seeker" or "avoider"
tag_type = "seeker"
debug = True
test_ir_sensor = False
import_matrix = None
save_Q_matrix = False
include_random = False
has_been_tagged = False
set_color = False


wall_value = 300
safe_zone_value = 1100
arena_value = 1400

if(not debug):
    while (tag_type != "seeker" and tag_type != "avoider"):
        tag_type = input("Do you want to be seeker or avoider? ")

    while ((import_matrix != True and import_matrix != False) and tag_type == "seeker"):
        import_matrix_answer = (input("Do you want to import matrix? (y/n): "))
        if (import_matrix_answer == "y"):
            import_matrix = True
        elif (import_matrix_answer == "n"):
            import_matrix = False

    print(tag_type)

    if import_matrix:
        try:
            q_matrix = np.load('nice_matrix.npy')
        except:
            print("No q_matrix numpy file found")
            q_matrix = np.zeros((actions_size, states_size))
    else:
        q_matrix = np.zeros((actions_size, states_size))

    if (tag_type == "seeker"):
        print(q_matrix)


def stop_thymio(node):
    print("Thymio stopped successfully!")
    node.v.motor.left.target = 0
    node.v.motor.right.target = 0
    node.v.leds.top = [0, 0, 32]
    node.flush()


with ClientAsync() as client:
    async def prog():
        global temperature, test_ir_sensor
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

            await node.wait_for_variables({"prox.horizontal"})


            if(set_color):
                ground_prox_values = node.v.prox.ground.reflected
                ground_values = get_sum_values(ground_prox_values)
                change_colour(tag_type, ground_values, node)
                return            

            # Wait for the robot's proximity sensors to be ready.


            print("Thymio started successfully!")
            cap = cv2.VideoCapture(0)

            if tag_type == "seeker":  # seeker behavior
                blue_lower = np.array([78, 128, 50])
                blue_upper = np.array([138, 255, 255])

                if not cap.isOpened():
                    print("Error: Couldn't open the camera.")
                    return

                while True:
                    ground_prox_values = node.v.prox.ground.reflected
                    ground_values = get_sum_values(ground_prox_values)
                    change_colour(tag_type, ground_values, node)
                    # get the values of the proximity sensors
                    prox_values = node.v.prox.horizontal
                    while test_ir_sensor:
                        message = node.v.prox.comm.rx
                        print(f"message from Thymio: {message}")
                        await client.sleep(0.2)

                    if (should_break_loop(prox_values)):
                        break

                    if (is_outside_arena(ground_values)):
                        while (is_outside_arena(ground_values)):
                            await navigate_back_to_arena(node, client)
                            ground_prox_values = node.v.prox.ground.reflected
                            ground_values = get_sum_values(ground_prox_values)
                    else:
                        if(debug):
                            get_enemy_position(cap, blue_lower, blue_upper, contour_size=20, debug=debug)
                            break
                        state = get_state(get_enemy_position(
                            cap, blue_lower, blue_upper))

                        action = Q_learning(state, q_matrix)

                        speeds = get_action(action)

                        if temperature > min_temperature:
                            temperature -= cooling_rate

                        node.v.motor.left.target = speeds[0]
                        node.v.motor.right.target = speeds[1]

                        message = node.v.prox.comm.rx
                        # print(f"message from Thymio: {message}")

                        node.flush()  # Send the set commands to the robot.

                        # Pause for 0.3 seconds before the next iteration.
                        await client.sleep(0.15)

                        new_state = get_state(get_enemy_position(
                            cap, blue_lower, blue_upper))
                        reward_val = get_reward(new_state)

                        update_q(q_matrix, state, action, new_state, reward_val)

                        await client.sleep(0.15)

                cap.release()
                if (save_Q_matrix):
                    print("Saving Q_matrix")
                    np.save('q_matrix.npy', q_matrix)
                    print("Saved Q_matrix")
            elif tag_type == "avoider":  # avoider behavior
                red_lower = np.array([155,50,50])
                red_upper = np.array([179,255,255])
                while test_ir_sensor:
                    message = node.v.prox.comm.rx
                    print(f"message from Thymio: {message}")
                    await client.sleep(0.2)

                while not has_been_tagged:
                    prox_values = node.v.prox.horizontal
                    if (should_break_loop(prox_values)):
                        break

                    ground_values = get_sum_values(
                        node.v.prox.ground.reflected)
                    if is_safe_zone(ground_values):
                        node.v.motor.left.target = 0
                        node.v.motor.right.target = 0
                        node.flush()
                        change_colour(tag_type, ground_values, node)

                        if (debug):
                            break

                    else:

                        get_enemy_position(cap, red_lower, red_upper, contour_size=50, debug=debug)

                        if (debug):
                            break

                        change_colour(tag_type, ground_values, node)

                        avoid_behaviour(node, get_enemy_position(cap, red_lower, red_upper, contour_size=50))

                        await client.sleep(0.2)
            else:
                print(
                    f"Behavior not recognized because tag_type is {tag_type}")

            #stop_thymio(node)

    # Run the asynchronous function to control the Thymio.
    cap = cv2.VideoCapture(0)
    blue_lower = np.array([78, 128, 50])
    blue_upper = np.array([138, 255, 255])
    get_enemy_position(cap, blue_lower, blue_upper, contour_size=10, debug=debug)
    #client.run_async_program(prog)
