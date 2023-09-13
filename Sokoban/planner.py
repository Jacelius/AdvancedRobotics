import threading
import sys
wall_coords = []
goal_coords = []

def read_input(input_string):
    global wall_coords
    global goal_coords
    man_coords = ()
    diamond_coords = []
    # Split the input_string into lines
    lines = input_string.strip().split('\n')

    # Initialize an empty 2D array
    grid = []

    # Iterate through each line and split it into characters
    for i, line in enumerate(lines):
        row = list(line)
        if '@' in row:
            man_coords = (row.index('@'), i)

        for j in range(len(row)):
            if row[j] == 'X':
                wall_coords.append((j, i))
            if row[j] == '.':
                goal_coords.append((j, i))
            if row[j] == '$':
                diamond_coords.append((j, i))
            if row[j] == '*':
                diamond_coords.append((j, i))
                goal_coords.append((j, i))
        grid.append(row)

    return grid, man_coords, diamond_coords


def read_input_from_terminal():
    print("Enter the input, and press Enter twice to finish:")
    input_lines = []

    while True:
        try:
            line = input()
            if line:
                input_lines.append(line)
            else:
                break
        except EOFError:
            break

    input_string = "\n".join(input_lines)
    return input_string

def add_defaults_to_map():
    # restore goal_coords and diamond_coords
    global grid, goal_coords, diamond_coords, man_coords
    for coord in goal_coords:
        row, col = coord
        grid[row][col] = '.'
    for coord in diamond_coords:
        row, col = coord
        grid[row][col] = '$'
    grid[man_coords[0]][man_coords[1]] = '@'
    

def print_grid():
    global grid
    add_defaults_to_map()
    for row in grid:
        print("".join(row))
    print("\n")

def update_grid(action):
    global man_coords, grid
    if not is_valid_action(action):
        print("Invalid action!!!", action)
        return grid
    coord, direction = action
    row, col = coord
    current_char = grid[row][col]
    grid[row][col] = ' '
    if direction == 'up':
        row -= 1
    elif direction == 'down':
        row += 1
    elif direction == 'left':
        col -= 1
    elif direction == 'right':
        col += 1
    grid[row][col] = current_char
    print_grid()
    return grid

def is_valid_new_state(proposed_state):
    man_coords, diamond_coords = proposed_state
    for coord in diamond_coords: 
        if is_corner(coord):
            if coord not in goal_coords:
                return False # avoid pushing diamond into corner
            return True # unless it is a goal
    if man_coords not in wall_coords and diamond_coords not in wall_coords: 
        return True
    else: 
        return False


def is_corner(coord):
    row, col = coord
    if (row, col+1) in wall_coords and (row+1, col) in wall_coords:
        return True
    elif (row, col-1) in wall_coords and (row+1, col) in wall_coords:
        return True
    elif (row, col+1) in wall_coords and (row-1, col) in wall_coords:
        return True
    elif (row, col-1) in wall_coords and (row-1, col) in wall_coords:
        return True
    else:
        return False

def is_goal_state(state, goal_coords): # state = (man_coords, diamond_coords)
    return state[1] == goal_coords

def get_next_state(state, direction):
    new_man_coords = ()
    diamond_coords = state[1]
    new_diamond_coords = diamond_coords.copy() # might not change
    if (direction == "up"):
        new_man_coords = (state[0][0], state[0][1] - 1)
        if new_man_coords in diamond_coords: # we push a diamond
            diamond_index = diamond_coords.index(new_man_coords)
            new_diamond_coords[diamond_index] = (new_diamond_coords[diamond_index][0], new_diamond_coords[diamond_index][1] - 1)
        return (new_man_coords, new_diamond_coords)
    elif (direction == "down"):
        new_man_coords = (state[0][0], state[0][1] + 1)
        if new_man_coords in diamond_coords:
            diamond_index = diamond_coords.index(new_man_coords)
            new_diamond_coords[diamond_index] = (new_diamond_coords[diamond_index][0], new_diamond_coords[diamond_index][1] + 1)
        return (new_man_coords, new_diamond_coords)
    elif (direction == "left"):
        new_man_coords = (state[0][0] - 1, state[0][1])
        if new_man_coords in diamond_coords:
            diamond_index = diamond_coords.index(new_man_coords)
            new_diamond_coords[diamond_index] = (new_diamond_coords[diamond_index][1] - 1, new_diamond_coords[diamond_index][1])
        return (new_man_coords, new_diamond_coords)
    elif (direction == "right"):
        new_man_coords = (state[0][0] + 1, state[0][1])
        if new_man_coords in diamond_coords:
            diamond_index = diamond_coords.index(new_man_coords)
            new_diamond_coords[diamond_index] = (new_diamond_coords[diamond_index][1] + 1, new_diamond_coords[diamond_index][1])
        return (new_man_coords, new_diamond_coords)

def main():
    print("started reading")
    input_str = read_input_from_terminal()
    _, man_coords, diamond_coords = read_input(input_str)
    previous_states = [] # (man_coords, diamond_coords)[]
    state = (man_coords, diamond_coords)
    search(state, previous_states)
        

def search(state, previous_states):
    if is_goal_state(state, goal_coords):
        print("Goal state reached!")
    else:
        #print("searching from ", state)
        previous_states.append(state)
        left_state = get_next_state(state, "left")
        right_state = get_next_state(state, "right")
        up_state = get_next_state(state, "up")
        down_state = get_next_state(state, "down")
        # print states
        #print()
        #print("left state: ", left_state)
        #print("right state: ", right_state)
        #print("up state: ", up_state)
        #print("down state: ", down_state)
        if is_valid_new_state(left_state) and left_state not in previous_states:
            threading.Thread(target=search, args=(left_state, previous_states)).start()
        elif is_valid_new_state(right_state) and right_state not in previous_states:
            threading.Thread(target=search, args=(right_state, previous_states)).start()
        elif is_valid_new_state(up_state) and up_state not in previous_states:
            threading.Thread(target=search, args=(up_state, previous_states)).start()
        elif is_valid_new_state(down_state) and down_state not in previous_states:
            threading.Thread(target=search, args=(down_state, previous_states)).start()
        else:
            print("No solution found!", file=sys.stderr)
    
main()