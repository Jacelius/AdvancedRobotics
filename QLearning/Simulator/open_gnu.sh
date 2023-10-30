#!/bin/bash

# Run the Python script
python3 simple_kinematic_simulator.py

# Launch gnuplot and load the visualization script
gnuplot -p -e "load 'simple_visualization.gnu'"

# -p flag is used to keep the gnuplot window open after execution
