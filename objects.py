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

"""
Shape systems that import from files, etc.
"""
class Graffiti(Shape):

	def __init__(self, x = 0, y = 0, r = 0, g = 0, b = 0,
			filename=None, initTheta=math.pi,
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
			r = CMAX, g = CMAX, b = CMAX, coords=None):
		super(SvgPath, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.coords = coords

		self.theta = 0
		self.thetaRate = 0
		self.scale = 1.0
		self.jitter = True

		self.drawEvery = 1
		self.drawIndex = 1

		self.skip = 0

		self.flipX = False
		self.flipY = False

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		# Obect skipping algo
		self.drawIndex = (self.drawIndex+1) % self.drawEvery

		doDraw = True
		if not self.drawIndex in [0, 1]:
			doDraw = False

		if not doDraw:
			self.drawn = True
			return

		i = 0
		for c in self.coords:
			if self.jitter and random.randint(0, 2) == 0:
				continue

			if self.skip:
				i += 1
				if i % self.skip == 0:
					continue

			# Scale
			x = c['x'] * self.scale
			y = c['y'] * self.scale

			# Rotate
			xx = x
			yy = y
			x = xx*math.cos(self.theta) - \
					yy*math.sin(self.theta)
			y = yy*math.cos(self.theta) + \
					xx*math.sin(self.theta)

			# Flip
			if self.flipX:
				x *= -1

			if self.flipY:
				y *= -1

			# Translate
			x += self.x
			y += self.y

			yield(int(x), int(y), self.r, self.g, self.b)

		self.drawn = True

"""
Primitive Shapes
"""
class Circle(Shape):
	def __init__(self, x = 0, y = 0,
				r = CMAX, g = CMAX, b = CMAX,
				radius = 82):

		super(Circle, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

		self.radius = radius

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		for i in xrange(0, 40, 1):
			i = float(i) / 40 * 2 * math.pi
			x = int(math.cos(i) * self.radius) + self.x
			y = int(math.sin(i) * self.radius) + self.y
			yield (x, y, self.r, self.g, self.b)

		self.drawn = True

class Square(Shape):
	def __init__(self, x = 0, y = 0,
				r = CMAX, g = CMAX, b = CMAX,
				edge = 8000, sample = 100):

		super(Square, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

		self.edge = edge
		self.sample = sample

	def produce(self):
		r, g, b = (0, 0, 0)
		size = self.edge
		s = self.sample

		class Point(object):
			def __init__(self, x, y):
				self.x = x
				self.y = y

		def line_generator(pt1, pt2, steps=100):
			xdiff = pt1.x - pt2.x
			ydiff = pt1.y - pt2.y
			for i in xrange(0, steps, 1):
				j = float(i)/steps
				x = pt1.x - (xdiff * j)
				y = pt1.y - (ydiff * j)
				yield (x, y, CMAX, CMAX, CMAX)

		a = size/2
		b = -size/2
		v = [
			Point(a, a),
			Point(a, b),
			Point(b, b),
			Point(b, a)
		]

		# Rotate vertices
		for p in v:
			x = p.x
			y = p.y
			p.x = x*math.cos(self.theta) \
					- y*math.sin(self.theta)
			p.y = y*math.cos(self.theta) \
					+ x*math.sin(self.theta)

		# Translate vertices
		for pt in v:
			pt.x += self.x
			pt.y += self.y

		for i in range(4):
			for pt in line_generator(v[i], v[(i+1)%4], s):
				yield pt

		self.drawn = True

