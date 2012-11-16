"""
A fake DAC that can print the point stream.
"""

import dac

class Dac2(dac.DAC):
	def __init__(self):

		class Conn(object):
			def sendall(self, st):
				return ""

			def recv(self, ln):
				return ""

			def readresp(self, st):
				return st

		self.last_status = dac.Status("0"*20)
		self.last_status.playback_state = 0
		self.last_status.fullness = 0
		self.conn = Conn()
		self.buf = ""

	def play_stream(self, stream):
		while True:
			print stream.read(1)

