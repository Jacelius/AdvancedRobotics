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


all_search_states = []

def main():
    global all_search_states
    
    print("started reading")
    input_str = read_input_from_terminal()
    grid, man_coords, diamond_coords = read_input(input_str)
    print("goal_coords: ", goal_coords)
    print("wall coords: ", wall_coords)
    print("diamond coords: ", diamond_coords)
    previous_states = [] # (man_coords, diamond_coords)[]
    state = (man_coords, diamond_coords,0,0)
    all_search_states.append(state)
    search(state, previous_states,grid, None)
        


def search(state, previous_states,grid,previous_state):
    global statelist
    global all_search_states
    own_index = state[2]
    man_cords = state[0]
    parent_index = state[3]

    #print_grid(grid, state)
    if is_goal_state(state, goal_coords):
        print("Goal state reached!")
        print_grid(grid, state)
    else:
        nextindex = own_index 
        left_state = get_next_state(state, "left")
        right_state = get_next_state(state, "right")
        up_state = get_next_state(state, "up")
        down_state = get_next_state(state, "down")
        if is_valid_new_state(left_state) and left_state not in previous_states:
            nextindex += 1
            left_state = (left_state[0], left_state[1], nextindex, own_index)
            statelist.append(left_state)
            all_search_states.append(left_state)
        if is_valid_new_state(right_state) and right_state not in previous_states:
            #print("valid right state", right_state)
            nextindex += 1
            right_state = (right_state[0], right_state[1], nextindex, own_index)
            statelist.append(right_state)
            all_search_states.append(right_state)
        if is_valid_new_state(up_state) and up_state not in previous_states:
            nextindex += 1
            up_state = (up_state[0], up_state[1], nextindex, own_index)
            statelist.append(up_state)
            all_search_states.append(up_state)
        if is_valid_new_state(down_state) and down_state not in previous_states:
            nextindex += 1
            down_state = (down_state[0], down_state[1], nextindex, own_index)
            statelist.append(down_state)
            all_search_states.append(down_state)
        previous_states.append((state[0], state[1]))
        try: 
            search(statelist.pop(0), previous_states,grid)
        except IndexError:
            print("No solution found!")
            return
        
if __name__ == "__main__":
    main()