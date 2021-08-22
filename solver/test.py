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

def percent_rgb_to_color(rgb:tuple, cube_type:str):
	"""Convert percent rgb to color."""
	best_lag = float('inf')
	best_color = None

	for color, avg_rgb in rgb_to_color[cube_type].items():
		lag = abs(avg_rgb[0] - rgb[0]) + abs(avg_rgb[1] - rgb[1]) + abs(avg_rgb[2] - rgb[2])

		if lag < best_lag:
			best_color = color
			best_lag = lag

		print(best_lag, best_color, lag, color)

	return best_color