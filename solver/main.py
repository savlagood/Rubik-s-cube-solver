import time
import copy
import threading

from color_detector import rgb_to_color_name
from datatypes import RubiksCube
from solver import Solver
from display import Display

# raw_input = [[[(5, 22, 49), (44, 18, 8), (58, 88, 100)], [(7, 33, 13), (29, 9, 6), (7, 35, 11)], [(46, 57, 13), (41, 18, 8), (5, 23, 49)]], [[(38, 16, 6), (7, 34, 11), (29, 9, 4)], [(56, 67, 15), (7, 24, 54), (28, 10, 6)], [(22, 8, 5), (26, 10, 6), (54, 82, 95)]], [[(53, 64, 13), (58, 69, 15), (25, 9, 4)], [(64, 95, 100), (66, 94, 100), (6, 31, 10)], [(6, 30, 10), (61, 93, 100), (22, 9, 5)]], [[(5, 22, 49), (6, 24, 55), (39, 17, 7)], [(27, 10, 6), (7, 33, 12), (42, 19, 8)], [(49, 60, 13), (6, 23, 52), (5, 21, 45)]], [[(57, 86, 100), (64, 96, 100), (6, 31, 10)], [(58, 70, 15), (47, 54, 16), (26, 10, 5)], [(37, 16, 6), (42, 18, 9), (54, 82, 95)]], [[(52, 63, 13), (64, 96, 100), (6, 31, 10)], [(57, 68, 15), (48, 19, 9), (6, 24, 53)], [(5, 29, 9), (6, 23, 53), (37, 16, 6)]]]
# raw_input = [[[(5, 20, 47), (39, 17, 7), (54, 81, 99)], [(6, 31, 11), (30, 10, 6), (6, 33, 10)], [(47, 56, 11), (40, 17, 7), (5, 21, 47)]], [[(36, 16, 5), (6, 31, 10), (23, 9, 4)], [(53, 65, 15), (6, 23, 49), (26, 10, 5)], [(23, 9, 4), (25, 10, 5), (53, 79, 100)]], [[(49, 59, 13), (53, 62, 14), (23, 9, 3)], [(59, 89, 100), (68, 99, 100), (6, 30, 11)], [(5, 28, 10), (57, 86, 100), (22, 9, 4)]], [[(5, 21, 48), (6, 22, 52), (37, 16, 6)], [(25, 9, 5), (7, 35, 13), (42, 18, 7)], [(46, 56, 12), (6, 23, 51), (5, 21, 48)]], [[(53, 78, 98), (58, 85, 100), (5, 29, 9)], [(54, 65, 15), (43, 52, 13), (25, 10, 4)], [(37, 16, 5), (41, 18, 7), (54, 81, 100)]], [[(49, 60, 12), (61, 91, 100), (6, 30, 9)], [(52, 63, 15), (47, 19, 8), (6, 22, 51)], [(5, 27, 9), (6, 22, 48), (34, 15, 5)]]]

def assemble_the_cube() -> None:
	solving_steps = solver.solve()
	print(f"Len of solving steps: {len(solving_steps)}")
	print("Solving steps:\n", solving_steps)

	for i, step in enumerate(solving_steps[:]):
		side_code, n, byclockwise = map(int, list(step))
		for _ in range(n):
			time.sleep(1)
			display.rotate_side(side_code=side_code, byclockwise=bool(byclockwise))

# sides_map = rgb_to_color_name(raw_input)
sides_map = [[['w', 'g', 'b'], ['o', 'r', 'o'], ['b', 'g', 'y']], [['w', 'w', 'g'], ['y', 'y', 'o'], ['o', 'o', 'w']], [['o', 'g', 'r'], ['y', 'b', 'r'], ['r', 'r', 'w']], [['y', 'y', 'r'], ['w', 'w', 'g'], ['g', 'w', 'r']], [['b', 'b', 'o'], ['r', 'g', 'o'], ['y', 'b', 'b']], [['g', 'y', 'y'], ['b', 'o', 'w'], ['o', 'b', 'g']]]

color_counter = {'r': 0, 'o': 0, 'w': 0, 'y': 0, 'g': 0, 'b': 0}
for side in sides_map:
	for row in side:
		for cube_color in row:
			color_counter[cube_color] += 1

print(color_counter)
print(sides_map)

rubcube = RubiksCube(sides_map)
solver = Solver(rubcube=rubcube)
# print(solver.solve())
display = Display(rubcube=solver.rubcube)
# assembler = threading.Thread(target=assemble_the_cube)
# assembler.start()

restart = True
while restart:
	try:
		display.run()
		restart = False
	except:
		print("EXCEPTION!")
