import numpy as np

actions = [
    (100, 400),  # Left detected
    (600, 600),  # Middle detected
    (400, 100),  # Right detrected
    (-100, 100)  # None detected
]

states = [
    "left",
    "middle",
    "right",
    "none"
]

temperature = 0.1
min_temperature = 0.1
cooling_rate = 0.002
actions_size = len(actions)
states_size = len(states)

guiding_matrix = np.array([[500, 100,  50,   0],
                          [125, 500, 125,   0],
                          [50, 100, 500,   0],
                          [0,   0,   0, 500]])


lr = 0.1  # Learning rate
gamma = 0.9  # Discount factor


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
        return 50
    elif state == 1:
        return 500
    elif state == 2:
        return 50
    elif state == 3:
        return 0


def Q_learning(state, q_matrix, include_random=False):
    if np.random.uniform(0, 1) < temperature and include_random:
        action = np.random.randint(0, actions_size)
    else:
        action = q_matrix[state].argmax()
        print(f"s: {state}, a: {action}, t: {temperature}")
    return action


def update_q(q_matrix, state, action, new_state, reward):
    q_matrix[state, action] = (1 - lr) * q_matrix[state, action] + \
        lr * (reward + gamma * np.max(q_matrix[new_state, :]))
