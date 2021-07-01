"""
For example:
	0 - green
	1 - yellow
	2 - red
	3 - white
	4 - orange
	5 - blue

Scanning must go from top right cell before bottom left cell.
Shifting is always to right.
"""

from cube import Cube

colors_shortcuts = {
	"green": 0,
	"yellow": 1,
	"red": 2,
	"white": 3,
	"orange": 4,
	"blue": 5,
}

sides_map = [
	[[2, 3, 3],
	 [3, 0, 0],
	 [4, 1, 5]],

	[[3, 0, 1],
	 [3, 1, 4],
	 [0, 4, 4]],

	[[4, 2, 0],
	 [5, 2, 2],
	 [5, 1, 3]],

	[[2, 2, 1],
	 [5, 3, 2],
	 [5, 3, 0]],

	[[5, 4, 0],
	 [1, 4, 0],
	 [2, 5, 4]],

	[[1, 1, 1],
	 [5, 5, 0],
	 [2, 4, 3]],
]

cube = Cube(sides_map=sides_map)
print(cube.sides_map)
print()
cube.rotate(side_idx=0, n=1, byclockwise=True)
print(cube.sides_map)
