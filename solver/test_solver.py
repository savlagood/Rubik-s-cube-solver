import random
import copy
import numpy as np

from datatypes import RubiksCube
from solver import Solver

def disassemble_rubcube(rubcube:RubiksCube) -> RubiksCube:
	"""Disassemble rebcube."""
	for i in range(10**4 // 2):
		side_idx = random.randint(0, 5)
		n_rots = random.randint(1, 2)
		rubcube.rotate_side(side_idx, n_rots)

	return rubcube

def validation(rubcube:RubiksCube) -> bool:
	"""Validation that rubcube was assembled correct."""
	for side_idx in range(6):
		central_cube_color = rubcube.sides_map[side_idx][1][1].color
		for row_idx in range(3):
			for col_idx in range(3):
				if row_idx == col_idx == 1:
					continue

				color = rubcube.sides_map[side_idx][row_idx][col_idx].color
				if color != central_cube_color:
					return False

	return True

def get_color_from_sides_map(original_sides_map:np.ndarray) -> list:
	"""Generates sides map with colors."""
	original_sides_map = rubcube.sides_map
	sides_map = []
	for side in original_sides_map:
		color_side = []
		for row in side:
			color_row = []
			for cell in row:
				color_row.append(cell.color)

			color_side.append(color_row)

		sides_map.append(color_side)

	return sides_map

sides_map = [
	[['y', 'y', 'y'], ['y', 'y', 'y'], ['y', 'y', 'y']],
	[['b', 'b', 'b'], ['b', 'b', 'b'], ['b', 'b', 'b']],
	[['r', 'r', 'r'], ['r', 'r', 'r'], ['r', 'r', 'r']],
	[['g', 'g', 'g'], ['g', 'g', 'g'], ['g', 'g', 'g']],
	[['o', 'o', 'o'], ['o', 'o', 'o'], ['o', 'o', 'o']],
	[['w', 'w', 'w'], ['w', 'w', 'w'], ['w', 'w', 'w']]
]

rubcube = RubiksCube(sides_map)

iter_num = 100
for i in range(iter_num):
	print(f"======= Iteration: {i+1}/{iter_num} =======")
	original_sides_map = copy.deepcopy(rubcube.sides_map)
	rubcube = disassemble_rubcube(rubcube)
	print("Disassembled")

	with open("last_sides_map.txt", 'w') as f:
		f.write(str(get_color_from_sides_map(rubcube.sides_map)))
		print("Sides map saved to file")

	solver = Solver(rubcube)
	solver.solve()
	rubcube = solver.rubcube
	print("Assembled")

	valid = validation(rubcube)
	if valid:
		print("VALID")
	else:
		print("INVALID")
		print(get_color_from_sides_map(original_sides_map))
