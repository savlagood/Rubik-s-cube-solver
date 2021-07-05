"""
class Square:
	color: int
	neighbors: list

class Cube:
	sides_map: list

0: 1 2 3 4
1: 0 2 5 4
2: 0 3 5 1
3: 0 4 5 2
4: 0 1 5 3
5: 1 2 3 4

"""

import numpy as np

side_neighbors = {
	0: [3, 2, 1, 4],
	1: [0, 2, 5, 4],
	2: [0, 3, 5, 1],
	3: [0, 4, 5, 2],
	4: [0, 1, 5, 3],
	5: [4, 1, 2, 3],
}


class Square:
	def __init__(self, color, neigh_colors=None):
		self.color = color
		self.neigh_colors = neigh_colors if neigh_colors is not None else list()

	def __str__(self):
		return f"c-{self.color}:" + "".join(map(str, self.neigh_colors))

	def __repr__(self):
		return str(self)

	def __len__(self):
		return len(self.neigh_colors) + 1

	def add_neigh_color(self, *colors):
		for color in colors:
			self.neigh_colors.append(color)


class Cube:
	def __init__(self, sides_map):
		for side in range(6):
			for row in range(3):
				for col in range(3):
					sides_map[side][row][col] = Square(sides_map[side][row][col])

		self.sides_map = np.array(sides_map)

		for side in range(6):
			for row in range(3):
				for col in range(3):
					square = self.sides_map[side, row, col]

					if row == 0 and col == 0: # => 3, 0
						square.add_neigh_color(
							self.sides_map[side_neighbors[side][0], 2, 0].color,
							self.sides_map[side_neighbors[side][3], 0, 2].color)

					elif row == 0 and col == 1: # => 0
						square.add_neigh_color(
							self.sides_map[side_neighbors[side][0], 2, 1].color)

					elif row == 0 and col == 2: # => 0, 1
						square.add_neigh_color(
							self.sides_map[side_neighbors[side][0], 2, 2].color,
							self.sides_map[side_neighbors[side][1], 0, 0].color)

					elif row == 1 and col == 0: # => 3
						square.add_neigh_color(
							self.sides_map[side_neighbors[side][3], 1, 2].color)

					elif row == 1 and col == 1: # => None because middle
						pass
					elif row == 1 and col == 2: # => 1
						square.add_neigh_color(
							self.sides_map[side_neighbors[side][1], 1, 0].color)

					elif row == 2 and col == 0: # => 2, 3
						square.add_neigh_color(
							self.sides_map[side_neighbors[side][2], 0, 0].color,
							self.sides_map[side_neighbors[side][3], 2, 2].color)

					elif row == 2 and col == 1: # => 2
						square.add_neigh_color(
							self.sides_map[side_neighbors[side][2], 0, 1].color)

					elif row == 2 and col == 2: # => 1, 2
						square.add_neigh_color(
							self.sides_map[side_neighbors[side][1], 2, 0].color,
							self.sides_map[side_neighbors[side][2], 0, 2].color)

					self.sides_map[side, row, col] = square

	def rotate(self, side_idx:int, n:int, byclockwise:bool):
		n %= 4

		if byclockwise:
			self.sides_map[side_idx] = np.rot90(self.sides_map[side_idx], -n)
		else:
			self.sides_map[side_idx] = np.rot90(self.sides_map[side_idx], n)

		for _ in range(n):
			if side_idx == 0:
				if byclockwise:
					self.sides_map[[1, 2, 3, 4], 0] = self.sides_map[[2, 3, 4, 1], 0]
				else:
					self.sides_map[[1, 2, 3, 4], 0] = self.sides_map[[4, 1, 2, 3], 0]

			elif side_idx == 1:
				if byclockwise:
					rows = [
						np.rot90(self.sides_map[4, :, 2], -1), # 0
						np.rot90(self.sides_map[0, 2], -1), # 2
						np.rot90(self.sides_map[2, :, 0], 2), # 5
						self.sides_map[5, :, 2], # 4
					]

				else:
					rows = [
						mp.rot90(self.sides_map[2, :, 0], 1), # 0
						np.rot90(self.sides_map[5, :, 2], 2), # 2
						np.rot90(self.sides_map[0, 2], 1), # 4
						self.sides_map[4, :, 2], # 5
					]

				self.sides_map[0, 2, :] = rows[0]
				self.sides_map[2, :, 0] = rows[1]
				self.sides_map[5, :, 0] = rows[2]
				self.sides_map[4, :, 2] = rows[3]

			elif side_idx == 2:
				if byclockwise:
					rows = [
						self.sides_map[1, :, 2], # 0
						np.rot90(self.sides_map[0, :, 2], 2), # 3
						np.rot90(self.sides_map[3, :, 0], 1), # 5
						np.rot90(self.sides_map[5, 0, :], 1), # 1
					]

				else:
					rows = [
						np.rot90(self.sides_map[3, :, 0], 2), # 0
						np.rot90(self.sides_map[5, 0, :], -1), # 3
						np.rot90(self.sides_map[1, :, 2], -1), # 5
						self.sides_map[0, :, 2], # 1
					]

				self.sides_map[0, :, 2] = rows[0]
				self.sides_map[3, :, 0] = rows[1]
				self.sides_map[5, 2, :] = rows[2]
				self.sides_map[1, :, 2] = rows[3]

			elif side_idx == 3:
				if byclockwise:
					rows = [
						np.rot90(self.sides_map[2, :, 2], 1), # 0
						np.rot90(self.sides_map[0, 0, :], 1), # 4
						self.sides_map[4, :, 0], # 5
						np.rot90(self.sides_map[5, :, 0], 2), # 2
					]

				else:
					rows = [
						np.rot90(self.sides_map[4, :, 0], -1), # 0
						self.sides_map[5, 0, :], # 4
						np.rot90(self.sides_map[2, :, 2], 2), # 5
						np.rot90(self.sides_map[0, :, 2], -1), # 2
					]

				self.sides_map[0, :, 2] = rows[0]
				self.sides_map[4, :, 0] = rows[1]
				self.sides_map[5, 2, :] = rows[2]
				self.sides_map[2, :, 2] = rows[3]

			elif side_idx == 4:
				if byclockwise:
					rows = [
						np.rot90(self.sides_map[3, :, 2], 2), # 0
						self.sides_map[0, :, 0], # 1
						np.rot90(self.sides_map[1, :, 0], -1), # 5
						np.rot90(self.sides_map[5, 0, :], -1), # 3
					]

				else:
					rows = [
						self.sides_map[1, :, 0], # 0
						np.rot90(self.sides_map[5, 0, :], 1), # 1
						np.rot90(self.sides_map[3, :, 2], 1), # 5
						np.rot90(self.sides_map[0, :, 0], 2), # 3
					]

				self.sides_map[0, :, 0] = rows[0]
				self.sides_map[1, :, 0] = rows[1]
				self.sides_map[5, 0, :] = rows[2]
				self.sides_map[3, :, 2] = rows[3]

			elif side_idx == 5:
				if byclockwise:
					self.sides_map[[1, 2, 3, 4], 2] = self.sides_map[[4, 1, 2, 3], 2]
				else:
					self.sides_map[[1, 2, 3, 4], 2] = self.sides_map[[2, 3, 4, 1], 2]
