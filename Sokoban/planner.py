man_coords = (1, 1)
goal_coords = []
diamond_coords = []

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


input_string = read_input_from_terminal()
result = read_input(input_string)

print("man coords", man_coords)
print("goal coords", goal_coords)
print("diamond coords", diamond_coords)