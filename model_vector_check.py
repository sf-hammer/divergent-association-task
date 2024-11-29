# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 12:00:35 2024

@author: sh23q253
"""

# Path to your vectors.txt file
# vectors_file = 'glove.840B.300d.txt'
vectors = 'model/vectors.txt'

# vectors.txt 301-D
# glove.840B.300d.txt 301-D

# Read the vectors file and check the format
with open(vectors, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Check the number of columns in each line
expected_vector_size = 301  # Assuming you have 1 word + 50 vector components

for i, line in enumerate(lines[:10]):  # Check the first 100 lines (adjust as needed)
    parts = line.strip().split()
    
    if len(parts) != expected_vector_size:
        print(f"Line {i+1} has an incorrect number of columns: {len(parts)} - {line.strip()}")
    else:
        print(f"Line {i+1} seems correct: {line.strip()}")

