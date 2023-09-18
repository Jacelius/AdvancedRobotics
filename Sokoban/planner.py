import threading
import sys
sys.setrecursionlimit(100000)
wall_coords = []
goal_coords = []
statelist = []

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

def replace_symbols_with_spaces(arr):
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            if arr[i][j] == '@' or arr[i][j] == '$':
                arr[i][j] = ' '
    

def print_grid(grid,state):
    replace_symbols_with_spaces(grid)
    grid[state[0][1]][state[0][0]] = '@'
    for coord in state[1]:
        grid[coord[1]][coord[0]] = '$'
    for row in grid:
        print("".join(row))
    print("\n")


def is_valid_new_state(proposed_state):
    man_coords, diamond_coords = proposed_state
    for coord in diamond_coords: 
        if is_corner(coord):
            if coord not in goal_coords:
                return False # avoid pushing diamond into corner
            print("found a goal in a corner")
            return True # unless it is a goal
    if man_coords not in wall_coords: 
        for coord in diamond_coords:
            if coord in wall_coords:
                return False
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
    if len(goal_coords) == 1:
        return state[1][0] == goal_coords[0]
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
            new_diamond_coords[diamond_index] = (new_diamond_coords[diamond_index][0] - 1, new_diamond_coords[diamond_index][1])
        return (new_man_coords, new_diamond_coords)
    elif (direction == "right"):
        new_man_coords = (state[0][0] + 1, state[0][1])
        if new_man_coords in diamond_coords:
            diamond_index = diamond_coords.index(new_man_coords)
            new_diamond_coords[diamond_index] = (new_diamond_coords[diamond_index][0] + 1, new_diamond_coords[diamond_index][1])
        return (new_man_coords, new_diamond_coords)

def search(state, previous_states, grid, path):
    global statelist
    if is_goal_state(state, goal_coords):
        return path + [state]  # Return the path along with the final state
    else:
        left_state = get_next_state(state, "left")
        right_state = get_next_state(state, "right")
        up_state = get_next_state(state, "up")
        down_state = get_next_state(state, "down")

        if is_valid_new_state(left_state) and left_state not in previous_states:
            statelist.append(left_state)
        if is_valid_new_state(right_state) and right_state not in previous_states:
            statelist.append(right_state)
        if is_valid_new_state(up_state) and up_state not in previous_states:
            statelist.append(up_state)
        if is_valid_new_state(down_state) and down_state not in previous_states:
            statelist.append(down_state)
        previous_states.append(state)
        try:
            return search(statelist.pop(0), previous_states, grid, path + [state])  # Pass path along with state
        except IndexError:
            return None  # No solution found

def main():
    print("started reading")
    input_str = read_input_from_terminal()
    grid, man_coords, diamond_coords = read_input(input_str)
    print("goal_coords: ", goal_coords)
    print("wall coords: ", wall_coords)
    print("diamond coords: ", diamond_coords)
    previous_states = []  # (man_coords, diamond_coords)[]
    state = (man_coords, diamond_coords)
    final_path = search(state, previous_states, grid, [])
    if final_path:
        print("Solution Found!")
        print("The final state is:")
        #print_grid(grid, final_path[-1][0])  # Print the final state
        print("Path:")
        print(f"Number of steps: {len(final_path) - 1}")
        for step, state in enumerate(final_path[1:]):  # Skip the initial state
            print(f"Step {step + 1}: Move {state[0]} to {state[1]}")
    else:
        print("No solution found!")

if __name__ == "__main__":
    main()