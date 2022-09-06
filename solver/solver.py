import copy
import numpy as np

from datatypes import RubiksCube
from shortcuts import (adjacent_sides_colors, sides_codes,
					   counter_side, adjacent_sides_codes)


side_idx_by_best_side = {
	0: {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
	1: {0: 1, 1: 5, 2: 2, 3: 0, 4: 4, 5: 3},
	2: {0: 2, 1: 5, 2: 3, 3: 0, 4: 1, 5: 4},
	3: {0: 3, 1: 5, 2: 4, 3: 0, 4: 2, 5: 1},
	4: {0: 4, 1: 5, 2: 1, 3: 0, 4: 3, 5: 2},
	5: {0: 5, 1: 1, 2: 4, 3: 3, 4: 2, 5: 0},
}


class Solver:
	"""
	Some most common variable names:
	- side_idx - code of the side: 
		0 - Top, 1 - front, 2 - left, 3 - back, 4 - right, 5 - bottom.
	- 
	"""
	def __init__(self, rubcube:RubiksCube) -> None:
		"""Initialize the main params to solving"""
		self.rubcube = copy.deepcopy(rubcube)
		# Color to code coding
		self.color_to_code = dict()
		# Contains rotations codes which is a triplets 012 where (0) is code of side,
		# (1) is number of spins, (2) is directon (by/counter clock wise)
		self.solving_steps = list()

	def color_to_code_init(self) -> None:
		"""Code colors to codes and writes this pairs to self.color_to_code"""
		for code in range(6):
			color = self.rubcube.sides_map[code, 1, 1].color
			self.color_to_code[color] = code
			self.color_to_code[code] = color

	def rotate_side(self, side_idx:int, n:int, byclockwise:bool=True) -> None:
		"""
		Rotate self.rubcube side with side_idx n times byclockwise.
		Add rotation code to self.solving_steps
		"""
		n %= 4

		if n == 3:
			n = 1
			byclockwise = not byclockwise

		self.solving_steps.append(f"{side_idx}{n}{int(byclockwise)}")
		self.rubcube.rotate_side(side_idx=side_idx, n=n, byclockwise=byclockwise)

	def solve(self) -> list:
		"""
		Looking for the optimal solution out of six possible solutions.
		Each of six sides may be main one
		"""
		rubcube = copy.deepcopy(self.rubcube)

		best_side = -1
		best_solving_steps = list()

		for main_side_idx in range(5, 6):
			# Clean solving steps
			self.solving_steps = list()
			# Cloning main rubcube
			self.rubcube = copy.deepcopy(rubcube)
			self.rubcube.rotate_all_cube(target_side_idx=main_side_idx)
			# Code the colors and get main_color (color of top central cube)
			self.color_to_code_init()
			# Solving
			self.solve_0_layer_crosspiece()
			self.solve_0_layer_corners()
			self.solve_1_layer_corners()
			self.solve_2_layer_crosspiece()
			self.solve_2_layer_corners()
			# Optimization
			self.optim_solving_steps()

			# Is best this solving way?
			if len(best_solving_steps) > len(self.solving_steps) or not best_solving_steps:
				best_side = main_side_idx
				best_solving_steps = self.solving_steps

		best_solving_steps = list(map(lambda s: f"{side_idx_by_best_side[best_side][int(s[0])]}{s[1]}{s[2]}", best_solving_steps))
		return best_solving_steps

	def solve_0_layer_crosspiece(self) -> None:
		"""Solves the crosspiece of the top layer."""
		main_color = self.rubcube.sides_map[0][1, 1].color

		# Rotates top side to best position
		for cube_idx in range(4):
			cross_cubes = self.get_cross_cubes(side_idx=0)
			cube = cross_cubes[cube_idx]

			if cube.color == main_color:
				target_idx = self.color_to_code[cube.adjace_colors[0]] - 1
				rot_n = (target_idx - cube_idx) % 4
				self.rotate_side(0, rot_n, byclockwise=False)
				break

		# Iterates over all crosspieces cubes on the top side and moves them to the
		# correct positions
		for side_idx in range(4):
			cross_cubes = self.get_cross_cubes(side_idx=0)
			cube = cross_cubes[side_idx]

			if cube.color == main_color:
				target_idx = self.color_to_code[cube.adjace_colors[0]] - 1
				rot_n = (target_idx - side_idx) % 4

				self.rotate_side(side_idx + 1, 1, byclockwise=False)
				self.rotate_side(0, rot_n, byclockwise=True)
				self.rotate_side(side_idx + 1, 1, byclockwise=True)
				self.rotate_side(0, rot_n, byclockwise=False)

		while True:
			# Checks that top crosspiece was solved
			counter = 0
			for cube in self.get_cross_cubes(side_idx=0):
				if cube.color == main_color:
					counter += 1

			if counter == 4:
				break

			# Handle from 1 to 4 side
			for side_idx in range(1, 5):
				for cube_position, (row_idx, col_idx) in enumerate(self.get_cross_indices()):
					cube = self.rubcube.sides_map[side_idx, row_idx, col_idx]
					if cube.color == main_color:
						# Cube at the bottom of side
						if cube_position == 0:
							adj_side = (side_idx - 1 + 1) % 4 + 1
							target_idx = self.color_to_code[cube.adjace_colors[0]]
							rot_n = (target_idx - adj_side) % 4

							self.rotate_side(0, rot_n, byclockwise=True)
							self.rotate_side(side_idx, 1, byclockwise=False)
							self.rotate_side(adj_side, 1, byclockwise=True)
							self.rotate_side(side_idx, 1, byclockwise=True)
							self.rotate_side(0, rot_n, byclockwise=False)

						# Cube at the right of side
						elif cube_position == 1:
							adj_side = (side_idx - 1 + 1) % 4 + 1
							target_idx = self.color_to_code[cube.adjace_colors[0]]
							rot_n = (target_idx - adj_side) % 4

							self.rotate_side(0, rot_n, byclockwise=True)
							self.rotate_side(adj_side, 1, byclockwise=True)
							self.rotate_side(0, rot_n, byclockwise=False)

						# Cube at the top of side
						elif cube_position == 2:
							adj_side = (side_idx - 1 + 1) % 4 + 1
							target_idx = self.color_to_code[cube.adjace_colors[0]]
							rot_n = (target_idx - adj_side) % 4

							self.rotate_side(side_idx, 1, byclockwise=True)
							self.rotate_side(0, rot_n, byclockwise=True)
							self.rotate_side(adj_side, 1, byclockwise=True)
							self.rotate_side(0, rot_n, byclockwise=False)

						# Cube at the left of side
						elif cube_position == 3:
							adj_side = (side_idx - 1 - 1) % 4 + 1
							target_idx = self.color_to_code[cube.adjace_colors[0]]
							rot_n = (target_idx - adj_side) % 4

							self.rotate_side(0, rot_n, byclockwise=True)
							self.rotate_side(adj_side, 1, byclockwise=False)
							self.rotate_side(0, rot_n, byclockwise=False)

			# Handle 5 side
			sequence = [0, 2, 1, 3]
			cross_indices = self.get_cross_indices()
			for cube_position in sequence:
				row_idx, col_idx = cross_indices[cube_position]
				cube = self.rubcube.sides_map[5, row_idx, col_idx]
				if cube.color == main_color:
					adj_side = (cube_position + 2 * (cube_position % 2 == 0)) % 5
					target_idx = self.color_to_code[cube.adjace_colors[0]]
					rot_n = (target_idx - adj_side) % 4

					self.rotate_side(0, rot_n, byclockwise=True)
					self.rotate_side(adj_side, 2, byclockwise=True)
					self.rotate_side(0, rot_n, byclockwise=False)

	def solve_0_layer_corners(self) -> None:
		"""Solves the corners of the top layer."""
		main_color = self.rubcube.sides_map[0][1][1].color
		while True:
			# Checks that top corners was solved
			counter = 0
			for cube_position, cube in enumerate(self.get_corner_cubes(side_idx=0)):
				adj_color = self.rubcube.sides_map[cube_position + 1, 1, 1].color
				if cube.color == main_color and adj_color in cube.adjace_colors:
					counter += 1

			if counter == 4:
				break

			# Handle 0 side
			for cube_position, (row_idx, col_idx) in enumerate(self.get_corner_indices()):
				cube = self.rubcube.sides_map[0, row_idx, col_idx]
				if cube.color == main_color:
					adj_side = cube_position + 1
					if self.rubcube.sides_map[adj_side, 1, 1].color not in cube.adjace_colors:
						target_idx = self.color_to_code[self.rubcube.sides_map[adj_side, 0, 2].color]
						rot_n = (target_idx - adj_side) % 4

						self.pif_paf(main_side_idx=0, adj_side_idx=adj_side)
						self.rotate_side(side_idx=5, n=rot_n, byclockwise=True)
						self.back_pif_paf(main_side_idx=0, adj_side_idx=target_idx)

			# Handle 1-4 sides
			for side_idx in range(1, 5):
				for cube_position, (row_idx, col_idx) in enumerate(self.get_corner_indices()):
					cube = self.rubcube.sides_map[side_idx, row_idx, col_idx]
					if cube.color == main_color:
						# Cube at the bottom of side
						if cube_position == 0:
							adj_side = side_idx % 4 + 1
							target_idx = self.color_to_code[self.rubcube.sides_map[adj_side, 2, 0].color]
							rot_n = (target_idx - adj_side) % 4

							self.rotate_side(side_idx=5, n=rot_n, byclockwise=True)
							self.pif_paf(main_side_idx=0, adj_side_idx=(target_idx - 2) % 4 + 1)

						# Cube at the right of side
						elif cube_position == 1:
							adj_side = side_idx % 4 + 1
							self.pif_paf(main_side_idx=0, adj_side_idx=side_idx)

							target_idx = self.color_to_code[self.rubcube.sides_map[adj_side, 2, 0].color]
							rot_n = (target_idx - adj_side) % 4

							self.rotate_side(side_idx=5, n=rot_n, byclockwise=True)
							self.pif_paf(main_side_idx=0, adj_side_idx=(target_idx - 2) % 4 + 1)

						# Cube at the top of side
						elif cube_position == 2:
							adj_side = (side_idx - 2) % 4 + 1
							self.back_pif_paf(main_side_idx=0, adj_side_idx=adj_side)

							target_idx = self.color_to_code[self.rubcube.sides_map[adj_side, 2, 2].color]
							rot_n = (target_idx - adj_side) % 4

							self.rotate_side(side_idx=5, n=rot_n, byclockwise=True)
							self.back_pif_paf(main_side_idx=0, adj_side_idx=target_idx)

						# Cube at the left of side
						elif cube_position == 3:
							adj_side = (side_idx - 2) % 4 + 1
							target_idx = self.color_to_code[self.rubcube.sides_map[adj_side, 2, 2].color]
							rot_n = (target_idx - adj_side) % 4

							self.rotate_side(side_idx=5, n=rot_n, byclockwise=True)
							self.back_pif_paf(main_side_idx=0, adj_side_idx=target_idx)

			# Handle 5 side
			for cube_position, (row_idx, col_idx) in enumerate(self.get_corner_indices()):
				cube = self.rubcube.sides_map[5, row_idx, col_idx]
				if cube.color == main_color:
					adj_side = (abs(3 - cube_position) + 1) % 4 + 1
					target_idx = self.color_to_code[self.rubcube.sides_map[adj_side, 2, 2].color]
					rot_n = (target_idx - (adj_side % 4 + 1)) % 4

					self.rotate_side(side_idx=5, n=rot_n, byclockwise=True)
					for _ in range(3):
						self.pif_paf(main_side_idx=0, adj_side_idx=(target_idx - 2) % 4 + 1)

	def solve_1_layer_corners(self):
		"""Solves the corners of the middle layer."""
		handled_cubes = 0
		top_color = self.rubcube.sides_map[5, 1, 1].color

		# Handle every cross cube at top layer
		while handled_cubes < 4:
			handled_cubes_before = handled_cubes
			for i, (row, col) in enumerate(self.get_cross_indices()):
				cube = self.rubcube.sides_map[5, row, col]
				if cube.color != top_color and cube.adjace_colors[0] != top_color:
					handled_cubes += 1

					curr_side_idx = (abs(i - 3) - 2) % 4 + 1
					target_idx_1 = self.color_to_code[cube.color]
					target_idx_2 = self.color_to_code[cube.adjace_colors[0]]
					rot_n = (target_idx_2 - curr_side_idx) % 4

					self.rotate_side(side_idx=5, n=rot_n, byclockwise=True)
					self.set_middle_corner(
						side_1_idx=target_idx_1,
						side_2_idx=target_idx_2,
						corner_side=target_idx_2,
					)

			if handled_cubes_before == handled_cubes:
				changed = False
				for side_idx in adjacent_sides_codes[0]:
					side_color = self.rubcube.sides_map[side_idx, 1, 1].color
					cube = self.rubcube.sides_map[side_idx, 1, 2]

					next_side_idx = side_idx % 4 + 1
					next_side_color = self.rubcube.sides_map[next_side_idx, 1, 1].color

					top_color = self.rubcube.sides_map[5, 1, 1].color
					if cube.color != top_color and cube.adjace_colors[0] != top_color:
						changed = True
						if cube.color != side_color:
							self.set_middle_corner(
								side_1_idx=side_idx,
								side_2_idx=next_side_idx,
								corner_side=next_side_idx,
							)
						elif cube.adjace_colors[0] != next_side_color:
							handled_cubes += 1
							self.rotate_side(side_idx=side_idx, n=2)
							self.rotate_side(side_idx=5, n=2)
							self.rotate_side(side_idx=side_idx, n=2)
							self.rotate_side(side_idx=5, n=2)
							self.rotate_side(side_idx=side_idx, n=2)

						new_cube = self.rubcube.sides_map[side_idx, 1, 2]
						if new_cube.color == side_color and new_cube.adjace_colors[0] == next_side_color:
							handled_cubes += 1

				if not changed:
					break

			handled_cubes = 0
			for side in range(1, 4+1):
				side_color = self.rubcube.sides_map[side, 1, 1].color
				cube = self.rubcube.sides_map[side, 1, 2]
				next_side_color = self.rubcube.sides_map[side % 4 + 1, 1, 1].color
				if cube.color == side_color and next_side_color in cube.adjace_colors:
					handled_cubes += 1

	def solve_2_layer_crosspiece(self):
		top_color = self.rubcube.sides_map[5, 1, 1].color

		# Collect top crosspiece
		cross_indices = self.get_cross_indices()
		for i in range(len(cross_indices)):
			side = (abs(i - 3) - 2) % 4 + 1
			cube = self.rubcube.sides_map[5, cross_indices[i][0], cross_indices[i][1]]

			pre_row, pre_col = cross_indices[(i - 1) % 4]
			previous_cube = self.rubcube.sides_map[5, pre_row, pre_col]

			next_row, next_col = cross_indices[(i + 1) % 4]
			next_cube = self.rubcube.sides_map[5, next_row, next_col]

			counter_row, counter_col = cross_indices[(i + 2) % 4]
			counter_cube = self.rubcube.sides_map[5, counter_row, counter_col]

			if previous_cube.color == cube.color == next_cube.color:
				break

			if previous_cube.color == cube.color:
				self.rotate_side(side_idx=((side - 2) % 4 + 1), n=1, byclockwise=True)
				self.pif_paf(main_side_idx=0, adj_side_idx=((side - 3) % 4 + 1))
				self.pif_paf(main_side_idx=0, adj_side_idx=((side - 3) % 4 + 1))
				self.rotate_side(side_idx=((side - 2) % 4 + 1), n=1, byclockwise=False)
				break

			elif cube.color == counter_cube.color:
				self.rotate_side(side_idx=((side - 2) % 4 + 1), n=1, byclockwise=True)
				self.pif_paf(main_side_idx=0, adj_side_idx=((side - 3) % 4 + 1))
				self.rotate_side(side_idx=((side - 2) % 4 + 1), n=1, byclockwise=False)
				break

		else:
			self.rotate_side(side_idx=side, n=1, byclockwise=True)
			self.pif_paf(main_side_idx=0, adj_side_idx=((side - 2) % 4 + 1))
			self.rotate_side(side_idx=side, n=1, byclockwise=False)
			self.rotate_side(side_idx=((side - 3) % 4 + 1), n=1, byclockwise=True)
			self.pif_paf(main_side_idx=0, adj_side_idx=((side - 4) % 4 + 1))
			self.pif_paf(main_side_idx=0, adj_side_idx=((side - 4) % 4 + 1))
			self.rotate_side(side_idx=((side - 3) % 4 + 1), n=1, byclockwise=False)

		# Move crosspiece cubes to needed positions
		# Is all crosspiece cubes in their positions
		crosspiece_colors = list(map(
			lambda cube: cube.adjace_colors[0], self.get_cross_cubes(side_idx=5)
		))
		pivot_color = crosspiece_colors[0]

		target_cross_colors = adjacent_sides_colors[top_color]
		pivot_in_target = target_cross_colors.index(pivot_color)
		target_cross_colors = target_cross_colors[pivot_in_target:] + \
							  target_cross_colors[:pivot_in_target]

		if crosspiece_colors == target_cross_colors:
			curr_side = 2
			target_side = self.color_to_code[pivot_color]
			rot_n = (target_side - curr_side) % 4

			self.rotate_side(side_idx=5, n=rot_n, byclockwise=True)
			return

		# Is crosspiece colors opposite for each other
		if crosspiece_colors[2] == target_cross_colors[2]:
			curr_side = 2
			target_side = self.color_to_code[pivot_color]
			rot_n = (target_side - curr_side) % 4

			self.rotate_side(side_idx=5, n=rot_n, byclockwise=True)

			acting_side = target_side % 4 + 1

			self.rotate_side(side_idx=acting_side, n=1, byclockwise=True)
			self.rotate_side(side_idx=5, n=1, byclockwise=True)
			self.rotate_side(side_idx=acting_side, n=1, byclockwise=False)
			self.rotate_side(side_idx=5, n=1, byclockwise=True)
			self.rotate_side(side_idx=acting_side, n=1, byclockwise=True)
			self.rotate_side(side_idx=5, n=1, byclockwise=True)
			self.rotate_side(side_idx=5, n=1, byclockwise=True)
			self.rotate_side(side_idx=acting_side, n=1, byclockwise=False)

			self.rotate_side(side_idx=5, n=1, byclockwise=True)

			acting_side = (target_side - 2) % 4 + 1
			self.rotate_side(side_idx=acting_side, n=1, byclockwise=True)
			self.rotate_side(side_idx=5, n=1, byclockwise=True)
			self.rotate_side(side_idx=acting_side, n=1, byclockwise=False)
			self.rotate_side(side_idx=5, n=1, byclockwise=True)
			self.rotate_side(side_idx=acting_side, n=1, byclockwise=True)
			self.rotate_side(side_idx=5, n=1, byclockwise=True)
			self.rotate_side(side_idx=5, n=1, byclockwise=True)
			self.rotate_side(side_idx=acting_side, n=1, byclockwise=False)
			return

		for i, color in enumerate(crosspiece_colors):
			color_in_target_idx = target_cross_colors.index(color)
			if crosspiece_colors[(i + 1) % 4] == target_cross_colors[(color_in_target_idx + 1) % 4]:
				curr_side = (abs(i - 3) - 2) % 4 + 1
				acting_side = curr_side

				self.rotate_side(side_idx=acting_side, n=1, byclockwise=True)
				self.rotate_side(side_idx=5, n=1, byclockwise=True)
				self.rotate_side(side_idx=acting_side, n=1, byclockwise=False)
				self.rotate_side(side_idx=5, n=1, byclockwise=True)
				self.rotate_side(side_idx=acting_side, n=1, byclockwise=True)
				self.rotate_side(side_idx=5, n=1, byclockwise=True)
				self.rotate_side(side_idx=5, n=1, byclockwise=True)
				self.rotate_side(side_idx=acting_side, n=1, byclockwise=False)

				target_side = self.color_to_code[self.rubcube.sides_map[curr_side, 2, 1].color]
				rot_n = (target_side - curr_side) % 4

				self.rotate_side(side_idx=5, n=rot_n, byclockwise=True)
				return

	def solve_2_layer_corners(self):
		# Get color of side which opposite of main side
		top_color = self.rubcube.sides_map[5, 1, 1].color

		# Get target colors of lateral sides
		target_lateral_sides_colors = [set([top_color]) for _ in range(4)]
		for i in range(4):
			side_idx = (i + 2) if i % 2 == 0 else i

			curr_color = self.rubcube.sides_map[side_idx, 1, 1].color
			next_color = self.rubcube.sides_map[(side_idx - 2) % 4 + 1, 1, 1].color

			target_lateral_sides_colors[i].add(curr_color)
			target_lateral_sides_colors[i].add(next_color)

		corner_cubes_coords = self.get_corner_indices()

		pivot_cube_idx = None
		while pivot_cube_idx is None:
			for i in range(4):
				row, col = corner_cubes_coords[i]
				cube = self.rubcube.sides_map[5, row, col]

				cube_colors = set(cube.color).union(cube.adjace_colors)
				target_colors = target_lateral_sides_colors[i]

				if cube_colors == target_colors:
					pivot_cube_idx = i

			if pivot_cube_idx is None:
				self.move_corner_cubes(side_idx=5, pivot_cube_idx=1)

		corner_cubes = tuple(
			map(lambda cube: set(cube.color).union(cube.adjace_colors),
				self.get_corner_cubes(side_idx=5)
			)
		)

		# opposite the pivot cube
		oppos_cube = corner_cubes[(pivot_cube_idx + 2) % 4]
		if oppos_cube == target_lateral_sides_colors[(pivot_cube_idx + 1) % 4]:
			self.move_corner_cubes(side_idx=5, pivot_cube_idx=pivot_cube_idx, byclockwise=True)
		elif oppos_cube == target_lateral_sides_colors[(pivot_cube_idx + 3) % 4]:
			self.move_corner_cubes(side_idx=5, pivot_cube_idx=pivot_cube_idx, byclockwise=False)

		for i in range(4):
			cube = self.rubcube.sides_map[5, 2, 2]
			if cube.color != top_color:
				back_cube = self.rubcube.sides_map[1, 2, 2]

				if back_cube.color == top_color:
					self.rotate_corner_cube(side_idx=5, cube_idx=0, byclockwise=False)
				else:
					self.rotate_corner_cube(side_idx=5, cube_idx=0, byclockwise=True)

			self.rotate_side(side_idx=5, n=1, byclockwise=True)

	def pif_paf(self, main_side_idx:int, adj_side_idx:int):
		side_1 = adj_side_idx
		side_2 = counter_side[main_side_idx]

		self.rotate_side(side_idx=side_1, n=1, byclockwise=True)
		self.rotate_side(side_idx=side_2, n=1, byclockwise=True)
		self.rotate_side(side_idx=side_1, n=1, byclockwise=False)
		self.rotate_side(side_idx=side_2, n=1, byclockwise=False)

	def back_pif_paf(self, main_side_idx:int, adj_side_idx:int):
		side_1 = adj_side_idx
		side_2 = counter_side[main_side_idx]

		self.rotate_side(side_idx=side_2, n=1, byclockwise=True)
		self.rotate_side(side_idx=side_1, n=1, byclockwise=True)
		self.rotate_side(side_idx=side_2, n=1, byclockwise=False)
		self.rotate_side(side_idx=side_1, n=1, byclockwise=False)

	def rotate_corner_cube(self, side_idx:int, cube_idx:int, byclockwise:bool=True):
		lateral_sides = adjacent_sides_codes[side_idx]

		left_side = lateral_sides[cube_idx]
		back_side = lateral_sides[(cube_idx + 1) % 4]

		if byclockwise:
			for _ in range(2):
				self.rotate_side(side_idx=back_side, n=1, byclockwise=True)
				self.rotate_side(side_idx=left_side, n=1, byclockwise=False)
				self.rotate_side(side_idx=back_side, n=1, byclockwise=False)
				self.rotate_side(side_idx=left_side, n=1, byclockwise=True)
		else:
			for _ in range(2):
				self.rotate_side(side_idx=left_side, n=1, byclockwise=False)
				self.rotate_side(side_idx=back_side, n=1, byclockwise=True)
				self.rotate_side(side_idx=left_side, n=1, byclockwise=True)
				self.rotate_side(side_idx=back_side, n=1, byclockwise=False)


	def move_corner_cubes(
						self,
						side_idx: int,
						pivot_cube_idx: int,
						n: int=1,
						byclockwise: bool=False):
		n %= 4
		if n > 2:
			n = 1
			byclockwise = not byclockwise

		lateral_sides = adjacent_sides_codes[side_idx]
		lateral_sides = lateral_sides[pivot_cube_idx:] + lateral_sides[:pivot_cube_idx]

		top_side = side_idx
		front_side = lateral_sides[0]
		right_side = lateral_sides[1]
		left_side = lateral_sides[-1]

		if byclockwise:
			self.rotate_side(side_idx=left_side, n=1, byclockwise=False)
			self.rotate_side(side_idx=top_side, n=1, byclockwise=True)
			self.rotate_side(side_idx=right_side, n=1, byclockwise=True)
			self.rotate_side(side_idx=top_side, n=1, byclockwise=False)
			self.rotate_side(side_idx=left_side, n=1, byclockwise=True)
			self.rotate_side(side_idx=top_side, n=1, byclockwise=True)
			self.rotate_side(side_idx=right_side, n=1, byclockwise=False)
			self.rotate_side(side_idx=top_side, n=1, byclockwise=False)

		else:
			self.rotate_side(side_idx=top_side, n=1, byclockwise=True)
			self.rotate_side(side_idx=right_side, n=1, byclockwise=True)
			self.rotate_side(side_idx=top_side, n=1, byclockwise=False)
			self.rotate_side(side_idx=left_side, n=1, byclockwise=False)
			self.rotate_side(side_idx=top_side, n=1, byclockwise=True)
			self.rotate_side(side_idx=right_side, n=1, byclockwise=False)
			self.rotate_side(side_idx=top_side, n=1, byclockwise=False)
			self.rotate_side(side_idx=left_side, n=1, byclockwise=True)

	def set_middle_corner(self, side_1_idx:int, side_2_idx:int, corner_side:int):
		if (side_1_idx - 2) % 4 + 1 == side_2_idx:
			side_1_idx, side_2_idx = side_2_idx, side_1_idx

		if corner_side == side_1_idx:
			self.rotate_side(side_idx=5, n=1, byclockwise=False)
			self.rotate_side(side_idx=side_2_idx, n=1, byclockwise=False)
			self.rotate_side(side_idx=5, n=1, byclockwise=True)
			self.rotate_side(side_idx=side_2_idx, n=1, byclockwise=True)
			self.back_pif_paf(main_side_idx=0, adj_side_idx=side_1_idx)

		elif corner_side == side_2_idx:
			self.back_pif_paf(main_side_idx=0, adj_side_idx=side_1_idx)
			self.rotate_side(side_idx=5, n=1, byclockwise=False)
			self.rotate_side(side_idx=side_2_idx, n=1, byclockwise=False)
			self.rotate_side(side_idx=5, n=1, byclockwise=True)
			self.rotate_side(side_idx=side_2_idx, n=1, byclockwise=True)

	def get_cross_cubes(self, side_idx:int) -> list:
		"""Returns array of cross cubes counter clockwise. Order example:
			#2#
			3#1
			#0#
		"""
		side = self.rubcube.sides_map[side_idx]
		cubes = []
		for pair in self.get_cross_indices():
			cubes.append(side[pair[0], pair[1]])

		return cubes

	def get_corner_cubes(self, side_idx:int) -> list:
		"""Returns array of corner cubes counterclockwise. Order example:
			2#1
			###
			3#0
		"""
		side = self.rubcube.sides_map[side_idx]
		cubes = []
		for pair in self.get_corner_indices():
			cubes.append(side[pair[0], pair[1]])

		return cubes

	def get_cross_indices(self) -> list:
		"""Returns array of cross cubes indices counter clockwise. Order example:
			#2#
			3#1
			#0#
		"""
		return [(2, 1), (1, 2), (0, 1), (1, 0)]

	def get_corner_indices(self) -> list:
		"""Returns array of corner cubes indices counter clockwise. Order example:
			2#1
			###
			3#0
		"""
		return [(2, 2), (0, 2), (0, 0), (2, 0)]

	def get_main_side(self):
		best_side = {"side_idx": None, "cross_weight": 0}

		for side_idx in range(6):
			side_color = self.rubcube.sides_map[side_idx, 1, 1].color

			cross_weight = int()
			next_colors = list()

			for i, (cross_row, cross_col) in enumerate(self.get_cross_indices()):
				cube = self.rubcube.sides_map[side_idx, cross_row, cross_col]
				if cube.color == side_color:
					if not next_colors:
						adj_colors = adjacent_sides_colors[side_color]
						start_color_idx = adj_colors.index(cube.adjace_colors[0])
						next_colors = [None] * (i) + \
									  adj_colors[start_color_idx:] + \
									  adj_colors[:start_color_idx]

					if next_colors[i] in cube.adjace_colors:
						cross_weight += 1

			if best_side['cross_weight'] < cross_weight:
				best_side['side_idx'] = side_idx
				best_side['cross_weight'] = cross_weight

		return best_side['side_idx']

	def optim_solving_steps(self):
		step_idx = 0
		while step_idx < len(self.solving_steps):
			step = self.solving_steps[step_idx]

			if len(self.solving_steps) == step_idx + 1:
				next_step = None
			else:
				next_step = self.solving_steps[step_idx + 1]

			if step[1] == "0":
				self.solving_steps = self.solving_steps[:step_idx] + self.solving_steps[step_idx + 1:]
				step_idx -= 1 if step_idx > 0 else 0

			elif step[1] == "3":
				self.solving_steps = self.solving_steps[:step_idx] + \
									 [f"{step[0]}1{int(not int(step[2]))}"] + \
									 self.solving_steps[step_idx + 1:]

				step_idx -= 1 if step_idx > 0 else 0

			elif next_step and step[0] == next_step[0]:
				n1 = int(step[1]) * (-1 if step[2] == "1" else 1)
				n2 = int(next_step[1]) * (-1 if next_step[2] == "1" else 1)
				n = n1 + n2

				if n == 0:
					self.solving_steps = self.solving_steps[:step_idx] + self.solving_steps[step_idx + 2:]

				else:
					byclockwise = "0" if n > 0 else "1"
					n = abs(n)

					self.solving_steps = self.solving_steps[:step_idx] + \
										 [f"{step[0]}{n}{byclockwise}"] + \
										 self.solving_steps[step_idx + 2:]

				step_idx -= 1 if step_idx > 0 else 0

			else:
				step_idx += 1
