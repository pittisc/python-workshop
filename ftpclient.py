import socket
import sys
import ssl

def main():
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#client = ssl.wrap_socket(client)
	client.connect(("127.0.0.1", 9001))
	data = client.recv(4096)
	print data
	client.send("USER username\x0d\x0a")
	data = client.recv(4096)
	print data
	client.send("PASS password\x0d\x0a")
	data = client.recv(4096)
	print data

if __name__ == "__main__":
	main()