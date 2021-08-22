colors_shortcuts = {
	"w": "white",
	"r": "red",
	"b": "blue",
	"o": "orange",
	"g": "green",
	"y": "yellow",
	"white" : "w",
	"red" : "r",
	"blue" : "b",
	"orange" : "o",
	"green" : "g",
	"yellow" : "y",
}

adjacent_sides_colors = {
	"w": ["r", "b", "o", "g"],
	"r": ["y", "b", "w", "g"],
	"b": ["y", "o", "w", "r"],
	"o": ["y", "g", "w", "b"],
	"g": ["y", "r", "w", "o"],
	"y": ["b", "r", "g", "o"],
}

adjacent_sides_codes = {
	0: [1, 2, 3, 4],
	1: [5, 2, 0, 4],
	2: [5, 3, 0, 1],
	3: [5, 4, 0, 2],
	4: [5, 1, 0, 3],
	5: [2, 1, 4, 3],
}

sides_codes = {
	"top": 0,
	"front": 1,
	"right": 2,
	"back": 3,
	"left": 4,
	"bottom": 5,
	0: "top",
	1: "front",
	2: "right",
	3: "back",
	4: "left",
	5: "bottom",
}

sides_names = ["top", "front", "right", "back", "left", "bottom"]

sides_positions = {
	"top": (0, 0.5, 0),
	"front": (0, 0, -0.5),
	"right": (0.5, 0, 0),
	"back": (0, 0, 0.5),
	"left": (-0.5, 0, 0),
	"bottom": (0, -0.5, 0),
	0: (0, 0.5, 0),
	1: (0, 0, -0.5),
	2: (0.5, 0, 0),
	3: (0, 0, 0.5),
	4: (-0.5, 0, 0),
	5: (0, -0.5, 0),
}

sides_rotations = {
	"top": (90, 0, 0),
	"front": (0, 0, 0),
	"right": (0, -90, 0),
	"back": (0, 180, 0),
	"left": (0, 90, 0),
	"bottom": (-90, 0, 0),
	0: (90, 0, 0),
	1: (0, 0, 0),
	2: (0, -90, 0),
	3: (0, 180, 0),
	4: (0, 90, 0),
	5: (-90, 0, 0),
}

rotation_axises = {
	"top": "y",
	"front": "z",
	"right": "x",
	"back": "z",
	"left": "x",
	"bottom": "y",
	0: "y",
	1: "z",
	2: "x",
	3: "z",
	4: "x",
	5: "y",
}

# Side turns counter clockwise by default
side_code_to_rotation = {
	0: {1:0, 2:0, 3:0, 4:0},
	1: {5:1, 2:-1, 0:2, 4:1},
	2: {5:2, 3:-1, 0:1, 1:1},
	3: {5:-1, 4:-1, 0:0, 2:1},
	4: {5:0, 1:-1, 0:-1, 3:1},
	5: {2:2, 1:2, 4:2, 3:2},
}

# (row, col): [(adj_side_idx, adj_row, adj_col)]
# Where adj_side_idx - index of adjacent side in shortcuts.adjacent_sides_codes
# adj_row - adjacent row at adj_side_idx
# adj_col - adjacent column at adj_side_idx
adjacent_indices = {
	(0, 0): [(2, 0, 2), (3, 0, 0)],
	(0, 1): [(2, 0, 1)],
	(0, 2): [(1, 0, 2), (2, 0, 0)],
	(1, 0): [(3, 0, 1)],
	(1, 1): [],
	(1, 2): [(1, 0, 1)],
	(2, 0): [(3, 0, 2), (0, 0, 0)],
	(2, 1): [(0, 0, 1)],
	(2, 2): [(0, 0, 2), (1, 0, 0)],
}

counter_side = {
	0: 5,
	1: 3,
	2: 4,
	3: 1,
	4: 2,
	5: 0,
}
