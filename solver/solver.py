import copy
import numpy as np

from datatypes import RubiksCube
from shortcuts import (adjacent_sides_colors, sides_codes,
					   counter_side, adjacent_sides_codes)


class Solver:
	def __init__(self, rubcube:RubiksCube):
		self.rubcube = copy.deepcopy(rubcube)
		self.solving_steps = list()
		self.color_to_code = dict()

	def color_to_code_init(self):
		for code in range(6):
			color = self.rubcube.sides_map[code, 1, 1].color
			self.color_to_code[color] = code
			self.color_to_code[code] = color

	def rotate_side(self, side_code:int, n:int, byclockwise:bool=True):
		n %= 4
		if n > 2:
			n = 1
			byclockwise = not byclockwise

		self.solving_steps.append(f"{side_code}{n}{int(byclockwise)}")
		self.rubcube.rotate_side(side_idx=side_code, n=n, byclockwise=byclockwise)

	def solve(self):
		self.color_to_code_init()
		self.main_color = self.rubcube.sides_map[0][1, 1].color

		self.collect_0_layer_crosspiece()
		self.collect_0_layer_corners()
		self.collect_1_layer_corners()
		self.collect_2_layer_crosspiece()
		self.collect_2_layer_corners()

		self.optim_solving_steps()
		return self.solving_steps

	def collect_0_layer_crosspiece(self):
		main_cross_cubes = self.get_cross_cubes(side_code=0)
		handled_cubes = 0

		first_idx = -1
		for idx in range(len(main_cross_cubes)):
			cube = main_cross_cubes[idx]
			if cube.color == self.main_color:
				handled_cubes += 1

				if first_idx == -1:
					first_idx = self.color_to_code[cube.adjace_colors[0]] - 1
					rot_n = (first_idx - idx) % 4

					if rot_n > 0:
						self.rotate_side(side_code=0, n=rot_n, byclockwise=False)

				else:
					_idx = (idx + first_idx) % 4
					target_idx = self.color_to_code[cube.adjace_colors[0]] - 1
					rot_n = (target_idx - _idx) % 4

					if rot_n > 0:
						self.rotate_side(side_code=_idx+1, n=1, byclockwise=False)
						self.rotate_side(side_code=0, n=rot_n, byclockwise=True)
						self.rotate_side(side_code=_idx+1, n=1, byclockwise=True)
						self.rotate_side(side_code=0, n=rot_n, byclockwise=False)

		while handled_cubes < 4:
			# Handle from 1 to 4 side
			for side in range(1, 5):
				for i, (cross_row, cross_col) in enumerate(self.get_cross_indices(side_code=side)):
					cube = self.rubcube.sides_map[side, cross_row, cross_col]
					if cube.color == self.main_color:
						handled_cubes += 1

						if i == 0:
							adj_side = (side - 1 + 1) % 4 + 1
							target_idx = self.color_to_code[cube.adjace_colors[0]]
							rot_n = (target_idx - adj_side) % 4

							self.rotate_side(side_code=0, n=rot_n, byclockwise=True)
							self.rotate_side(side_code=side, n=1, byclockwise=False)
							self.rotate_side(side_code=adj_side, n=1, byclockwise=True)
							self.rotate_side(side_code=side, n=1, byclockwise=True)
							self.rotate_side(side_code=0, n=rot_n, byclockwise=False)

						elif i == 1:
							adj_side = (side - 1 + 1) % 4 + 1
							target_idx = self.color_to_code[cube.adjace_colors[0]]
							rot_n = (target_idx - adj_side) % 4

							self.rotate_side(side_code=0, n=rot_n, byclockwise=True)
							self.rotate_side(side_code=adj_side, n=1, byclockwise=True)
							self.rotate_side(side_code=0, n=rot_n, byclockwise=False)

						elif i == 2:
							adj_side = (side - 1 + 1) % 4 + 1
							target_idx = self.color_to_code[cube.adjace_colors[0]]
							rot_n = (target_idx - adj_side) % 4

							self.rotate_side(side_code=side, n=1, byclockwise=True)
							self.rotate_side(side_code=0, n=rot_n, byclockwise=True)
							self.rotate_side(side_code=adj_side, n=1, byclockwise=True)
							self.rotate_side(side_code=0, n=rot_n, byclockwise=False)

						elif i == 3:
							adj_side = (side - 1 - 1) % 4 + 1
							target_idx = self.color_to_code[cube.adjace_colors[0]]
							rot_n = (target_idx - adj_side) % 4
							self.rotate_side(side_code=0, n=rot_n, byclockwise=True)
							self.rotate_side(side_code=adj_side, n=1, byclockwise=False)
							self.rotate_side(side_code=0, n=rot_n, byclockwise=False)

			# Handle 5 side
			for i, (cross_row, cross_col) in enumerate(self.get_cross_indices(side_code=5)):
				cube = self.rubcube.sides_map[5, cross_row, cross_col]
				if cube.color == self.main_color:
					handled_cubes += 1

					adj_side = (i + 2 * (not i % 2)) % 5
					target_idx = self.color_to_code[cube.adjace_colors[0]]
					rot_n = (target_idx - adj_side) % 4

					self.rotate_side(side_code=0, n=rot_n, byclockwise=True)
					self.rotate_side(side_code=adj_side, n=2, byclockwise=True)
					self.rotate_side(side_code=0, n=rot_n, byclockwise=False)

	def collect_0_layer_corners(self):
		handled_cubes = 0

		while handled_cubes < 4:
			# Handle 0 side
			for i, (cor_row, cor_col) in enumerate(self.get_corner_indices(side_code=0)):
				cube = self.rubcube.sides_map[0, cor_row, cor_col]
				if cube.color == self.main_color:
					handled_cubes += 1

					adj_side = i + 1
					target_idx = self.color_to_code[self.rubcube.sides_map[adj_side, 0, 2].color]
					rot_n = (target_idx - adj_side) % 4

					self.pif_paf(main_side_idx=0, adj_side_idx=adj_side)
					self.rotate_side(side_code=5, n=rot_n, byclockwise=True)
					self.back_pif_paf(main_side_idx=0, adj_side_idx=target_idx)

			# Handle 1-4 sides
			for side in range(1, 5):
				for i, (cor_row, cor_col) in enumerate(self.get_corner_indices(side_code=side)):
					cube = self.rubcube.sides_map[side, cor_row, cor_col]
					if cube.color == self.main_color:
						handled_cubes += 1

						if i == 0:
							adj_side = side % 5 + 1
							target_idx = self.color_to_code[self.rubcube.sides_map[adj_side, 2, 0].color]
							rot_n = (target_idx - adj_side) % 4

							self.rotate_side(side_code=5, n=rot_n, byclockwise=True)
							self.pif_paf(main_side_idx=0, adj_side_idx=(target_idx - 2) % 4 + 1)

						elif i == 1:
							adj_side = side % 5 + 1
							self.pif_paf(main_side_idx=0, adj_side_idx=side)

							target_idx = self.color_to_code[self.rubcube.sides_map[adj_side, 2, 0].color]
							rot_n = (target_idx - adj_side) % 4

							self.rotate_side(side_code=5, n=rot_n, byclockwise=True)
							self.pif_paf(main_side_idx=0, adj_side_idx=(target_idx - 2) % 4 + 1)

						elif i == 2:
							adj_side = (side - 2) % 4 + 1
							self.back_pif_paf(main_side_idx=0, adj_side_idx=adj_side)

							target_idx = self.color_to_code[self.rubcube.sides_map[adj_side, 2, 2].color]
							rot_n = (target_idx - adj_side) % 4

							self.rotate_side(side_code=5, n=rot_n, byclockwise=True)
							self.back_pif_paf(main_side_idx=0, adj_side_idx=target_idx)

						elif i == 3:
							adj_side = (side - 2) % 4 + 1
							target_idx = self.color_to_code[self.rubcube.sides_map[adj_side, 2, 2].color]
							rot_n = (target_idx - adj_side) % 4

							self.rotate_side(side_code=5, n=rot_n, byclockwise=True)
							self.back_pif_paf(main_side_idx=0, adj_side_idx=target_idx)

			# Handle 5 side
			for i, (cor_row, cor_col) in enumerate(self.get_corner_indices(side_code=5)):
				cube = self.rubcube.sides_map[5, cor_row, cor_col]
				if cube.color == self.main_color:
					handled_cubes += 1

					adj_side = (abs(3 - i) + 1) % 4 + 1
					target_idx = self.color_to_code[self.rubcube.sides_map[adj_side, 2, 2].color]
					rot_n = (target_idx - (adj_side % 4 + 1)) % 4

					self.rotate_side(side_code=5, n=rot_n, byclockwise=True)
					for _ in range(3):
						self.pif_paf(main_side_idx=0, adj_side_idx=(target_idx - 2) % 4 + 1)

	def collect_1_layer_corners(self):
		handled_cubes = 0
		top_color = self.rubcube.sides_map[5, 1, 1].color

		# Handle every cross cube at top layer
		while handled_cubes < 4:
			handled_cubes_before = handled_cubes
			for i, (row, col) in enumerate(self.get_cross_indices(side_code=5)):
				cube = self.rubcube.sides_map[5, row, col]
				if cube.color != top_color and cube.adjace_colors[0] != top_color:
					handled_cubes += 1

					curr_side_idx = (abs(i - 3) - 2) % 4 + 1
					target_idx_1 = self.color_to_code[cube.color]
					target_idx_2 = self.color_to_code[cube.adjace_colors[0]]
					rot_n = (target_idx_2 - curr_side_idx) % 4

					self.rotate_side(side_code=5, n=rot_n, byclockwise=True)
					self.set_middle_corner(
						side_1_idx=target_idx_1,
						side_2_idx=target_idx_2,
						corner_side=target_idx_2,
					)

			if handled_cubes_before == handled_cubes:
				break

		# Handle every corner cube at middle layer
		if handled_cubes < 4:
			for side_idx in adjacent_sides_codes[0]:
				side_color = self.rubcube.sides_map[side_idx, 1, 1].color

				next_side_idx = side_idx % 4 + 1
				next_side_color = self.rubcube.sides_map[next_side_idx, 1, 1].color

				cube = self.rubcube.sides_map[side_idx, 1, 2]

				if cube.color == next_side_color and cube.adjace_colors[0] == side_color:
					handled_cubes += 1

					self.set_middle_corner(
						side_1_idx=side_idx,
						side_2_idx=next_side_idx,
						corner_side=next_side_idx
					)
					self.rotate_side(side_code=5, n=2, byclockwise=True)
					self.set_middle_corner(
						side_1_idx=side_idx,
						side_2_idx=next_side_idx,
						corner_side=next_side_idx
					)

	def collect_2_layer_crosspiece(self):
		top_color = self.rubcube.sides_map[5, 1, 1].color

		# Collect top crosspiece
		cross_indices = self.get_cross_indices(side_code=5)
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
				self.rotate_side(side_code=((side - 2) % 4 + 1), n=1, byclockwise=True)
				self.pif_paf(main_side_idx=0, adj_side_idx=((side - 3) % 4 + 1))
				self.pif_paf(main_side_idx=0, adj_side_idx=((side - 3) % 4 + 1))
				self.rotate_side(side_code=((side - 2) % 4 + 1), n=1, byclockwise=False)
				break

			elif cube.color == counter_cube.color:
				self.rotate_side(side_code=((side - 2) % 4 + 1), n=1, byclockwise=True)
				self.pif_paf(main_side_idx=0, adj_side_idx=((side - 3) % 4 + 1))
				self.rotate_side(side_code=((side - 2) % 4 + 1), n=1, byclockwise=False)
				break

		else:
			self.rotate_side(side_code=side, n=1, byclockwise=True)
			self.pif_paf(main_side_idx=0, adj_side_idx=((side - 2) % 4 + 1))
			self.rotate_side(side_code=side, n=1, byclockwise=False)
			self.rotate_side(side_code=((side - 3) % 4 + 1), n=1, byclockwise=True)
			self.pif_paf(main_side_idx=0, adj_side_idx=((side - 4) % 4 + 1))
			self.pif_paf(main_side_idx=0, adj_side_idx=((side - 4) % 4 + 1))
			self.rotate_side(side_code=((side - 3) % 4 + 1), n=1, byclockwise=False)

		# return
		# Move crosspiece cubes to needed positions
		# Is all crosspiece cubes in their positions
		crosspiece_colors = list(map(
			lambda cube: cube.adjace_colors[0], self.get_cross_cubes(side_code=5)
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

			self.rotate_side(side_code=5, n=rot_n, byclockwise=True)
			return

		# Is crosspiece colors opposite for each other
		if crosspiece_colors[2] == target_cross_colors[2]:
			curr_side = 2
			target_side = self.color_to_code[pivot_color]
			rot_n = (target_side - curr_side) % 4

			self.rotate_side(side_code=5, n=rot_n, byclockwise=True)

			acting_side = target_side % 4 + 1

			self.rotate_side(side_code=acting_side, n=1, byclockwise=True)
			self.rotate_side(side_code=5, n=1, byclockwise=True)
			self.rotate_side(side_code=acting_side, n=1, byclockwise=False)
			self.rotate_side(side_code=5, n=1, byclockwise=True)
			self.rotate_side(side_code=acting_side, n=1, byclockwise=True)
			self.rotate_side(side_code=5, n=1, byclockwise=True)
			self.rotate_side(side_code=5, n=1, byclockwise=True)
			self.rotate_side(side_code=acting_side, n=1, byclockwise=False)

			self.rotate_side(side_code=5, n=1, byclockwise=True)

			acting_side = (target_side - 2) % 4 + 1
			self.rotate_side(side_code=acting_side, n=1, byclockwise=True)
			self.rotate_side(side_code=5, n=1, byclockwise=True)
			self.rotate_side(side_code=acting_side, n=1, byclockwise=False)
			self.rotate_side(side_code=5, n=1, byclockwise=True)
			self.rotate_side(side_code=acting_side, n=1, byclockwise=True)
			self.rotate_side(side_code=5, n=1, byclockwise=True)
			self.rotate_side(side_code=5, n=1, byclockwise=True)
			self.rotate_side(side_code=acting_side, n=1, byclockwise=False)
			return

		# Other combinations
		for i, color in enumerate(crosspiece_colors):
			color_in_target_idx = target_cross_colors.index(color)
			if crosspiece_colors[(i + 1) % 4] == target_cross_colors[(color_in_target_idx + 1) % 4]:
				curr_side = (abs(i - 3) - 2) % 4 + 1
				acting_side = curr_side

				self.rotate_side(side_code=acting_side, n=1, byclockwise=True)
				self.rotate_side(side_code=5, n=1, byclockwise=True)
				self.rotate_side(side_code=acting_side, n=1, byclockwise=False)
				self.rotate_side(side_code=5, n=1, byclockwise=True)
				self.rotate_side(side_code=acting_side, n=1, byclockwise=True)
				self.rotate_side(side_code=5, n=1, byclockwise=True)
				self.rotate_side(side_code=5, n=1, byclockwise=True)
				self.rotate_side(side_code=acting_side, n=1, byclockwise=False)

				target_side = self.color_to_code[self.rubcube.sides_map[curr_side, 2, 1].color]
				rot_n = (target_side - curr_side) % 4

				self.rotate_side(side_code=5, n=rot_n, byclockwise=True)
				return

	def collect_2_layer_corners(self):
		# Get color of side which opposite of main side
		top_color = self.rubcube.sides_map[5, 1, 1].color
		
		# Get target colors of lateral sides
		target_lateral_sides_colors = [set([top_color]) for _ in range(4)]
		for i in range(4):
			side_code = (i + 2) if i % 2 == 0 else i

			curr_color = self.rubcube.sides_map[side_code, 1, 1].color
			next_color = self.rubcube.sides_map[(side_code - 2) % 4 + 1, 1, 1].color

			target_lateral_sides_colors[i].add(curr_color)
			target_lateral_sides_colors[i].add(next_color)

		corner_cubes_coords = self.get_corner_indices(side_code=5)

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
				self.move_corner_cubes(side_code=5, pivot_cube_idx=1)

		corner_cubes = tuple(
			map(lambda cube: set(cube.color).union(cube.adjace_colors),
				self.get_corner_cubes(side_code=5)
			)
		)

		# opposite the pivot cube
		oppos_cube = corner_cubes[(pivot_cube_idx + 2) % 4]
		if oppos_cube == target_lateral_sides_colors[(pivot_cube_idx + 1) % 4]:
			self.move_corner_cubes(side_code=5, pivot_cube_idx=pivot_cube_idx, byclockwise=True)
		elif oppos_cube == target_lateral_sides_colors[(pivot_cube_idx + 3) % 4]:
			self.move_corner_cubes(side_code=5, pivot_cube_idx=pivot_cube_idx, byclockwise=False)

		for i in range(4):
			cube = self.rubcube.sides_map[5, 2, 2]
			if cube.color != top_color:
				back_cube = self.rubcube.sides_map[1, 2, 2]

				if back_cube.color == top_color:
					self.rotate_corner_cube(side_code=5, cube_idx=0, byclockwise=False)
				else:
					self.rotate_corner_cube(side_code=5, cube_idx=0, byclockwise=True)

			self.rotate_side(side_code=5, n=1, byclockwise=True)

	def pif_paf(self, main_side_idx:int, adj_side_idx:int):
		side_1 = adj_side_idx
		side_2 = counter_side[main_side_idx]

		self.rotate_side(side_code=side_1, n=1, byclockwise=True)
		self.rotate_side(side_code=side_2, n=1, byclockwise=True)
		self.rotate_side(side_code=side_1, n=1, byclockwise=False)
		self.rotate_side(side_code=side_2, n=1, byclockwise=False)

	def back_pif_paf(self, main_side_idx:int, adj_side_idx:int):
		side_1 = adj_side_idx
		side_2 = counter_side[main_side_idx]

		self.rotate_side(side_code=side_2, n=1, byclockwise=True)
		self.rotate_side(side_code=side_1, n=1, byclockwise=True)
		self.rotate_side(side_code=side_2, n=1, byclockwise=False)
		self.rotate_side(side_code=side_1, n=1, byclockwise=False)

	def rotate_corner_cube(self, side_code:int, cube_idx:int, byclockwise:bool=True):
		lateral_sides = adjacent_sides_codes[side_code]

		left_side = lateral_sides[cube_idx]
		back_side = lateral_sides[(cube_idx + 1) % 4]

		if byclockwise:
			for _ in range(2):
				self.rotate_side(side_code=back_side, n=1, byclockwise=True)
				self.rotate_side(side_code=left_side, n=1, byclockwise=False)
				self.rotate_side(side_code=back_side, n=1, byclockwise=False)
				self.rotate_side(side_code=left_side, n=1, byclockwise=True)
		else:
			for _ in range(2):
				self.rotate_side(side_code=left_side, n=1, byclockwise=False)
				self.rotate_side(side_code=back_side, n=1, byclockwise=True)
				self.rotate_side(side_code=left_side, n=1, byclockwise=True)
				self.rotate_side(side_code=back_side, n=1, byclockwise=False)


	def move_corner_cubes(self, side_code:int, pivot_cube_idx:int, n:int=1, byclockwise:bool=False):
		n %= 4
		if n > 2:
			n = 1
			byclockwise = not byclockwise
		
		lateral_sides = adjacent_sides_codes[side_code]
		lateral_sides = lateral_sides[pivot_cube_idx:] + lateral_sides[:pivot_cube_idx]

		top_side = side_code
		front_side = lateral_sides[0]
		right_side = lateral_sides[1]
		left_side = lateral_sides[-1]

		if byclockwise:
			self.rotate_side(side_code=left_side, n=1, byclockwise=False)
			self.rotate_side(side_code=top_side, n=1, byclockwise=True)
			self.rotate_side(side_code=right_side, n=1, byclockwise=True)
			self.rotate_side(side_code=top_side, n=1, byclockwise=False)
			self.rotate_side(side_code=left_side, n=1, byclockwise=True)
			self.rotate_side(side_code=top_side, n=1, byclockwise=True)
			self.rotate_side(side_code=right_side, n=1, byclockwise=False)
			self.rotate_side(side_code=top_side, n=1, byclockwise=False)

		else:
			self.rotate_side(side_code=top_side, n=1, byclockwise=True)
			self.rotate_side(side_code=right_side, n=1, byclockwise=True)
			self.rotate_side(side_code=top_side, n=1, byclockwise=False)
			self.rotate_side(side_code=left_side, n=1, byclockwise=False)
			self.rotate_side(side_code=top_side, n=1, byclockwise=True)
			self.rotate_side(side_code=right_side, n=1, byclockwise=False)
			self.rotate_side(side_code=top_side, n=1, byclockwise=False)
			self.rotate_side(side_code=left_side, n=1, byclockwise=True)

	def set_middle_corner(self, side_1_idx:int, side_2_idx:int, corner_side:int):
		if (side_1_idx - 2) % 4 + 1 == side_2_idx:
			side_1_idx, side_2_idx = side_2_idx, side_1_idx

		if corner_side == side_1_idx:
			self.rotate_side(side_code=5, n=1, byclockwise=False)
			self.rotate_side(side_code=side_2_idx, n=1, byclockwise=False)
			self.rotate_side(side_code=5, n=1, byclockwise=True)
			self.rotate_side(side_code=side_2_idx, n=1, byclockwise=True)
			self.back_pif_paf(main_side_idx=0, adj_side_idx=side_1_idx)

		elif corner_side == side_2_idx:
			self.back_pif_paf(main_side_idx=0, adj_side_idx=side_1_idx)
			self.rotate_side(side_code=5, n=1, byclockwise=False)
			self.rotate_side(side_code=side_2_idx, n=1, byclockwise=False)
			self.rotate_side(side_code=5, n=1, byclockwise=True)
			self.rotate_side(side_code=side_2_idx, n=1, byclockwise=True)

	def get_cross_cubes(self, side_code:int):
		side = self.rubcube.sides_map[side_code]
		return [side[2, 1], side[1, 2], side[0, 1], side[1, 0]]

	def get_corner_cubes(self, side_code:int):
		side = self.rubcube.sides_map[side_code]
		return [side[2, 2], side[0, 2], side[0, 0], side[2, 0]]

	def get_cross_indices(self, side_code:int):
		side = self.rubcube.sides_map[side_code]
		return [(2, 1), (1, 2), (0, 1), (1, 0)]

	def get_corner_indices(self, side_code:int):
		side = self.rubcube.sides_map[side_code]
		return [(2, 2), (0, 2), (0, 0), (2, 0)]

	def get_main_side(self):
		best_side = {"side_code": None, "cross_weight": 0}

		for side_code in range(6):
			side_color = self.rubcube.sides_map[side_code, 1, 1].color

			cross_weight = int()
			next_colors = list()

			for i, (cross_row, cross_col) in enumerate(self.get_cross_indices(side_code=side_code)):
				cube = self.rubcube.sides_map[side_code, cross_row, cross_col]
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
				best_side['side_code'] = side_code
				best_side['cross_weight'] = cross_weight

		return best_side['side_code']

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
