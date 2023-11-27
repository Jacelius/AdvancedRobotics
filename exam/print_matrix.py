import os
import numpy as np

matrix_to_load = input("What matrix would you like to load? ")

q_matrix = np.load(matrix_to_load)

print(q_matrix)