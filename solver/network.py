import time
import json
import socket
import threading

from color_detector import rgb_to_color_name
from datatypes import RubiksCube
from solver import Solver
from display import Display

def assemble_the_cube(solving_steps:list, conn:socket.socket, addr:tuple) -> None:
	"""
	Solves the Rubik's cube by solving_steps.
	Rotates sides at display synchronously with robot.
	"""
	# Starts solving
	conn.sendto("solving".encode(), addr)

	time.sleep(1)
	print("[ Starts solving! ]")
	for i, step in enumerate(solving_steps[:]):
		print(f"{i} / {len(solving_steps)}")
		side_code, n, byclockwise = map(int, list(step))
		conn.sendto(step.encode(), addr)
		for _ in range(n):
			display.rotate_side(side_code=side_code, byclockwise=bool(byclockwise))

		resp = conn.recv(1024)
		if not resp:
			# Error
			print("[ Robot disconnected! ]")
			return

	print("[ Solving finished! ]")

HOST = "10.42.0.1"
PORT = 56780

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	# Creates a server at HOST and PORT
	s.bind((HOST, PORT))
	s.listen()
	print(f"[ Server started at host:{HOST}, port:{PORT} ]")

	# Accepts the connection
	conn, addr = s.accept()
	with conn:
		print(f"[ Connected by {addr} ]")
		# Checks test message
		test_message = conn.recv(1024)
		if not test_message:
			# Error at robot side
			print("[ Test message didn't recived ]")
			s.close()
			sys.exit()

		print("[ Test message recived! ]")
		conn.sendto("scan".encode(), addr)

		# Gets raw colors (red, green blue at percents)
		raw_colors = conn.recv(1024)
		if not raw_colors:
			print("[ Colors didn't recived ]")
			s.close()
			sys.exit()

		print("[ Colors recived! ]")
		raw_colors = json.loads(raw_colors.decode())
		# print(raw_colors)
		sides_map = rgb_to_color_name(raw_colors)

		rubcube = RubiksCube(sides_map)
		solver = Solver(rubcube)
		solving_steps = solver.solve()

		display = Display(rubcube)

		assembler = threading.Thread(target=assemble_the_cube, args=(solving_steps, conn, addr))
		assembler.start()

		restart = True
		while restart:
			try:
				display.run()
				restart = False
			except:
				print("[ Error at starting display. Restarts display ]")


print("[ Server stopped ]")
