import time
import copy
import threading

from datatypes import RubiksCube
from robot import Robot
from solver import Solver
from display import Display


def assemble_the_cube():
	rubcube.rotate_all_cube(target_side_code=best_side)
	solver.rubcube.rotate_all_cube(target_side_code=best_side)

	time.sleep(1)
	if best_side == 1:
		display.rotate_all_cube(rotation_axis="x", byclockwise=True)
	elif best_side == 2:
		display.rotate_all_cube(rotation_axis="z", byclockwise=False)
	elif best_side == 3:
		display.rotate_all_cube(rotation_axis="x", byclockwise=False)
	elif best_side == 4:
		display.rotate_all_cube(rotation_axis="z", byclockwise=True)
	elif best_side == 5:
		for _ in range(2):
			display.rotate_all_cube(rotation_axis="z", byclockwise=True)
			time.sleep(1)

	solving_steps = solver.solve()
	for step in solving_steps[:]:
		side_code, n, byclockwise = map(int, list(step))
		for _ in range(n):
			time.sleep(1)
			display.rotate_side(side_code=side_code, byclockwise=bool(byclockwise))



robot = Robot()
rubcube = robot.scan_cube() # Returns instance of RubiksCube class
# print(rubcube.sides_map)

best_side = (None, float('inf'))

# for side in range(6):
# 	rc = copy.deepcopy(rubcube)
# 	rc.rotate_all_cube(target_side_code=side)
# 	solver = Solver(rubcube=rc)
# 	solving_steps = solver.solve()
# 	if best_side[1] > len(solving_steps):
# 		best_side = (side, len(solving_steps))
	# print(side, len(solving_steps))

best_side = best_side[0]
best_side = 5

solver = Solver(rubcube=rubcube)
# best_side = solver.get_main_side()
# best_side = 2
display = Display(rubcube=rubcube)

# assembler = threading.Thread(target=assemble_the_cube)

# assembler.start()
display.run()
