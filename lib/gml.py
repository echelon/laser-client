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
from lib.svg import *
from lib.system import *
from lib.shape import Shape
from lib.importObj import importObj

def load_gml(filename, initMulX=80000, initMulY=80000,
			initTheta=math.pi/2):

	def getGml(fn):
		f = open(fn, 'r')
		g = PyGML.GML(f)
		f.close()
		return g

	gml = getGml(filename)

	allPts = []
	strokes = []

	t = initTheta

	for stroke in gml.iterStrokes():
		strokePts = []
		for pt in stroke.iterPoints():

			x = pt.x * initMulX
			y = pt.y * initMulY

			xx = x
			yy = y

			x = xx*math.cos(t) - \
					yy*math.sin(t)
			y = yy*math.cos(t) + \
					xx*math.sin(t)

			pt = {'x': int(x), 'y': int(y)}

			allPts.append(pt)
			strokePts.append(pt)

		strokes.append(strokePts)

	# Normalize points to center
	xsum = 0
	ysum = 0
	for c in allPts:
		xsum += c['x']
		ysum += c['y']

	xavg = xsum / len(allPts)
	yavg = ysum / len(allPts)

	# Normalize strokes
	for i in range(len(strokes)):
		for j in range(len(strokes[i])):
			strokes[i][j]['x'] -= xavg
			strokes[i][j]['y'] -= yavg

	# Create stroke objects
	gmlStrokes = []
	for stroke in strokes:
		s = GmlStroke(points=stroke)
		gmlStrokes.append(s)

	return Gml(strokes=gmlStrokes)

class Gml(Shape):
	"""
	A cross between SHAPE and STREAM.
	Manages several SvgPath(Shape) objects in a Stream.
	"""

	def __init__(self, strokes,
			x = 0, y = 0,
			r = CMAX, g = CMAX, b = CMAX):
		super(Gml, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		# Remove these? XXX
		self.showBlanking = False
		self.showTracking = False
		self.blankingSamplePts = 10
		self.trackingSamplePts = 10

		self.objects = strokes # [Stroke]s

		self.theta = 0
		self.thetaRate = 0
		self.scale = 1.0
		self.scaleX = None
		self.scaleY = None
		self.jitter = True

		self.drawEvery = 1
		self.drawIndex = 1

		self.skip = 0

		self.flipX = False
		self.flipY = False

	def setScaleIndep(self, x=1.0, y=1.0):
		self.scaleX = x
		self.scaleY = y

	def setColor(self, r=CMAX, g=CMAX, b=CMAX):
		"""
		Mutuator to set color for all SvgPaths.
		"""
		for obj in self.objects:
			obj.r = r
			obj.g = g
			obj.b = b

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		# Obect skipping algo
		self.drawIndex = (self.drawIndex+1) % self.drawEvery

		doDraw = True
		if not self.drawIndex in [0, 1]:
			doDraw = False

		if not doDraw:
			self.drawn = True
			return

		i = 0
		for stroke in self.objects:
			if self.skip:
				i += 1
				if i % self.skip == 0:
					continue

			# FIXME: Hugely inefficient
			# TODO: Enforce use of accessor/mutator
			stroke.scale = self.scale
			stroke.scaleX = self.scaleX
			stroke.scaleY = self.scaleY
			stroke.theta = self.theta
			stroke.flipX = self.flipX
			stroke.flipY = self.flipY
			stroke.x = self.x
			stroke.y = self.y

			# TODO: Actual drawing and blanking!!
			#yield(int(x), int(y), self.r, self.g, self.b)

		#print "POINT STREAM LOOP BEGIN"
		curObj = None # XXX SCOPE HERE FOR DEBUG ONLY
		nextObj = None # XXX SCOPE HERE FOR DEBUG 
		reverse = False

		# XXX: Memory copy for opencv app
		objects = self.objects[:]

		# Reverse heuristic
		reverse = not reverse
		if reverse:
			objects.reverse()

		# Generate and cache the first points of the
		# objects. Necessary in order to slow down 
		# galvo tracking as we move to the next object.

		for b in objects:
			b.cacheFirstPt()

		# Objects to destroy at end of loop
		# TODO: Move this outside of object. 
		# TODO: Not PointStream's job
		destroy = []

		# Draw all the objects... 
		for i in range(len(objects)):
			curObj = objects[i]
			nextObj = objects[(i+1)%len(objects)]

			# Skip draw?
			if curObj.skipDraw:
				continue

			# Prepare to cull object if it is marked destroy
			# TODO: Move this outside of object. 
			# TODO: Not PointStream's job
			if curObj.destroy:
				destroy.append(i)

			# FIXME: This is done twice for all firstPts
			# Once here, twice for tracking to nextObj
			#firstPt = self.transform(curObj.firstPt)
			firstPt = curObj.firstPt

			# Blanking (on the way in), if set
			if curObj.doBlanking:
				p = firstPt
				p = (p[0], p[1], 0, 0, 0)
				# If we want to debug the blanking 
				if self.showBlanking:
					p = (p[0], p[1], _CMAX, 0, _CMAX)
				for x in range(self.blankingSamplePts):
					yield p

			# Draw the object
			lastPt = (0, 0, 0, 0, 0)
			if not curObj.drawn:
				# XXX: This was cached upfront!
				yield firstPt
				for pt in curObj.produce():
					#lastPt = self.transform(pt)
					lastPt = pt
					yield lastPt

			# Blanking (on the way out), if set
			if curObj.doBlanking:
				p = lastPt
				p = (p[0], p[1], 0, 0, 0)
				# If we want to debug the blanking 
				if self.showBlanking:
					p = (p[0], p[1], _CMAX, 0, _CMAX)
				for x in range(self.blankingSamplePts):
					yield p

			# Now, track to the next object. 
			# FIXME: inefficient
			# FIXME: nextObj.firstPt transformed 2x!
			#nextFirstPt = self.transform(nextObj.firstPt)
			nextFirstPt = nextObj.firstPt
			lastX = lastPt[0]
			lastY = lastPt[1]
			xDiff = lastPt[0] - nextFirstPt[0]
			yDiff = lastPt[1] - nextFirstPt[1]

			mv = self.trackingSamplePts
			for i in xrange(mv):
				percent = i/float(mv)
				xb = int(lastX - xDiff*percent)
				yb = int(lastY - yDiff*percent)
				# If we want to debug the tracking path 
				if self.showTracking:
					yield (xb, yb, 0, _CMAX, 0)
				else:
					yield (xb, yb, 0, 0, 0)

		# Reset object state (nasty hack for point caching)
		for b in objects:
			b.drawn = False

		# Items to destroy
		# TODO: Move this outside of object. 
		# TODO: Not PointStream's job
		destroy.sort()
		destroy.reverse()
		for i in destroy:
			objects.pop(i)

		self.drawn = True

class GmlStroke(Shape):

	def __init__(self, points,
			x = 0, y = 0, r = CMAX, g = CMAX, b = CMAX,
			initMulX = 30000, initMulY = 30000):

		super(GmlStroke, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0
		self.scale = 1.0
		self.jitter = True

		# Points in the stroke
		self.points = points

	def produce(self):
		for pt in self.points:
			x = pt['x']
			y = pt['y']
			yield (x, y, self.r, self.g, self.b)

		self.drawn = True

class Graffiti2(Shape):

	def __init__(self, x = 0, y = 0, r = 0, g = 0, b = 0,
			filename=None, initTheta=math.pi,
			initMulX = 30000, initMulY = 30000):

		super(Graffiti2, self).__init__(x, y, r, g, b)

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

