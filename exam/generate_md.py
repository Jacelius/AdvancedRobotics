import numpy as np

def read_matrix_from_file(file_path):
    matrix = np.load(file_path)
    return matrix

def generate_markdown_table(matrix, row_names, col_names):
    markdown_table = "| {:^15} |".format("") + " |".join("{:^15}".format(col) for col in col_names) + " |\n"
    markdown_table += "|:--------------:|" + ":--------------:|" * len(col_names) + "\n"

    for i in range(len(matrix)):
        markdown_table += "| {:^15} |".format(row_names[i]) + " |".join("{:^15.5f}".format(value) for value in matrix[i]) + " |\n"

    return markdown_table

def save_markdown_table(markdown_table, output_file):
    with open(output_file, 'w') as file:
        file.write(markdown_table)

# Example usage
matrix_file_path = "q_matrix.npy"
output_markdown_file = "output_table.md"

# Replace these names with your actual row and column names
row_names = ["Turn left", "Straight", "Turn right", "Spin"]
col_names = ["left", "middle", "right", "none"]

matrix = read_matrix_from_file(matrix_file_path)
markdown_table = generate_markdown_table(matrix, row_names, col_names)
save_markdown_table(markdown_table, output_markdown_file)
