man_coords = (1, 1)
goal_coords = []
diamond_coords = []
wall_coords = []

def read_input(input_string):
    global man_coords
    global goal_coords
    global diamond_coords
    # Split the input_string into lines
    lines = input_string.strip().split('\n')

    # Initialize an empty 2D array
    grid = []

    # Iterate through each line and split it into characters
    for i, line in enumerate(lines):
        row = list(line)
        if '@' in row:
            man_coords = (i, row.index('@'))

        for j in range(len(row)):
            if row[j] == 'X':
                wall_coords.append((i, j))
            if row[j] == '.':
                goal_coords.append((i, j))
            if row[j] == '$':
                diamond_coords.append((i, j))
            if row[j] == '*':
                diamond_coords.append((i, j))
                goal_coords.append((i, j))
        grid.append(row)

    return grid


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

def is_valid_action(action):
    global grid
    coord, direction = action
    row, col = coord
    if direction == 'up':
        row -= 1
    elif direction == 'down':
        row += 1
    elif direction == 'left':
        col -= 1
    elif direction == 'right':
        col += 1
    if grid[row][col] == '$':
        is_valid = is_valid_action(((row, col), direction))
        if is_valid:
            #update_grid(((row, col), direction))
            return True
        else:
            return False
            
    if grid[row][col] == ' ' or grid[row][col] == '.':
        return True
    return False

input_string = read_input_from_terminal()
grid = read_input(input_string)

print("man coords", man_coords)
print("goal coords", goal_coords)
print("diamond coords", diamond_coords)
print_grid()
update_grid((man_coords, 'right'))
update_grid((man_coords, 'right'))
update_grid((man_coords, 'down'))


