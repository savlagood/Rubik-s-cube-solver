#!/usr/bin/env pybricks-micropython
import time
import sys

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
								 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile


cube_index_to_pos = {
	0: (2, 1),
	1: (2, 2),
	2: (1, 2),
	3: (0, 2),
	4: (0, 1),
	5: (0, 0),
	6: (1, 0),
	7: (2, 0),
}

class Robot:
	def __init__(self):
		"""Initalizing main robot parameters."""
		# Mian EV3 Brick
		self.ev3 = EV3Brick()

		# Motors
		self.platform = Motor(Port.B)
		self.hand = Motor(Port.C)
		self.scanner = Motor(Port.A)

		self.scanner.control.limits(speed=1500)

		# Sensors
		self.color_sensor = ColorSensor(Port.S3)

		# Motor speeds
		self.platform_speed = 180 / 12 * 40 # 37
		self.hand_speed = 330 # 270
		self.scanner_speed = 1400

		# Resets all motors angles
		self.platform.reset_angle(0)
		self.hand.reset_angle(0)
		self.scanner.reset_angle(0)

		# Codes of sides from color sensor
		# 0 - Top, 1 - front, 2 - left, 3 - back, 4 - right, 5 - bottom
		self.side_codes_seq = [0, 1, 2, 3, 4, 5]

		# Stabilization
		self.hand.run_time(-90, 4000, wait=False) # -360
		self.scanner.run_time(260, 4000) # 1040
		# Zeroing the anglr values
		self.hand.reset_angle(0)
		self.scanner.reset_angle(0)
		# Positing
		self.hand.run_target(speed=50, target_angle=5)
		self.scanner.run_target(speed=300, target_angle=-15)
		# Zeroing the anglr values
		self.hand.reset_angle(0)
		self.scanner.reset_angle(0)

	def rotate_platform(self, n:int, byclockwise:bool=True, side_control:bool=True, rot_optim:bool=True):
		"""Rotate platform on which the Rubik's cube stands n times byclockwise.
		:side_control - if True then self.side_codes_seq will be changed.
		:rot_optim - optimizate n rotation. Instead of 4 - 0 times.
		"""
		if rot_optim:
			n %= 4
			if n == 0:
				return
			elif n > 2:
				n = 1
				byclockwise = not byclockwise
			
			n *= 1 if byclockwise else -1
		
		self.platform.run_angle(speed=self.platform_speed, rotation_angle=n*270)

		# Change side codes sequence
		if side_control:
			scs = self.side_codes_seq # Create shortcut
			scs[1], scs[2], scs[3], scs[4] = scs[(1+n-1)%4+1], scs[(2+n-1)%4+1], scs[(3+n-1)%4+1], scs[(4+n-1)%4+1]
	
	def hand_rotate(self, n:int, side_control:bool=True, hand_raised:bool=False):
		"""Rotate cube by hand motor n times.
		:side_control - if True then self.side_codes_seq will be changed.
		:hand_raised - raise hand after cube rotation.
		"""
		n %= 4
		for t in range(n):
			self.hand_pulling_cube()
			if t < n - 1:
				self.hand_on_cube()
			# Change side codes sequence
			if side_control:
				scs = self.side_codes_seq
				scs[0], scs[1], scs[5], scs[3] = scs[1], scs[5], scs[3], scs[0]
		
		if hand_raised:
			self.hand_raised()
		
	def hand_raised(self):
		"""Hand at 0 deg."""
		self.hand.run_target(speed=self.hand_speed, target_angle=10)

	def hand_on_cube(self):
		"""Hand at 110 deg."""
		self.hand.run_target(speed=self.hand_speed, target_angle=90)
	
	def hand_pulling_cube(self):
		"""Hand at 200 deg."""
		self.hand.run_target(speed=self.hand_speed, target_angle=200)

	def scan_cross_cube(self):
		"""Lift up color scanner on cross cubes of Rubik's cube and return his color at percentage."""
		self.scanner.run_target(speed=self.scanner_speed, target_angle=-615, then=Stop.COAST) # -615
		return self.color_sensor.rgb()
	
	def scan_corner_cube(self):
		"""Lift up color scanner on corner cubes of Rubik's cube and return his color at percentage."""
		self.scanner.run_target(speed=self.scanner_speed, target_angle=-535, then=Stop.COAST) # -540
		return self.color_sensor.rgb()

	def scan_central_cube(self):
		"""Lift up color scanner on central cube of Rubik's cube and return his color at percentage."""
		self.scanner.run_target(speed=self.scanner_speed, target_angle=-750) # -720
		return self.color_sensor.rgb()
	
	def color_scanner_off(self):
		"""Let down color scanner."""	
		self.scanner.run_target(speed=self.scanner_speed, target_angle=0)
		self.scanner.hold()
		time.sleep(0.1)

	def scan_side(self):
		"""Full scan of one side."""
		side_colors = [[0 for _ in range(3)] for _ in range(3)]

		# Firstly scan central cube
		color = self.scan_central_cube()
		side_colors[1][1] = color

		self.scan_corner_cube()

		# Secondly scan border cubes
		for i in range(1, 5):
			# Cross cubes
			pos = cube_index_to_pos[i * 2 - 2]
			color = self.scan_cross_cube()
			side_colors[pos[0]][pos[1]] = color
			self.rotate_platform(n=0.5, side_control=False)

			# Corner cubes
			pos = cube_index_to_pos[i * 2 - 1]
			color = self.scan_corner_cube()
			side_colors[pos[0]][pos[1]] = color
			self.rotate_platform(n=0.5, side_control=False)

			# Change side codes sequence
			scs = self.side_codes_seq # Create shortcut
			scs[1], scs[2], scs[3], scs[4] = scs[2], scs[3], scs[4], scs[1]

		# Off color scanner
		self.color_scanner_off()
		return side_colors
	
	def scan_cube(self):
		"""Full scan of all cube sides."""
		cube_colors = list()
		# 0 side
		cube_colors.append(self.scan_side())
		# 1 side
		self.hand_rotate(1, hand_raised=True)
		cube_colors.append(self.scan_side())
		# 2 side
		self.rotate_platform(n=1)
		self.hand_rotate(1, hand_raised=True)
		side_colors = self.scan_side()
		side_colors = self.rotate_matrix(side_colors, n=1, byclockwise=False)
		cube_colors.append(side_colors)
		# 3 side
		self.hand_rotate(1, hand_raised=True)
		side_colors = self.scan_side()
		side_colors = self.rotate_matrix(side_colors, n=1, byclockwise=False)
		cube_colors.append(side_colors)
		# 4 side
		self.hand_rotate(1, hand_raised=True)
		side_colors = self.scan_side()
		side_colors = self.rotate_matrix(side_colors, n=1, byclockwise=False)
		cube_colors.append(side_colors)
		# 5 side
		self.rotate_platform(n=1, byclockwise=False)
		self.hand_rotate(1, hand_raised=True)
		cube_colors.append(self.scan_side())

		return cube_colors
	
	def rotate_current_side(self, n:int=1, byclockwise:bool=True):
		"""Rotate side on which cube stands byclockwise n times."""
		n %= 4
		# Because rotate SIDE but not platform!
		byclockwise = not byclockwise

		if n == 3:
			n = 1
			byclockwise = not byclockwise
		
		if n > 0:
			self.hand_on_cube()
			self.rotate_platform(n, byclockwise, side_control=False)
			self.hand_raised()
	
	def target_to_current(self, target_side_code:int):
		"""Move side with target_side_code to the bottom of cube."""
		index = self.side_codes_seq.index(target_side_code)
		if index == 0:
			# if target side is top side
			self.hand_rotate(2)

		elif index < 5:
			# if target side not at top and not at bottom
			if 3 - index != 0:
				self.hand_raised()
				self.rotate_platform(3 - index, byclockwise=False)

			self.hand_rotate(1)
	
	def rotate_side(self, side_code:int, n:int=1, byclockwise:bool=True):
		"""Rotate side with side_code n times byclockwise."""
		self.target_to_current(side_code)
		self.rotate_current_side(n, byclockwise=byclockwise)

	@staticmethod
	def rotate_matrix(matrix:list, n:int=1, byclockwise:bool=True):
		"""Rotate matrix n times by byclockwise. One time = 90 deg."""
		if not byclockwise:
			n = abs(n - 4)
		
		n %= 4
		for _ in range(n):
			matrix = list(map(lambda l: list(l), list(zip(*matrix[::-1]))))
		
		return matrix

if __name__ == "__main__":
	# r = Robot()
	# r.color_sensor.rgb()

	print(sys.version)



	import socket
	import sys
	import time
	ev3_message = None


	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(('10.42.0.1', 56789))    # your PC's Bluetooth IP & PORT
	print('connected')
	ev3_message = 'Hello other side!'
	s.send(ev3_message.encode())
	time.sleep(0.5)

	ev3_message = 'BACKSPACE'
	s.send(ev3_message.encode())

	print('End program')
	sys.exit()



	

	# import socket
	# sock = socket.socket()
	# sock.bind(('', 9876))
	# sock.listen(1)
	# conn, addr = sock.accept()

	# print('connected:', addr)

	# while True:
	# 	data = conn.recv(1024)
	# 	if not data:
	# 		break
	# 	conn.send(data.upper())

	# conn.close()

	
	# import socket, time

	# # host = socket.gethostbyname(socket.gethostname()) # gethostname - получает имя хоста, gethostbyname - получаеет адрес хоста по имеени
	# host = "127.0.0.1"
	# port = 65432 # Порт

	# clients = [] # Клиенты

	# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Устанавливаем протокол TCP/IP
	# s.bind((host, port)) # Поднятие сервера на host - имени и port - порте

	# quit = False
	# print("[ Server Started ]")

	# while not quit:
	# 	try:
	# 		data, addr = s.recvfrom(1024) # data - сообщение пользователя, addr - адрес пользователя, recvfrom - размер сообщения

	# 		if addr not in clients: # если клиеента нет в клиентах, то добавить в клиенты
	# 			clients.append(addr)

	# 		itsatime = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime()) # текущеее время, преобразованное в строку

	# 		print("[ " + addr[0] + " ]=[ " + addr[1] + " ]=[ " + itsatime + " ]/", end = "") # вывод в консоль информации о пользователе, время
	# 		print(data.decode('utf-8')) # вывод в консоль декодированного из кодировки utf-8 сообщения пользователя

	# 		for client in clients: # рассылка сообщеения всем клиентам кроме текущего
	# 			if addr != client:
	# 				s.sendto(data, client)

	# 	except: # остановка сервеера
	# 		print("\n[ Server Stoped ]")
	# 		quit = True
	# 		exit()
	# 		break

	# s.close() # закрытие порта


	# print('Cube colors:')
	# print(r.scan_cube())
	# r.hand_rotate(2, hand_raised=True)
	# r.rotate_platform(1)

	# solving_steps = ['511', '311', '110', '520', '211', '510', '310', '520', '311', '010', '310', '011', '111', '010', '110', '011', '111', '010', '110', '010', '411', '011', '410', '010', '411', '011', '410', '010', '411', '011', '410', '111', '010', '110', '010', '410', '011', '411', '020', '110', '011', '111', '011', '211', '010', '210', '021', '411', '010', '410', '010', '310', '011', '311', '011', '210', '011', '211', '011', '311', '010', '310', '411', '111', '011', '110', '010', '111', '011', '110', '010', '410', '311', '011', '310', '011', '311', '021', '310', '010', '211', '010', '410', '011', '210', '010', '411', '011', '111', '010', '310', '011', '110', '010', '311', '410', '111', '411', '110', '410', '111', '411', '110', '011', '410', '111', '411', '110', '410', '111', '411', '110', '011', '410', '111', '411', '110', '410', '111', '411', '110', '021']

	# print(len(solving_steps))
	# for i, step in enumerate(solving_steps[:]):
	# 	print(i, '/', len(solving_steps))
	# 	side_code, n, byclockwise = map(int, list(step))
	# 	r.rotate_side(side_code, n, byclockwise)

	time.sleep(1)
