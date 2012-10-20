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

		objCoords = importObj(OBJECTS, MULT_X/2.0, MULT_Y/2.0)

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

		objCoords = importObj(OBJECTS, MULT_X/3.0, MULT_Y/3.0)

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

class GmlAnimation(Animation):
	def __init__(self, filename,
			theta=math.pi/2, mul=20000, mulX=None, mulY=None):

		if not mulX or not mulY:
			mulX = mul
			mulY = mul

		self.filename = filename
		self.theta = theta
		self.mulX = mulX
		self.mulY = mulY

		super(GmlAnimation, self).__init__()

	def setup(self):

		#self.hasAnimationThread = True
		#self.scale = 1.0
		#self.theta = 1.0
		#self.thetaDirec = True

		obj = Graffiti(filename=self.filename,
						initTheta = self.theta,
						initMulX = self.mulX,
						initMulY = self.mulY
		)
		self.objects.append(obj)

	def animThreadFunc(self):
		pass

"""
Simple Objects
"""
class BouncingBall(Animation):
	def setup(self):
		self.hasAnimationThread = True
		self.scale = 1.0
		self.theta = 1.0
		self.thetaDirec = True

		obj = Circle()
		self.objects.append(obj)

		self.xAdd = 1000
		self.yAdd = 1000

		self.xDirec = 0
		self.yDirec = 0

	def animThreadFunc(self):
		MAX_X = 14000
		MIN_X = -14000

		MAX_Y = 7000
		MIN_Y = -7000

		obj = self.objects[0]

		if obj.x > MAX_X:
			self.xDirec = 0
			self.xAdd = random.randint(500, 1000)
		elif obj.x < MIN_X:
			self.xDirec = 1
			self.xAdd = random.randint(500, 1000)
		if obj.y > MAX_Y:
			self.yDirec = 0
			self.yAdd = random.randint(500, 1000)
		elif obj.y < MIN_Y:
			self.yDirec = 1
			self.yAdd = random.randint(500, 1000)

		if self.xDirec:
			obj.x += self.xAdd
		else:
			obj.x -= self.xAdd

		if self.yDirec:
			obj.y += self.yAdd
		else:
			obj.y -= self.yAdd

