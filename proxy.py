import sys
import socket
import threading
import ssl

def server_loop(lhost, lport, rhost, rport, recv_first):

	# create server object and bind to port. 
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		server.bind((lhost, lport))
	except:
		print "[!] Failed to bind to %s:%d" % (lhost, lport)
		sys.exit(0)
	print "[*] Listening on %s:%d" % (lhost, lport)

	# accept backlog of 5 connections
	server.listen(5)

	# spawn threads to handle incoming connections
	while True:
		client_socket, addr = server.accept()
		print "[>] Received incoming connection from %s:%d" % (addr[0], addr[1])
		proxy_thread = threading.Thread(target = proxy_handler,
										args = (client_socket, rhost, rport, recv_first))
		proxy_thread.start()

def proxy_handler(client_socket, rhost, rport, recv_first):

	# spawn socket to connect to target
	#remote_socket = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
	remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	remote_socket.connect((rhost, rport))

	# receive data from remote end if necessary
	if recv_first:
		remote_buffer = receive_from(remote_socket)
		hexdump(remote_buffer)

		# send to response handler and then to client
		remote_buffer = response_handler(remote_buffer)
		if len(remote_buffer):
			print "[<] Sending %d bytes to localhost" % len(remote_buffer)
			client_socket.send(remote_buffer)

	# read local, send remote, read remote, send local
	while True:

		# read local
		local_buffer = receive_from(client_socket)
		if (len(local_buffer)):
			print "[>] Received %d bytes from localhost" % len(local_buffer)
			hexdump(local_buffer)
			local_buffer = request_handler(local_buffer)
			# send remote
			remote_socket.send(local_buffer)
			print "[>] Sent to remote"

		# read remote
		remote_buffer = receive_from(remote_socket)
		if (len(remote_buffer)):
			print "[>] Received %d bytes from %s:%d" % (len(remote_buffer), rhost, rport)
			hexdump(remote_buffer)
			remote_buffer = response_handler(remote_buffer)
			# send local
			client_socket.send(remote_buffer)
			print "[>] Sent to localhost"

		# close the connection if no more data on either side
		if not len(local_buffer) or not len(remote_buffer):
			client_socket.close()
			remote_socket.close()
			print "[*] Connection closed."
			break

def receive_from(connection, timeout = 2):
	
	response_buffer = ""
	connection.settimeout(2)
	try:
		# keep reading until there's no more data or we time out
		while True:
			data = connection.recv(4096)
			if not data:
				break
			response_buffer += data
	except:
		pass
	return response_buffer

# this is a pretty hex dumping function directly taken from
# the comments here:
# http://code.activestate.com/recipes/142812-hex-dumper/
def hexdump(src, length=16):
	result = []
	digits = 4 if isinstance(src, unicode) else 2
 	for i in xrange(0, len(src), length):
 		s = src[i:i+length]
 		hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
 		text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
 		result.append( b"%04X %-*s %s" % (i, length*(digits + 1), hexa,
 		text) )
 	print b'\n'.join(result)

def request_handler(buffer):
	# perform packet modifications
	return buffer

def response_handler(buffer):
	# perform packet modifications
	return buffer

def main():

	if (len(sys.argv[1:]) != 5):
		print "USAGE: %s [localhost] [localport] [remotehost] [remoteport] [receive_first]" % sys.argv[0]
		sys.exit(1)
	receive_first = ("True" in sys.argv[5])
	server_loop(sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), receive_first)

if __name__ == '__main__':
	main()
