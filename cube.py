import numpy as np


class Cube:
	def __init__(self, sides_map):
		self.sides_map = np.array(sides_map)

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
