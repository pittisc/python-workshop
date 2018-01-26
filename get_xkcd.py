import socket
import ssl

def main():
	raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client = ssl.wrap_socket(raw_socket)
	client.connect(("xkcd.com", 443))
	client.send("GET / HTTP/1.1\r\nHost: xkcd.com\r\n\r\n")
	data = client.recv(4096)
	print data

if __name__ == "__main__":
	main()