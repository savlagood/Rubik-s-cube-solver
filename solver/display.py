import numpy as np
from ursina import *

from shortcuts import (sides_codes, colors_shortcuts, sides_names,
					   sides_positions, sides_rotations, rotation_axises)
from datatypes import RubiksCube


class Display(Ursina):
	def __init__(self, rubcube:RubiksCube):
		super().__init__()

		self.left_poses = [Vec3(-1, y, z) for y in range(1, -2, -1) for z in range(1, -2, -1)]
		self.right_poses = [Vec3(1, y, z) for y in range(1, -2, -1) for z in range(-1, 2)]
		self.top_poses = [Vec3(x, 1, z) for z in range(1, -2, -1) for x in range(-1, 2)]
		self.bottom_poses = [Vec3(x, -1, z) for x in range(-1, 2) for z in range(1, -2, -1)]
		self.front_poses = [Vec3(x, y, -1) for y in range(1, -2, -1) for x in range(-1, 2)]
		self.back_poses = [Vec3(x, y, 1) for y in range(1, -2, -1) for x in range(1, -2, -1)]

		self.all_poses = set(self.left_poses + self.right_poses + self.top_poses + \
							 self.bottom_poses + self.front_poses + self.back_poses)
		self.cam = EditorCamera(rotation=(30, -45, 0)) # rotation=(45, 45, 0) world_position=(2, 1, -2), 
		self.pivot = Entity()

		self.side_texture = "textures/side"
		self.animation_time = 0.5
		# self.animation_time = 0.8
		self.rotation = False

		window.windowed_size = 0.7
		window.update_aspect_ratio()
		window.late_init()
		# window.fullscreen = True



		self.cubes = list()
		self.sides_map = np.empty((6, 3, 3), dtype=Entity)

		for idx in range(9):
			for side_name in sides_names:
				side_code = sides_codes[side_name]
				side_position = sides_positions[side_name]
				side_rotation = sides_rotations[side_name]
				side_color = eval(
					f"color.{rubcube.sides_map[side_code, idx//3, idx%3].color_name}"
				)

				cube = self.get_cube(position=eval(f"self.{side_name}_poses[idx]"))

				self.sides_map[side_code, idx//3, idx%3] = Entity(
					parent=cube,
					model="quad",
					texture=self.side_texture,
					color=side_color,
					position=side_position,
					rotation=side_rotation,
				)
	
	def get_cube(self, position:Vec3):
		cubes = list(filter(lambda cube: cube.world_position == position, self.cubes))
		if cubes:
			cube = cubes[0]
		else:
			cube = Entity(position=position)
			self.cubes.append(cube)

		return cube

	def reaprent_all_cubes_to_scene(self):
		for cube in self.cubes:
			if cube.parent == self.pivot:
				world_pos, world_rot = round(cube.world_position, 1), cube.world_rotation
				cube.parent = scene
				cube.position, cube.rotation = world_pos, world_rot

		self.pivot.rotation = 0

	def rotation_to_false(self):
		self.rotation = False

	def rotate_side(self, side_code:str, byclockwise:bool=True):
		n = 90
		n *= 1 if byclockwise else -1

		side_name = sides_codes[side_code]
		if side_name in ["back", "left", "bottom"]:
			n *= -1

		self.rotation = True
		self.reaprent_all_cubes_to_scene()

		cubes_poses = eval(f"self.{side_name}_poses")
		rotation_axis = rotation_axises[side_name]

		for cube in self.cubes:
			if cube.position in cubes_poses:
				cube.parent = self.pivot

		eval(f"self.pivot.animate_rotation_{rotation_axis}(n, duration=self.animation_time)")
		invoke(self.rotation_to_false, delay=self.animation_time + 0.11)

	def rotate_all_cube(self, rotation_axis:str, byclockwise:bool=True):
		n = 90
		n *= 1 if byclockwise else -1

		self.rotation = True
		self.reaprent_all_cubes_to_scene()

		for cube in self.cubes:
			cube.parent = self.pivot

		eval(f"self.pivot.animate_rotation_{rotation_axis}(n, duration=self.animation_time)")
		invoke(self.rotation_to_false, delay=self.animation_time + 0.11)

	# def input(self, key):
	# 	keys = dict(zip('asdwqe', 'left bottom right top front back'.split()))
	# 	if key in keys and not self.rotation:
	# 		self.rotate_side(keys[key])

	# 	super().input(key)
