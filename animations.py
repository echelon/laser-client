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

from objects import *

class NameAnimation(Animation):
	SCALE_MAX = 1.5
	SCALE_MIN = 0.5

	"""
	Loribell's businessname text
	"""
	def setup(self):
		self.hasAnimationThread = True
		self.scale = 1.0
		self.scaleDirec = True

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


	def animThreadFunc(self):
		scale = self.scale
		if self.scaleDirec:
			scale += 0.05
		else:
			scale -= 0.05

		if scale <= NameAnimation.SCALE_MIN:
			scale = NameAnimation.SCALE_MIN
			self.scaleDirec = True

		elif scale >= NameAnimation.SCALE_MAX:
			scale = NameAnimation.SCALE_MAX
			self.scaleDirec = False

		self.scale = scale

		for obj in self.objects:
			obj.scale = scale

class AwesomeAnimation(Animation):
	"""
	Awesome face animation
	"""
	def setup(self):
		from objs.awesome import OBJECTS
		from objs.awesome import ADD_X
		from objs.awesome import ADD_Y
		from objs.awesome import MULT_X
		from objs.awesome import MULT_Y

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

			OBJECTS[i] = coords
			obj = SvgPath(coords=coords)
			self.objects.append(obj)


