import copy
import numpy as np
from shortcuts import (adjacent_sides_codes, colors_shortcuts,
					   side_code_to_rotation, adjacent_indices)


class Square:
	def __init__(self, color:str, adjace_colors:list=None):
		self.color = color
		self.color_name = colors_shortcuts[self.color]
		self.adjace_colors = adjace_colors if adjace_colors is not None else list()

	def __str__(self):
		return f"c-{self.color}:" + "".join(self.adjace_colors)

	def __repr__(self):
		return str(self)

	def __len__(self):
		return len(self.adjace_colors) + 1

	def add_adjace_color(self, *colors:str):
		for color in colors:
			self.adjace_colors.append(color)


class RubiksCube:
	def __init__(self, sides_map:list):
		self.sides_map = copy.deepcopy(sides_map)
		for side in range(6):
			for row in range(3):
				for col in range(3):
					self.sides_map[side][row][col] = Square(self.sides_map[side][row][col])

		self.sides_map = np.array(self.sides_map)

		for side in range(6):
			loc_sides_map = copy.deepcopy(self.sides_map)
			for adj_side, rot_n in side_code_to_rotation[side].items():
				loc_sides_map[adj_side] = np.rot90(loc_sides_map[adj_side], rot_n)

			for row in range(3):
				for col in range(3):
					for adj_side, adj_row, adj_col in adjacent_indices[(row, col)]:
						adj_side = adjacent_sides_codes[side][adj_side]
						self.sides_map[side, row, col].add_adjace_color(
							loc_sides_map[adj_side, adj_row, adj_col].color
						)

	def rotate_side(self, side_idx:int, n:int, byclockwise:bool=True):
		# -1 : By clockwise
		# 1 : Counter clockwise
		n %= 4
		n *= -1 if byclockwise else 1

		main_side = int()
		if side_idx == 5 or side_idx == 0:
			main_side = side_idx
		else:
			main_side = (side_idx + 2) % 5 + (side_idx + 2) // 5

		self.rotate_all_cube(target_side_code=side_idx)
		loc_sides_map = copy.deepcopy(self.sides_map)

		# Rotate main side
		self.sides_map[0] = np.rot90(loc_sides_map[0], n)

		# Rotate neighbor squares
		for side in range(1, 5):
			self.sides_map[side, 0, :] = loc_sides_map[(side - n - 1) % 4 + 1, 0, :]

		self.rotate_all_cube(target_side_code=main_side)

	def rotate_all_cube(self, target_side_code:int):
		"""After rotation side with target_side_code will be at the top."""
		if target_side_code == 0:
			return

		new_sides_map = np.empty((6, 3, 3), dtype=Square)

		if target_side_code == 1:
			new_sides_map[0] = self.sides_map[1]
			new_sides_map[1] = np.rot90(self.sides_map[5], 1)
			new_sides_map[2] = np.rot90(self.sides_map[2], -1)
			new_sides_map[3] = np.rot90(self.sides_map[0], 2)
			new_sides_map[4] = np.rot90(self.sides_map[4], 1)
			new_sides_map[5] = np.rot90(self.sides_map[3], 1)

		elif target_side_code == 2:
			new_sides_map[0] = np.rot90(self.sides_map[2], 1)
			new_sides_map[1] = np.rot90(self.sides_map[1], 1)
			new_sides_map[2] = np.rot90(self.sides_map[5], 2)
			new_sides_map[3] = np.rot90(self.sides_map[3], -1)
			new_sides_map[4] = np.rot90(self.sides_map[0], 1)
			new_sides_map[5] = self.sides_map[4]

		elif target_side_code == 3:
			new_sides_map[0] = np.rot90(self.sides_map[3], 2)
			new_sides_map[1] = self.sides_map[0]
			new_sides_map[2] = np.rot90(self.sides_map[2], 1)
			new_sides_map[3] = np.rot90(self.sides_map[5], -1)
			new_sides_map[4] = np.rot90(self.sides_map[4], -1)
			new_sides_map[5] = np.rot90(self.sides_map[1], -1)

		elif target_side_code == 4:
			new_sides_map[0] = np.rot90(self.sides_map[4], -1)
			new_sides_map[1] = np.rot90(self.sides_map[1], -1)
			new_sides_map[2] = np.rot90(self.sides_map[0], -1)
			new_sides_map[3] = np.rot90(self.sides_map[3], 1)
			new_sides_map[4] = self.sides_map[5]
			new_sides_map[5] = np.rot90(self.sides_map[2], 2)

		elif target_side_code == 5:
			new_sides_map[0] = np.rot90(self.sides_map[5], -1)
			new_sides_map[1] = np.rot90(self.sides_map[1], -2)
			new_sides_map[2] = np.rot90(self.sides_map[4], 2)
			new_sides_map[3] = np.rot90(self.sides_map[3], -2)
			new_sides_map[4] = np.rot90(self.sides_map[2], 2)
			new_sides_map[5] = np.rot90(self.sides_map[0], 1)

		self.sides_map = new_sides_map
