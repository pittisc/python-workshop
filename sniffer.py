import socket
import os
import struct
from ctypes import *

# host to listen on
host = "10.0.0.3"

# IP header
class IP(Structure):
	_fields_ = [
		("ihl", 			c_ubyte, 4),
		("version", 		c_ubyte, 4),
		("tos", 			c_ubyte),
		("len", 			c_ushort),
		("id", 				c_ushort),
		("offset", 			c_ushort),
		("ttl", 			c_ubyte),
		("protocol_num",	c_ubyte),
		("sum", 			c_ushort),
		("src", 			c_ulong),
		("dst", 			c_ulong),
	]

	def __new__(self, socket_buffer=None):
		return self.from_buffer_copy(socket_buffer)

	def __init__(self, socket_buffer=None):

		# map protocol constants to their names
		self.protocol_map = {1:"ICMP", 6:"TCP", 17:"UDP"}

		# human readable IP addresses
		self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
		self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))

		# human readable protocol
		try:
			self.protocol = self.protocol_map[self.protocol_num]
		except:
			self.protocol = str(self.protocol_num)

def main():
	# create a raw socket and bind it to the public interface
	if os.name == "nt":
		socket_protocol = socket.IPPROTO_IP
	else:
		socket_protocol = socket.IPPROTO_ICMP

	sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

	sniffer.bind((host, 0))

	# we want the IP headers included in the capture
	sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

	# if we're using Windows, we need to send an IOCTL
	# to set up promiscuous mode
	if os.name == "nt":
		sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

	# read in twenty packets
	try:
		while True:
			raw_buffer = sniffer.recvfrom(65565)[0]
			ip_header = IP(raw_buffer[:20])
			print "Protocol: %s %s -> %s" % (ip_header.protocol, 
											 ip_header.src_address,
											 ip_header.dst_address)
	except KeyboardInterrupt:
		if os.name == "nt":
			sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

	# if we're using Windows, turn off promiscuous mode
	if os.name == "nt":
		sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

if __name__ == "__main__":
	main()