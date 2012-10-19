import os
import math
import random
import itertools
import sys
import time
import thread

# Graffiti Markup Language
import PyGML

from lib import dac
from lib.common import *
from lib.stream import PointStream
from lib.system import *
from lib.shape import Shape

class Graffiti(Shape):

	def __init__(self, x = 0, y = 0, r = 0, g = 0, b = 0,
			filename=None, initTheta=0,
			initMulX = 30000, initMulY = 30000):

		super(Graffiti, self).__init__(x, y, r, g, b)

		def getGml(fn):
			f = open(fn, 'r')
			g = PyGML.GML(f)
			f.close()
			return g

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.gml = getGml(filename)

		self.theta = 0
		self.thetaRate = 0
		self.scale = 1.0
		self.jitter = True

		# Applied at import only
		t = initTheta

		# Cache Points
		self.points = []
		for stroke in self.gml.iterStrokes():
			for pt in stroke.iterPoints():

				x = pt.x * initMulX
				y = pt.y * initMulY

				xx = x
				yy = y

				x = xx*math.cos(t) - \
						yy*math.sin(t)
				y = yy*math.cos(t) + \
						xx*math.sin(t)

				self.points.append({'x': x, 'y': y})

		# Normalize points to center
		xsum = 0
		ysum = 0
		for c in self.points:
			xsum += c['x']
			ysum += c['y']

		xavg = xsum / len(self.points)
		yavg = ysum / len(self.points)

		for i in range(len(self.points)):
			self.points[i]['x'] -= xavg
			self.points[i]['y'] -= yavg


	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		for pt in self.points:
			x = pt['x']
			y = pt['y']

			yield (x, y, CMAX, CMAX, CMAX/4)

		self.drawn = True

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
			x = xx*math.cos(self.theta) - \
					yy*math.sin(self.theta)
			y = yy*math.cos(self.theta) + \
					xx*math.sin(self.theta)

			# Translate
			x += self.x
			y += self.y

			yield(int(x), int(y), CMAX, CMAX, CMAX)

		self.drawn = True

