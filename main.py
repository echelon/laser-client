#!/usr/bin/env python

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



"""
CONFIGURATION
"""

LASER_POWER_DENOM = 1.0

"""
Globals
"""

objs = []
obj = None
ps = None


"""
Animation code / logic
"""

class SvgPath(Shape):

	def __init__(self, x = 0, y = 0,
			r = 0, g = 0, b = 0, coords=None):
		super(SvgPath, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

		self.coords = coords

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
			x = c['x'] * self.scale;
			y = c['y'] * self.scale;

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

class Svg(Shape):

	def __init__(self, x = 0, y = 0,
			r = 0, g = 0, b = 0, cords=None):
		super(Svg, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		"""
		for c in self.cords:
			x = math.floor(float(c['x']) * 10)
			y = math.floor(float(c['y']) * 10)
			print x, y

			#yield(0, 0, CMAX, CMAX, CMAX)
			yield(int(x), int(y), CMAX, CMAX, CMAX)
		"""

		for i in range(len(OBJECTS)): #obj in OBJECTS:
			obj = OBJECTS[i]
			for pt in obj:
				x = math.floor(pt['x'] * 20)
				y = math.floor(pt['y'] * 20)
				yield(int(x), int(y), CMAX, CMAX, CMAX)



		self.drawn = True

def dac_thread():
	global objs
	global ps

	for obj in objs:
		ps.objects.append(obj)

	while True:
		try:
			d = dac.DAC(dac.find_first_dac())
			d.play_stream(ps)

		except KeyboardInterrupt:
			sys.exit()

		except Exception as e:
			import sys, traceback
			print '\n---------------------'
			print 'Exception: %s' % e
			print '- - - - - - - - - - -'
			traceback.print_tb(sys.exc_info()[2])
			print "\n"

SHOW = None

class NameAnimation(Animation):
	"""
	Loribell's businessname text
	"""
	def setup(self):
		from objs.threshold_logo_filled_trunked import OBJECTS
		from objs.threshold_logo_filled_trunked import ADD_X
		from objs.threshold_logo_filled_trunked import ADD_Y
		from objs.threshold_logo_filled_trunked import MULT_X
		from objs.threshold_logo_filled_trunked import MULT_Y

		#ps.blankingSamplePts = 12 # TODO TODO TODO
		#ps.trackingSamplePts = 12 # TODO TODO TODO

		for i in range(len(OBJECTS)):
			coords = OBJECTS[i]

			# Normalize/fix coordinate system
			for j in range(len(coords)):
				c = coords[j]
				x = math.floor(float(c['x'])*MULT_X) + ADD_X
				y = math.floor(float(c['y'])*MULT_Y) + ADD_Y
				coords[j] = {'x': x, 'y': y};

			#if random.randint(0, 1) == 0:
			#	continue

			OBJECTS[i] = coords

			letter = LbLetter(coords=coords)
			letter.turn = True if random.randint(0, 1) \
							else False

			self.objects.append(letter)

			print "Test"

#
# Start Threads
#

def main():
	global SHOW
	global objs
	global ps

	ps = PointStream()
	#ps.showBlanking = True
	#ps.showTracking = True
	ps.blankingSamplePts = 12
	ps.trackingSamplePts = 12


	SHOW = Show()
	anim = NameAnimation()
	objs = anim.objects

	thread.start_new_thread(dac_thread, ())
	time.sleep(1.0)
	#thread.start_new_thread(spin_thread, ())

	while True:
		time.sleep(100000)

if __name__ == '__main__':
	main()