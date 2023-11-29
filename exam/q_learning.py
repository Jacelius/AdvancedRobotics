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


def Q_learning(state):
    if not include_random:
        action = q_matrix[state].argmax()
        print(f"s: {state}, a: {action}, t: {temperature}")
        return action
    else:
        if np.random.uniform(0, 1) < temperature:
            action = np.random.randint(0, actions_size)
        else:
            action = q_matrix[state].argmax()
            print(f"s: {state}, a: {action}, t: {temperature}")
        return action


def update_q(state, action, new_state, reward):
    q_matrix[state, action] = (1 - lr) * q_matrix[state, action] + \
        lr * (reward + gamma * np.max(q_matrix[new_state, :]))