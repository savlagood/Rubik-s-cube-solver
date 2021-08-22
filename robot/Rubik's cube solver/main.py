#!/usr/bin/env pybricks-micropython
import time

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

# rgb_to_color = {
# 	# 'w': (74, 98, 100),
# 	'w': (76, 100, 100),
# 	'r': (50, 29, 12),
# 	'b': (16, 46, 81),
# 	'o': (55, 57, 29),
# 	'g': (33, 79, 56),
# 	# 'y': (63, 92, 100),
# 	'y': (65, 95, 100),
# }

rgb_to_color = {
	'central': {
		'w': (80, 100, 100),
		'r': (52, 29, 17),
		'b': (15, 46, 79),
		'o': (62, 66, 40),
		'g': (33, 78, 59),
		'y': (70, 100, 100),
	},
	'cross': {
		'w': (70, 95, 100),
		'r': (45, 28, 13),
		'b': (14, 45, 75),
		'o': (55, 57, 29),
		'g': (31, 75, 53),
		'y': (60, 85, 100),
	},
	'corner': {
		'w': (68, 94, 100),
		'r': (44, 26, 12),
		'b': (12, 43, 71),
		'o': (53, 56, 28),
		'g': (28, 71, 53),
		'y': (55, 85, 100),
	},
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
		self.infrared_sensor = InfraredSensor(Port.S4)
		self.color_sensor = ColorSensor(Port.S3)

		# Motor speeds
		self.platform_speed = 180 / 12 * 37
		self.hand_speed = 270
		self.scanner_speed = 700

		# Resets all motors angles
		self.platform.reset_angle(0)
		self.hand.reset_angle(0)
		self.scanner.reset_angle(0)

	def rotate_platform(self, n:int, byclockwise:bool=True):
		"""Rotate platform on which the Rubik's cube stands."""
		n %= 4

		if n == 0:
			return
		elif n > 2:
			n = 1
			byclockwise = not byclockwise
		
		n *= 1 if byclockwise else -1
		
		self.platform.run_angle(speed=self.platform_speed, rotation_angle=n*270)
	
	def hand_rotate(self, n:int):
		"""Rotate cube by hand motor."""
		n %= 4

		for t in range(n):
			self.hand.run_target(speed=self.hand_speed, target_angle=200)
			self.hand.run_target(speed=self.hand_speed, target_angle=0)
		
		self.hand.hold()
		time.sleep(0.1)
	
	def scan_cross_cube(self):
		"""Lift up color scanner on cross cubes of Rubik's cube and return his color at percentage."""
		self.scanner.run_target(speed=self.scanner_speed, target_angle=-590) # -560
		return self.color_sensor.rgb()
	
	def scan_corner_cube(self):
		"""Lift up color scanner on corner cubes of Rubik's cube and return his color at percentage."""
		self.scanner.run_target(speed=self.scanner_speed, target_angle=-520) # -545
		return self.color_sensor.rgb()

	def scan_central_cube(self):
		"""Lift up color scanner on central cube of Rubik's cube and return his color at percentage."""
		self.scanner.run_target(speed=self.scanner_speed, target_angle=-680)
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
		print('central:', self.color_sensor.reflection(), color)
		color = self.percent_rgb_to_color(color, 'central')
		side_colors[1][1] = color

		self.scan_corner_cube()

		# Secondly scan border cubes
		for i in range(1, 5):
			# Cross cubes
			pos = cube_index_to_pos[i * 2 - 2]
			color = self.scan_cross_cube()
			print('cross:', self.color_sensor.reflection(), color)
			color = self.percent_rgb_to_color(color, 'cross')
			side_colors[pos[0]][pos[1]] = color

			self.rotate_platform(n=0.5)

			# Corner cubes
			pos = cube_index_to_pos[i * 2 - 1]
			color = self.scan_corner_cube()
			print('corner:', self.color_sensor.relfection(), color)
			color = self.percent_rgb_to_color(color, 'corner')
			side_colors[pos[0]][pos[1]] = color

			self.rotate_platform(n=0.5)

		# Off color scanner
		self.color_scanner_off()

		return side_colors
	
	def scan_cube(self):
		"""Full scan of all cube sides."""
		cube_colors = list()

		# 0 side
		cube_colors.append(self.scan_side())
		print(cube_colors[-1])

		# 1 side
		self.hand_rotate(n=1)
		cube_colors.append(self.scan_side())
		print(cube_colors[-1])

		# 2 side
		self.rotate_platform(n=1)
		self.hand_rotate(n=1)
		side_colors = self.scan_side()
		side_colors = self.rotate_matrix(side_colors, n=1, byclockwise=False)
		cube_colors.append(side_colors)
		print(cube_colors[-1])

		# 3 side
		self.hand_rotate(n=1)
		side_colors = self.scan_side()
		side_colors = self.rotate_matrix(side_colors, n=1, byclockwise=False)
		cube_colors.append(side_colors)
		print(cube_colors[-1])

		# 4 side
		self.hand_rotate(n=1)
		side_colors = self.scan_side()
		side_colors = self.rotate_matrix(side_colors, n=1, byclockwise=False)
		cube_colors.append(side_colors)
		print(cube_colors[-1])

		# 5 side
		self.rotate_platform(n=1, byclockwise=False)
		self.hand_rotate(n=1)
		cube_colors.append(self.scan_side())
		print(cube_colors[-1])

		return cube_colors
	
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
	
	print(r.scan_cross_cube())
	print(r.color_sensor.value0())

	# cube_colors = r.scan_cube()
	# print(cube_colors)

	time.sleep(1)
