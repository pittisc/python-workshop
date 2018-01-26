import socket
import sys
import ssl

def main():
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#client = ssl.wrap_socket(client)
	client.connect(("127.0.0.1", 9001))
	client.send("GET / HTTP/1.1\r\nHost: xkcd.com\r\n\r\n")
	data = client.recv(4096)
	print data

if __name__ == "__main__":
	main()