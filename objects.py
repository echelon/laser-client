import os
import math
import random
import itertools
import sys
import time
import thread

from lib import dac
from lib.common import *
from lib.stream import PointStream
from lib.system import *
from lib.shape import Shape

class SvgPath(Shape):

	def __init__(self, x = 0, y = 0,
			r = 0, g = 0, b = 0, coords=None):
		super(SvgPath, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.coords = coords

		self.theta = 0
		self.thetaRate = 0
		self.scale = 1.0
		self.jitter = True

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		for c in self.coords:
			if self.jitter and random.randint(0, 2) == 0:
				continue

			# Scale
			x = c['x'] * self.scale;
			y = c['y'] * self.scale;

			# Rotate
			xx = x
			yy = y
			x = xx*math.cos(self.theta) - yy*math.sin(self.theta)
			y = yy*math.cos(self.theta) + xx*math.sin(self.theta)

			# Translate
			x += self.x
			y += self.y

			yield(int(x), int(y), CMAX, CMAX, CMAX)

		self.drawn = True

class LbLetter(SvgPath):
	def __init__(self, x=0, y=0, r=0, g=0, b=0, coords=None):
		super(LbLetter, self).__init__(x, y, r, g, b, coords)

		self.turn = True

	def produce(self):
		if self.turn or True:
			return super(LbLetter, self).produce()
		else:
			return (0, 0, 0, 0, 0)

		self.turn = not self.turn
		self.drawn = True


