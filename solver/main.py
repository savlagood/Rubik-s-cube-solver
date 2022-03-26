import time
import copy
import threading

from color_detector import rgb_to_color_name
from datatypes import RubiksCube
from solver import Solver
from display import Display

raw_input = [[[(49, 59, 12), (61, 93, 100), (50, 59, 12)], [(59, 91, 100), (7, 33, 11), (59, 86, 100)], [(46, 56, 12), (59, 89, 100), (42, 50, 11)]], [[(23, 9, 4), (43, 19, 6), (24, 9, 3)], [(26, 10, 5), (69, 100, 100), (26, 10, 4)], [(23, 9, 4), (40, 19, 7), (21, 9, 4)]], [[(5, 29, 9), (6, 24, 52), (5, 30, 9)], [(6, 33, 11), (48, 21, 8), (6, 33, 10)], [(6, 29, 9), (6, 25, 53), (5, 29, 9)]], [[(35, 15, 5), (26, 10, 5), (37, 16, 5)], [(40, 18, 7), (47, 59, 14), (41, 18, 7)], [(36, 16, 5), (27, 10, 4), (38, 17, 6)]], [[(5, 20, 47), (6, 33, 11), (5, 21, 48)], [(5, 23, 52), (30, 11, 6), (6, 24, 52)], [(5, 21, 48), (6, 34, 11), (5, 22, 49)]], [[(54, 82, 100), (55, 67, 14), (55, 83, 100)], [(53, 66, 15), (7, 25, 54), (55, 66, 14)], [(46, 68, 94), (51, 61, 13), (49, 72, 98)]]]

def assemble_the_cube():
	solving_steps = solver.solve()
	for i, step in enumerate(solving_steps[:]):
		side_code, n, byclockwise = map(int, list(step))
		for _ in range(n):
			time.sleep(1)
			display.rotate_side(side_code=side_code, byclockwise=bool(byclockwise))

sides_map = rgb_to_color_name(raw_input)
rubcube = RubiksCube(sides_map)

solver = Solver(rubcube=rubcube)

solving_steps = solver.solve()
print(f"Len of solving steps: {len(solving_steps)}")
print("Solving steps:\n", solving_steps)

display = Display(rubcube=solver.rubcube)

assembler = threading.Thread(target=assemble_the_cube)

assembler.start()
display.run()
