import time
import copy
import threading

from datatypes import RubiksCube
from solver import Solver
from display import Display


def assemble_the_cube():
	solving_steps = solver.solve()
	print("Solving steps:\n", solving_steps)

	for step in solving_steps[:]:
		side_code, n, byclockwise = map(int, list(step))
		for _ in range(n):
			time.sleep(1)
			display.rotate_side(side_code=side_code, byclockwise=bool(byclockwise))

sides_map = [[['r', 'o', 'y'], ['y', 'y', 'y'], ['w', 'w', 'o']], [['g', 'g', 'b'], ['r', 'g', 'y'], ['o', 'r', 'w']], [['y', 'b', 'b'], ['o', 'o', 'w'], ['o', 'g', 'b']], [['r', 'b', 'g'], ['o', 'b', 'g'], ['r', 'r', 'g']], [['y', 'g', 'o'], ['o', 'r', 'b'], ['w', 'b', 'y']], [['r', 'w', 'g'], ['w', 'w', 'y'], ['w', 'r', 'b']]]
rubcube = RubiksCube(sides_map)

solver = Solver(rubcube=rubcube)
display = Display(rubcube=rubcube)

assembler = threading.Thread(target=assemble_the_cube)

assembler.start()
display.run()
