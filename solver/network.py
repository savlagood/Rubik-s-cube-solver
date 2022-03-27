import socket
import sys
import time

ev3_massage = None

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.bind(('10.42.0.1', 56789))  # your PC's Bluetooth IP & PORT
	s.listen(1)
	print('Start program...')
	while True:
		conn, addr = s.accept()
		with conn:
			while True:
				ev3_massage = conn.recv(1024)
				if ev3_massage is not None:
					ev3_massage = ev3_massage.decode()
					print('get ' + ev3_massage)
					time.sleep(1.0)
					if ev3_massage == 'BACKSPACE':
						break
					ev3_massage = None
			print('End program')
			sys.exit()














# # echo-client.py

# # import socket

# # HOST = "127.0.0.1"  # The server's hostname or IP address
# # PORT = 65432  # The port used by the server

# # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
# # 	s.connect((HOST, PORT))
# # 	s.sendall(b"Hello, world")
# # 	data = s.recv(1024)

# # print(f"Received {data!r}")


# # import socket

# # sock = socket.socket()
# # sock.bind(('10.42.0.1', 9090))
# # sock.listen(1)
# # conn, addr = sock.accept()

# # print('connected:', addr)

# # while True:
# # 	data = conn.recv(1024)
# # 	if not data:
# # 		break
# # 	conn.send(data.upper())

# # conn.close()


# import socket

# sock = socket.socket()
# sock.connect(('127.0.0.1', 9876))
# sock.send('hello, world!'.encode('utf-8'))

# data = sock.recv(1024)
# sock.close()

# print(data)