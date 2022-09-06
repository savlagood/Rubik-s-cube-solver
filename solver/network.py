import sys
import time
import json
import socket
import threading

from color_detector import rgb_to_color_name
from datatypes import RubiksCube
from solver import Solver
from display import Display


def validation(rubcube:RubiksCube) -> bool:
	"""Validates that rubcube was assembled correct."""
	for side_idx in range(6):
		central_cube_color = rubcube.sides_map[side_idx][1][1].color
		for row_idx in range(3):
			for col_idx in range(3):
				if row_idx == col_idx == 1:
					continue

				color = rubcube.sides_map[side_idx][row_idx][col_idx].color
				if color != central_cube_color:
					return False

	return True

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
			time.sleep(1)
			display.rotate_side(side_code=side_code, byclockwise=bool(byclockwise))

		resp = conn.recv(1024)
		if not resp:
			# Error
			print("[ Robot disconnected! ]")
			return

	print("[ Solving finished! ]")

if __name__ == "__main__":
	HOST = "10.42.0.1"
	#HOST = "192.168.137.1"
	PORT = 56789

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
			while True:
				raw_colors = conn.recv(1024)
				if not raw_colors:
					print("[ Colors didn't recived ]")
					s.close()
					sys.exit()

				print("[ Colors recived! ]")

				raw_colors = json.loads(raw_colors.decode())
				sides_map = rgb_to_color_name(raw_colors)
				print(sides_map)

				color_counter = {'r': 0, 'o': 0, 'w': 0, 'y': 0, 'g': 0, 'b': 0}
				for side in sides_map:
					for row in side:
						for cube_color in row:
							color_counter[cube_color] += 1

				if min(color_counter.values()) != 9 and max(color_counter.values()) != 9:
					print(color_counter)
					print("[ Rescanning ]")
					conn.sendto("rescan".encode(), addr)
					continue

				rubcube = RubiksCube(sides_map)
				solver = Solver(rubcube)

				try:
					# If solver.solve() raise exception then cube was scanned incorrectly
					solving_steps = solver.solve()
				except:
					# Cube was scanned incorrectly
					print("[ Rescanning ]")
					conn.sendto("rescan".encode(), addr)
					continue

				if validation(solver.rubcube):
					# Everything is awesome
					break
				else:
					# Cube was scanned incorrectly
					print("[ Rescanning ]")
					conn.sendto("rescan".encode(), addr)
					continue

			# sides_map = []
			# rubcube = RubiksCube(sides_map)
			# solver = Solver(rubcube)
			# solving_steps = solver.solve()

			display = Display(rubcube)

			# Visual assembler starts at thread
			assembler = threading.Thread(target=assemble_the_cube, args=(solving_steps, conn, addr))
			assembler.start()

			# Launching display visualisation
			restart = True
			while restart:
				try:
					display.run()
					restart = False
				except:
					print("[ Error at starting display. Restarts display ]")

		s.close()

	print("[ Server stopped ]")
