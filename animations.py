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
from lib.importObj import importObj

from objects import *

"""
OBJS FROM SVG
"""

class LogoAnimation(Animation):
	"""
	Loribell's Logo
	"""

	SCALE_MAX = 1.75
	SCALE_MIN = 0.5
	SCALE_RATE = 0.1

	TILT_THETA_MAX = 1.5
	TILT_THETA_MIN = -1.5
	TILT_THETA_RATE = 0.1

	def setup(self):
		from objs.threshold_ice import OBJECTS
		from objs.threshold_ice import MULT_X
		from objs.threshold_ice import MULT_Y

		self.hasAnimationThread = True
		self.scale = 1.0
		self.scaleDirec = True
		self.theta = 1.0
		self.thetaDirec = True

		self.blankingSamplePts = 50
		self.trackingSamplePts = 50

		objCoords = importObj(OBJECTS, MULT_X, MULT_Y)

		for i in range(len(objCoords)):
			coords = objCoords[i]

			obj = SvgPath(coords=coords)
			obj.jitter = False
			self.objects.append(obj)


	def animThreadFunc(self):
		scale = self.scale
		if self.scaleDirec:
			scale += self.SCALE_RATE
		else:
			scale -= self.SCALE_RATE

		if scale <= self.SCALE_MIN:
			scale = self.SCALE_MIN
			self.scaleDirec = True

		elif scale >= self.SCALE_MAX:
			scale = self.SCALE_MAX
			self.scaleDirec = False

		self.scale = scale

		for obj in self.objects:
			obj.scale = scale

		theta = self.theta
		if self.thetaDirec:
			theta += self.TILT_THETA_RATE
		else:
			theta -= self.TILT_THETA_RATE

		if theta <= self.TILT_THETA_MIN:
			theta = self.TILT_THETA_MIN
			self.thetaDirec = True
		elif theta >= self.TILT_THETA_MAX:
			theta = self.TILT_THETA_MAX
			self.thetaDirec = False

		self.theta = theta

		for obj in self.objects:
			obj.theta = theta

class NameAnimation(Animation):
	"""
	Loribell's businessname text
	"""

	SCALE_MAX = 1.75
	SCALE_MIN = 0.5
	SCALE_RATE = 0.1

	def setup(self):
		from objs.threshold_logo_filled_trunked import OBJECTS
		from objs.threshold_logo_filled_trunked import MULT_X
		from objs.threshold_logo_filled_trunked import MULT_Y

		self.hasAnimationThread = True
		self.scale = 1.0
		self.scaleDirec = True

		self.blankingSamplePts = 12
		self.trackingSamplePts = 12

		objCoords = importObj(OBJECTS, MULT_X, MULT_Y)

		for i in range(len(objCoords)):
			coords = objCoords[i]

			obj = SvgPath(coords=coords)
			obj.jitter = False
			self.objects.append(obj)

	def animThreadFunc(self):
		scale = self.scale
		if self.scaleDirec:
			scale += NameAnimation.SCALE_RATE
		else:
			scale -= NameAnimation.SCALE_RATE

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
		from objs.awesome import MULT_X
		from objs.awesome import MULT_Y

		self.hasAnimationThread = True
		self.scale = 1.0
		self.theta = 1.0
		self.thetaDirec = True

		objCoords = importObj(OBJECTS, MULT_X, MULT_Y)

		for i in range(len(objCoords)):
			coords = objCoords[i]

			obj = SvgPath(coords=coords)
			obj.jitter = False
			self.objects.append(obj)

	def animThreadFunc(self):
		theta = self.theta
		if self.thetaDirec:
			theta += self.TILT_THETA_RATE
		else:
			theta -= self.TILT_THETA_RATE

		if theta <= self.TILT_THETA_MIN:
			theta = self.TILT_THETA_MIN
			self.thetaDirec = True
		elif theta >= self.TILT_THETA_MAX:
			theta = self.TILT_THETA_MAX
			self.thetaDirec = False

		self.theta = theta

		for obj in self.objects:
			obj.theta = theta

"""
GML
"""

class HappyAnimation(Animation):
	"""
	Happy Anniversary Text
	"""
	def setup(self):

		#self.hasAnimationThread = True
		#self.scale = 1.0
		#self.theta = 1.0
		#self.thetaDirec = True

		obj = Graffiti(filename='gml/happy.gml',
						initTheta = math.pi/2,
						initMulX = 80000,
						initMulY = 80000
		)
		self.objects.append(obj)

	def animThreadFunc(self):
		pass

