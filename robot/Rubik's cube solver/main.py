#!/usr/bin/env pybricks-micropython
import time
import threading

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
								 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

cube_index_to_pos = {
	0: (2, 1),
	1: (2, 2),
	2: (1, 2),
	3: (0, 2),
	4: (0, 1),
	5: (0, 0),
	6: (1, 0),
	7: (2, 0),
}

rgb_to_color = {
	'central': {
		'w': (82, 100, 100), 
		'r': (53, 28, 16),
		'b': (15, 45, 78),
		'o': (61, 63, 38),
		'g': (31, 74, 53),
		'y': (69, 98, 100),
	},
	'cross': {
		'w': (68, 90, 100), 
		'r': (41, 25, 12),
		'b': (12, 42, 67),
		'o': (50, 55, 28),
		'g': (27, 69, 49),
		'y': (58, 89, 100),
	},
	'corner': {
		'w': (76, 100, 100), 
		'r': (43, 26, 13),
		'b': (13, 43, 74),
		'o': (54, 56, 30),
		'g': (29, 70, 53),
		'y': (60, 90, 100),
	}
}


class Robot:
	def __init__(self):
		"""Initalizing main robot parameters."""
		# Mian EV3 Brick
		self.ev3 = EV3Brick()

		# Motors
		self.platform = Motor(Port.B)
		self.hand = Motor(Port.C)
		self.scanner = Motor(Port.A)

		# Sensors
		# self.infrared_sensor = InfraredSensor(Port.S4)
		self.color_sensor = ColorSensor(Port.S3)

		# Motor speeds
		self.platform_speed = 180 / 12 * 40 # 37
		self.hand_speed = 350 # 270
		self.scanner_speed = 1000

		# Resets all motors angles
		self.platform.reset_angle(0)
		self.hand.reset_angle(0)
		self.scanner.reset_angle(0)

		# Codes of sides from color sensor
		# 0 - Top, 1 - front, 2 - left, 3 - back, 4 - right, 5 - bottom
		self.side_codes_seq = [0, 1, 2, 3, 4, 5]

	def rotate_platform(self, n:int, byclockwise:bool=True, side_control:bool=True, rot_optim:bool=True):
		"""Rotate platform on which the Rubik's cube stands n times byclockwise.
		:side_control - if True then self.side_codes_seq will be changed.
		:rot_optim - optimizate n rotation. Instead of 4 - 0 times.
		"""
		if rot_optim:
			n %= 4
			if n == 0:
				return
			elif n > 2:
				n = 1
				byclockwise = not byclockwise
			
			n *= 1 if byclockwise else -1
		
		self.platform.run_angle(speed=self.platform_speed, rotation_angle=n*270)

		# Change side codes sequence
		if side_control:
			scs = self.side_codes_seq # Create shortcut
			scs[1], scs[2], scs[3], scs[4] = scs[(1+n-1)%4+1], scs[(2+n-1)%4+1], scs[(3+n-1)%4+1], scs[(4+n-1)%4+1]
	
	def hand_rotate(self, n:int, side_control:bool=True):
		"""Rotate cube by hand motor n times.
		:side_control - if True then self.side_codes_seq will be changed.
		"""
		n %= 4

		for t in range(n):
			self.hand.run_target(speed=self.hand_speed, target_angle=200)
			self.hand.run_target(speed=self.hand_speed, target_angle=0)
		
			# Change side codes sequence
			if side_control:
				scs = self.side_codes_seq
				scs[0], scs[1], scs[5], scs[3] = scs[1], scs[5], scs[3], scs[0]
	
	def scan_cross_cube(self):
		"""Lift up color scanner on cross cubes of Rubik's cube and return his color at percentage."""
		self.scanner.run_target(speed=self.scanner_speed, target_angle=-580, then=Stop.COAST) # -600
		return self.color_sensor.rgb()
	
	def scan_corner_cube(self):
		"""Lift up color scanner on corner cubes of Rubik's cube and return his color at percentage."""
		self.scanner.run_target(speed=self.scanner_speed, target_angle=-520, then=Stop.COAST) # -560
		return self.color_sensor.rgb()

	def scan_central_cube(self):
		"""Lift up color scanner on central cube of Rubik's cube and return his color at percentage."""
		self.scanner.run_target(speed=self.scanner_speed, target_angle=-710) # -700
		return self.color_sensor.rgb()
	
	def color_scanner_off(self):
		"""Let down color scanner."""	
		self.scanner.run_target(speed=self.scanner_speed, target_angle=0)
		self.scanner.hold()
		time.sleep(0.1)

	def scan_side(self):
		"""Full scan of one side."""
		side_colors = [[0 for _ in range(3)] for _ in range(3)]

		# Firstly scan central cube
		color = self.scan_central_cube()
		print(color, ': ', end="")
		color = self.percent_rgb_to_color(color, 'central')
		print(color)
		side_colors[1][1] = color

		self.scan_corner_cube()

		# Secondly scan border cubes
		for i in range(1, 5):
			# Cross cubes
			pos = cube_index_to_pos[i * 2 - 2]
			color = self.scan_cross_cube()
			print(color, ': ', end="")
			color = self.percent_rgb_to_color(color, 'cross')
			print(color)
			side_colors[pos[0]][pos[1]] = color

			self.rotate_platform(n=0.5, side_control=False)

			# Corner cubes
			pos = cube_index_to_pos[i * 2 - 1]
			color = self.scan_corner_cube()
			print(color, ': ', end="")
			color = self.percent_rgb_to_color(color, 'corner')
			print(color)
			side_colors[pos[0]][pos[1]] = color

			self.rotate_platform(n=0.5, side_control=False)

			# Change side codes sequence
			scs = self.side_codes_seq # Create shortcut
			scs[1], scs[2], scs[3], scs[4] = scs[2], scs[3], scs[4], scs[1]

		# Off color scanner
		self.color_scanner_off()

		return side_colors
	
	def scan_cube(self):
		"""Full scan of all cube sides."""
		cube_colors = list()

		# 0 side
		cube_colors.append(self.scan_side())
		# print(cube_colors[-1])

		# 1 side
		self.hand_rotate(n=1)
		cube_colors.append(self.scan_side())
		# print(cube_colors[-1])

		# 2 side
		self.rotate_platform(n=1)
		self.hand_rotate(n=1)
		side_colors = self.scan_side()
		side_colors = self.rotate_matrix(side_colors, n=1, byclockwise=False)
		cube_colors.append(side_colors)
		# print(cube_colors[-1])

		# 3 side
		self.hand_rotate(n=1)
		side_colors = self.scan_side()
		side_colors = self.rotate_matrix(side_colors, n=1, byclockwise=False)
		cube_colors.append(side_colors)
		# print(cube_colors[-1])

		# 4 side
		self.hand_rotate(n=1)
		side_colors = self.scan_side()
		side_colors = self.rotate_matrix(side_colors, n=1, byclockwise=False)
		cube_colors.append(side_colors)
		# print(cube_colors[-1])

		# 5 side
		self.rotate_platform(n=1, byclockwise=False)
		self.hand_rotate(n=1)
		cube_colors.append(self.scan_side())
		# print(cube_colors[-1])

		return cube_colors
	
	def rotate_current_side(self, n:int=1, byclockwise:bool=True):
		"""Rotate side on which cube stands byclockwise n times."""
		n %= 4
		# Because rotate SIDE but not platform!
		byclockwise = not byclockwise

		if n == 3:
			n = 1
			byclockwise = not byclockwise
		
		if n > 0:
			self.hand.run_target(speed=self.hand_speed, target_angle=110)
			self.rotate_platform(n, byclockwise, side_control=False)
			self.hand.run_target(speed=self.hand_speed, target_angle=0)
	
	def target_to_current(self, target_side_code:int):
		"""Move side with target_side_code to the bottom of cube."""
		index = self.side_codes_seq.index(target_side_code)
		if index == 0:
			# if target side is top side
			self.hand_rotate(2)

		elif index < 5:
			# if target side not at top and not at bottom 
			self.rotate_platform(3 - index, byclockwise=False)
			self.hand_rotate(1)
	
	def rotate_side(self, side_code:int, n:int=1, byclockwise:bool=True):
		"""Rotate side with side_code n times byclockwise."""
		self.target_to_current(side_code)
		self.rotate_current_side(n, byclockwise=byclockwise)

	@staticmethod
	def percent_rgb_to_color(rgb:tuple, cube_type:str):
		"""Convert percent rgb to color."""
		best_lag = float('inf')
		best_color = None

		for color, avg_rgb in rgb_to_color[cube_type].items():
			lag = abs(avg_rgb[0] - rgb[0]) + abs(avg_rgb[1] - rgb[1]) + abs(avg_rgb[2] - rgb[2])

			if lag < best_lag:
				best_color = color
				best_lag = lag

		return best_color

	@staticmethod
	def rotate_matrix(matrix:list, n:int=1, byclockwise:bool=True):
		"""Rotate matrix n times by byclockwise. One time = 90 deg."""
		if not byclockwise:
			n = abs(n - 4)
		
		n %= 4
		for _ in range(n):
			matrix = list(map(lambda l: list(l), list(zip(*matrix[::-1]))))
		
		return matrix

if __name__ == "__main__":
	r = Robot()

	
	# for i in range(50):
	
	# print(r.scan_side())

	# print(r.scan_central_cube())
	# print(r.scan_cross_cube())
	# time.sleep(3)
	# r.rotate_platform(0.5, side_control=False)
	# print(r.scan_corner_cube())
	# time.sleep(3)
	# r.rotate_platform(0.5, False, side_control=False)
	# r.color_scanner_off()

	
	# # r.rotate_platform(0.5, byclockwise=False, side_control=False)
	# r.color_scanner_off()

	# for i in range(5):
	# 	print(r.scan_cube())
	# 	r.hand_rotate(2)
	# 	r.rotate_platform(1)

	print('Cube colors:')
	print(r.scan_cube())

	r.hand_rotate(2)
	r.rotate_platform(1)
	
	# inp = ['021', '221', '121', '421', '321', '020', '111', '511', '110', '521', '311', '510', '310', '111', '511', '110', '211', '511', '210', '511', '111', '511', '110', '510', '111', '511', '110', '510', '111', '511', '110', '410', '511', '411', '511', '311', '510', '310', '110', '511', '111', '511', '411', '510', '410', '520', '210', '511', '211', '511', '111', '510', '110', '310', '511', '311', '511', '211', '510', '210', '411', '311', '511', '310', '510', '311', '511', '310', '510', '410', '311', '511', '310', '511', '311', '521', '310', '510', '111', '510', '310', '511', '110', '510', '311', '210', '111', '211', '110', '210', '111', '211', '110', '511', '210', '111', '211', '110', '210', '111', '211', '110', '511', '111', '210', '110', '211', '111', '210', '110', '211', '511', '111', '210', '110', '211', '111', '210', '110', '211', '511']
	# solving_steps = list(map(str, inp[1:-1].replace(',', '').replace('\'', '').split()))

	# solving_steps = ['410', '021', '111', '011', '310', '221', '011', '311', '511', '310', '511', '411', '510', '410', '511', '211', '510', '210', '511', '211', '510', '210', '411', '511', '410', '311', '510', '310', '511', '311', '510', '310', '510', '211', '510', '210', '510', '310', '511', '311', '520', '410', '511', '411', '511', '311', '510', '310', '511', '111', '510', '110', '510', '210', '511', '211', '411', '511', '410', '511', '411', '521', '410', '511', '210', '511', '411', '510', '211', '511', '410', '210', '111', '211', '110', '210', '111', '211', '110', '521', '111', '210', '110', '211', '111', '210', '110', '211', '511']

	# for step in solving_steps[:]:
	# 	side_code, n, byclockwise = map(int, list(step))
	# 	r.rotate_side(side_code, n, byclockwise)

	time.sleep(1)
