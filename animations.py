import os
import math
import random
import itertools
import sys
import time
import thread
import copy
from datetime import datetime

from lib import dac
from lib.common import *
from lib.stream import PointStream
from lib.system import *
from lib.shape import Shape
from lib.svg import *
from lib.importObj import importObj

from objects import *

"""
OBJS FROM SVG
"""

class ObjectAnimation(Animation):
	"""
	Imports a script containing points.
	VERY crude.
	"""

	def __init__(self, objName, init = None, anim = None,
			r=CMAX, g=CMAX, b=CMAX):

		self.objName = objName

		self.initParams = init
		self.animParams = anim

		self.r = r
		self.g = g
		self.b = b

		self.timeLast = datetime.now() # For timedelta

		self.scaleX = 1.0
		self.scaleY = 1.0
		self.scaleDirecX = True
		self.scaleDirecY = True

		self.rotate = 0.0
		self.rotateDirec = True

		super(ObjectAnimation, self).__init__()

	def setup(self):
		# FIXME: Definitely a better way to do this...
		exec "from objs.%s import OBJECTS" % self.objName
		exec "from objs.%s import MULT_X" % self.objName
		exec "from objs.%s import MULT_Y" % self.objName

		self.hasAnimationThread = False if not \
				self.animParams else True

		self.blankingSamplePts = 7
		self.trackingSamplePts = 15

		obj = load_svg(self.objName)
		self.objects.append(obj)

	def animThreadFunc(self):
		ap = self.animParams

		if not self.timeLast:
			self.timeLast = datetime.now()

		last = self.timeLast
		now = datetime.now()

		delta = now - last
		delta = delta.microseconds / float(10**3)

		if 'scale' in ap and ap['scale']:
			scaleMinX = 0.0
			scaleMaxX = 0.0
			scaleMinY = 0.0
			scaleMaxY = 0.0
			scaleRateX = 0.0
			scaleRateY = 0.0

			# Specify dimensions together?
			# TODO: Extremely flexible assignment
			if 'scaleMin' in ap:
				scaleMinX = ap['scaleMin']
				scaleMinY = ap['scaleMin']
				scaleMaxX = ap['scaleMax']
				scaleMaxY = ap['scaleMax']

			else:
				scaleMinX = ap['scaleMinX']
				scaleMinY = ap['scaleMinY']
				scaleMaxX = ap['scaleMaxX']
				scaleMaxY = ap['scaleMaxY']

			if 'scaleRate' in ap:
				scaleRateX = ap['scaleRate']
				scaleRateY = ap['scaleRate']

			else:
				scaleRateX = ap['scaleRateX']
				scaleRateY = ap['scaleRateY']

			# Do scale animation

			scaleX = self.scaleX
			scaleY = self.scaleY

			if self.scaleDirecX:
				scaleX += scaleRateX * delta
			else:
				scaleX -= scaleRateX * delta

			if self.scaleDirecY:
				scaleY += scaleRateY * delta
			else:
				scaleY -= scaleRateY * delta

			if scaleX <= scaleMinX:
				scaleX = scaleMinX
				self.scaleDirecX = True
			elif scaleX >= scaleMaxX:
				scaleX = scaleMaxX
				self.scaleDirecX = False

			if scaleY <= scaleMinY:
				scaleY = scaleMinY
				self.scaleDirecY = True
			elif scaleY >= scaleMaxY:
				scaleY = scaleMaxY
				self.scaleDirecY = False

			self.scaleX = scaleX
			self.scaleY = scaleY

			for obj in self.objects:
				obj.scaleX = scaleX
				obj.scaleY = scaleY


		if 'rotate' in ap and ap['rotate']:
			rotate = self.rotate
			rotateRate = ap['rotateRate']
			rotateMax = 0.0
			rotateMin = 0.0
			rotateLimits = False

			if 'rotateMag' in ap:
				rotateLimits = True
				rotateMax = ap['rotateMag']
				rotateMin = -ap['rotateMag']
			elif 'rotateMin' in ap:
				rotateLimits = True
				rotateMax = ap['rotateMax']
				rotateMin = ap['rotateMin']

			if not rotateLimits:
				rotate += rotateRate * delta

			else:
				if self.rotateDirec:
					rotate += rotateRate * delta
				else:
					rotate -= rotateRate * delta

				if rotate <= rotateMin:
					rotate = rotateMin
					self.rotateDirec = True
				elif rotate >= rotateMax:
					rotate = rotateMax
					self.rotateDirec = False

			self.rotate = rotate

			for obj in self.objects:
				obj.theta = rotate

		if 'scale_x_mag' in ap:
			scaleX = self.scaleX
			if self.scaleDirecX:
				scaleX += ap['scale_x_rate'] * delta
			else:
				scaleX -= ap['scale_x_rate'] * delta

			if scaleX <= -ap['scale_x_mag']:
				scaleX = -ap['scale_x_mag']
				self.scaleDirecX = True

			elif scaleX >= ap['scale_x_mag']:
				scaleX = ap['scale_x_mag']
				self.scaleDirecX = False

			self.scaleX = scaleX

			for obj in self.objects:
				obj.scaleX = scaleX

		if 'scale_y_mag' in ap:
			scaleY = self.scaleY
			if self.scaleDirecY:
				scaleY += ap['scale_y_rate'] * delta
			else:
				scaleY -= ap['scale_y_rate'] * delta

			if scaleY <= -ap['scale_y_mag']:
				scaleY = -ap['scale_y_mag']
				self.scaleDirecY = True

			elif scaleY >= ap['scale_y_mag']:
				scaleY = ap['scale_y_mag']
				self.scaleDirecY = False

			self.scaleY = scaleY

			for obj in self.objects:
				obj.scaleY = scaleY

		self.timeLast = datetime.now()

class SquareAnimation(Animation):

	def setup(self):

		self.hasAnimationThread = True
		self.scale = 1.0
		self.scaleDirec = True

		self.blankingSamplePts = 12
		self.trackingSamplePts = 12

		# OLD
		self.inc = True
		self.panInc = True
		self.xPan = 0
		self.spin = 0

		self.square = Square()
		self.objects.append(self.square)

	def animThreadFunc(self):
		SQUARE_RADIUS_MIN = 4000
		SQUARE_RADIUS_MAX = 12000
		SQUARE_RADIUS_INC = 50

		PAN_X_INC_MAG = 500
		PAN_X_MAX = 23000
		PAN_X_MIN = -23000

		SPIN_THETA_INC = math.pi / 40

		# Edgelen
		r = self.square.edge
		if r > SQUARE_RADIUS_MAX:
			self.inc = False
		elif r < SQUARE_RADIUS_MIN:
			self.inc = True

		if self.inc:
			r += SQUARE_RADIUS_INC
		else:
			r -= SQUARE_RADIUS_INC

		self.square.edge = r

		# PAN
		if self.xPan > PAN_X_MAX:
			self.panInc = False
		elif self.xPan < PAN_X_MIN:
			self.panInc = True

		if self.panInc:
			self.xPan += PAN_X_INC_MAG
			self.spin = -SPIN_THETA_INC
		else:
			self.xPan -= PAN_X_INC_MAG
			self.spin = SPIN_THETA_INC

		self.square.x = self.xPan
		self.square.theta += self.spin

class BatAnimation(Animation):

	SCALE_MAX = 3.0
	SCALE_MIN = 1.5
	SCALE_RATE = 0.01

	TILT_THETA_MAX = 0.4
	TILT_THETA_MIN = -0.4
	TILT_THETA_RATE = 0.01

	EDGE_X = 27000
	EDGE_Y = 10000
	EDGE_Y_MIN = -1000

	VEL_MAG_MIN = 200
	VEL_MAG_MAX = 500

	def setup(self):

		def importBat():
			from objs.bat2 import OBJECTS
			from objs.bat2 import MULT_X
			from objs.bat2 import MULT_Y

			objCoords = importObj(OBJECTS,
					MULT_X/3.0, MULT_Y/3.0)

			coords = objCoords[0]

			obj = SvgPath(coords=coords)
			obj.jitter = False
			return obj


		self.hasAnimationThread = True
		self.scale = self.SCALE_MIN
		self.scaleDirec = True
		self.theta = 1.0
		self.thetaDirec = True

		self.blankingSamplePts = 10
		self.trackingSamplePts = 10

		bat = importBat()
		for i in range(4):
			obj = copy.copy(bat)
			obj.x = random.randint(-5000, 5000)
			obj.y = random.randint(-5000, 5000)

			obj.xVel = random.randint(self.VEL_MAG_MIN,
					self.VEL_MAG_MAX)
			obj.xVel *= 1 if random.randint(0, 1) else -1

			obj.yVel = random.randint(self.VEL_MAG_MIN,
					self.VEL_MAG_MAX)
			obj.yVel *= 1 if random.randint(0, 1) else -1

			obj.scale = random.randint(15, 35) / float(10)
			obj.scaleVel = random.randint(1, 6) / float(100)
			obj.thetaVel = random.randint(3, 6) / float(100)

			if i % 4 == 0:
				obj.g = 0
			elif i % 4 == 1:
				obj.b = 0

			self.objects.append(obj)

	def animThreadFunc(self):
		for obj in self.objects:
			obj.x += obj.xVel
			obj.y += obj.yVel

			if obj.x >= self.EDGE_X:
				obj.x = self.EDGE_X
				obj.xVel = -random.randint(self.VEL_MAG_MIN,
										self.VEL_MAG_MAX)
			elif obj.x <= -self.EDGE_X:
				obj.x = -self.EDGE_X
				obj.xVel = random.randint(self.VEL_MAG_MIN,
										self.VEL_MAG_MAX)

			if obj.y >= self.EDGE_Y:
				obj.y = self.EDGE_Y
				obj.yVel = -random.randint(self.VEL_MAG_MIN,
										self.VEL_MAG_MAX)
			elif obj.y <= self.EDGE_Y_MIN:
				obj.y = self.EDGE_Y_MIN
				obj.yVel = random.randint(self.VEL_MAG_MIN,
										self.VEL_MAG_MAX)

			obj.theta += obj.thetaVel
			obj.scale += obj.scaleVel

			if obj.theta >= self.TILT_THETA_MAX:
				obj.theta = self.TILT_THETA_MAX
				obj.thetaVel *= -1
			elif obj.theta <= -self.TILT_THETA_MAX:
				obj.theta = -self.TILT_THETA_MAX
				obj.thetaVel *= -1

			if obj.scale >= self.SCALE_MAX:
				obj.scale = self.SCALE_MAX
				#obj.scaleVel = -self.SCALE_RATE
				obj.scaleVel *= -1
			elif obj.scale <= self.SCALE_MIN:
				obj.scale = self.SCALE_MIN
				#obj.scaleVel = self.SCALE_RATE
				obj.scaleVel *= -1

class ShamrockAnimation(Animation):

	SCALE_MAX = 3.0
	SCALE_MIN = 1.5
	#SCALE_RATE = 0 #0.00001

	TILT_THETA_MAX = 0.4
	TILT_THETA_MIN = -0.4
	#TILT_THETA_RATE = 0 #0.0001

	EDGE_X = 27000
	EDGE_Y_MAX = 7000
	EDGE_Y_MIN = 0

	VEL_MAG_MIN = 7
	VEL_MAG_MAX = 15

	def setup(self):

		def importBat():
			from objs.shamrock import OBJECTS
			from objs.shamrock import MULT_X
			from objs.shamrock import MULT_Y

			objCoords = importObj(OBJECTS,
					MULT_X/3.0, MULT_Y/3.0)

			coords = objCoords[0]

			obj = SvgPath(coords=coords)
			obj.jitter = False
			return obj

		self.timeLast = datetime.now() # For timedelta

		self.hasAnimationThread = True
		self.scale = self.SCALE_MIN
		self.scaleDirec = True
		self.theta = 1.0
		self.thetaDirec = True

		self.blankingSamplePts = 10
		self.trackingSamplePts = 10

		bat = importBat()
		for i in range(3):
			obj = copy.copy(bat)
			obj.x = random.randint(-5000, 5000)
			obj.y = random.randint(-5000, 5000)

			obj.xVel = random.randint(self.VEL_MAG_MIN,
					self.VEL_MAG_MAX)
			obj.xVel *= 1 if random.randint(0, 1) else -1

			obj.yVel = random.randint(self.VEL_MAG_MIN,
					self.VEL_MAG_MAX)
			obj.yVel *= 1 if random.randint(0, 1) else -1

			obj.scale = random.randint(15, 35) / float(10)
			obj.scaleVel = random.randint(1, 4) / float(1000)
			obj.thetaVel = random.randint(1, 3) / float(1000)

			if i % 2 == 0:
				obj.b = 0
			else:
				obj.g = 0

			self.objects.append(obj)

	def animThreadFunc(self):

		if not self.timeLast:
			self.timeLast = datetime.now()

		last = self.timeLast
		now = datetime.now()

		delta = now - last
		delta = delta.microseconds / float(10**3)

		for obj in self.objects:
			obj.x += obj.xVel * delta
			obj.y += obj.yVel * delta

			if obj.x >= self.EDGE_X:
				obj.x = self.EDGE_X
				obj.xVel = -random.randint(self.VEL_MAG_MIN,
										self.VEL_MAG_MAX)
			elif obj.x <= -self.EDGE_X:
				obj.x = -self.EDGE_X
				obj.xVel = random.randint(self.VEL_MAG_MIN,
										self.VEL_MAG_MAX)

			if obj.y >= self.EDGE_Y_MAX:
				obj.y = self.EDGE_Y_MAX
				obj.yVel = -random.randint(self.VEL_MAG_MIN,
										self.VEL_MAG_MAX)
			elif obj.y <= self.EDGE_Y_MIN:
				obj.y = self.EDGE_Y_MIN
				obj.yVel = random.randint(self.VEL_MAG_MIN,
										self.VEL_MAG_MAX)

			obj.theta += obj.thetaVel * delta
			obj.scale += obj.scaleVel * delta

			if obj.theta >= self.TILT_THETA_MAX:
				obj.theta = self.TILT_THETA_MAX
				obj.thetaVel *= -1
			elif obj.theta <= -self.TILT_THETA_MAX:
				obj.theta = -self.TILT_THETA_MAX
				obj.thetaVel *= -1

			if obj.scale >= self.SCALE_MAX:
				obj.scale = self.SCALE_MAX
				#obj.scaleVel = -self.SCALE_RATE
				obj.scaleVel *= -1
			elif obj.scale <= self.SCALE_MIN:
				obj.scale = self.SCALE_MIN
				#obj.scaleVel = self.SCALE_RATE
				obj.scaleVel *= -1

		self.timeLast = datetime.now() # For timedelta

class ShamrockAnimation(Animation):

	SCALE_MAX = 3.0
	SCALE_MIN = 1.5
	#SCALE_RATE = 0 #0.00001

	TILT_THETA_MAX = 0.4
	TILT_THETA_MIN = -0.4
	#TILT_THETA_RATE = 0 #0.0001

	EDGE_X = 27000
	EDGE_Y_MAX = 7000
	EDGE_Y_MIN = 0

	VEL_MAG_MIN = 7
	VEL_MAG_MAX = 15

	def setup(self):

		def importBat():
			from objs.shamrock import OBJECTS
			from objs.shamrock import MULT_X
			from objs.shamrock import MULT_Y

			objCoords = importObj(OBJECTS,
					MULT_X/3.0, MULT_Y/3.0)

			coords = objCoords[0]

			obj = SvgPath(coords=coords)
			obj.jitter = False
			return obj

		self.timeLast = datetime.now() # For timedelta

		self.hasAnimationThread = True
		self.scale = self.SCALE_MIN
		self.scaleDirec = True
		self.theta = 1.0
		self.thetaDirec = True

		self.blankingSamplePts = 10
		self.trackingSamplePts = 10

		bat = importBat()
		for i in range(3):
			obj = copy.copy(bat)
			obj.x = random.randint(-5000, 5000)
			obj.y = random.randint(-5000, 5000)

			obj.xVel = random.randint(self.VEL_MAG_MIN,
					self.VEL_MAG_MAX)
			obj.xVel *= 1 if random.randint(0, 1) else -1

			obj.yVel = random.randint(self.VEL_MAG_MIN,
					self.VEL_MAG_MAX)
			obj.yVel *= 1 if random.randint(0, 1) else -1

			obj.scale = random.randint(15, 35) / float(10)
			obj.scaleVel = random.randint(1, 4) / float(1000)
			obj.thetaVel = random.randint(1, 3) / float(1000)

			if i % 2 == 0:
				obj.b = 0
			else:
				obj.g = 0

			self.objects.append(obj)

	def animThreadFunc(self):

		if not self.timeLast:
			self.timeLast = datetime.now()

		last = self.timeLast
		now = datetime.now()

		delta = now - last
		delta = delta.microseconds / float(10**3)

		for obj in self.objects:
			obj.x += obj.xVel * delta
			obj.y += obj.yVel * delta

			if obj.x >= self.EDGE_X:
				obj.x = self.EDGE_X
				obj.xVel = -random.randint(self.VEL_MAG_MIN,
										self.VEL_MAG_MAX)
			elif obj.x <= -self.EDGE_X:
				obj.x = -self.EDGE_X
				obj.xVel = random.randint(self.VEL_MAG_MIN,
										self.VEL_MAG_MAX)

			if obj.y >= self.EDGE_Y_MAX:
				obj.y = self.EDGE_Y_MAX
				obj.yVel = -random.randint(self.VEL_MAG_MIN,
										self.VEL_MAG_MAX)
			elif obj.y <= self.EDGE_Y_MIN:
				obj.y = self.EDGE_Y_MIN
				obj.yVel = random.randint(self.VEL_MAG_MIN,
										self.VEL_MAG_MAX)

			obj.theta += obj.thetaVel * delta
			obj.scale += obj.scaleVel * delta

			if obj.theta >= self.TILT_THETA_MAX:
				obj.theta = self.TILT_THETA_MAX
				obj.thetaVel *= -1
			elif obj.theta <= -self.TILT_THETA_MAX:
				obj.theta = -self.TILT_THETA_MAX
				obj.thetaVel *= -1

			if obj.scale >= self.SCALE_MAX:
				obj.scale = self.SCALE_MAX
				#obj.scaleVel = -self.SCALE_RATE
				obj.scaleVel *= -1
			elif obj.scale <= self.SCALE_MIN:
				obj.scale = self.SCALE_MIN
				#obj.scaleVel = self.SCALE_RATE
				obj.scaleVel *= -1

		self.timeLast = datetime.now() # For timedelta


class ArrowAnim(Animation):

	SCALE_MAX = 7.0
	SCALE_MIN = 5.5
	SCALE_RATE = 0.5

	TILT_THETA_MAX = 0.2
	TILT_THETA_MIN = -0.3
	TILT_THETA_RATE = 0.06

	def setup(self):
		from objs.arrow import OBJECTS
		from objs.arrow import MULT_X
		from objs.arrow import MULT_Y

		self.hasAnimationThread = True
		self.scale = self.SCALE_MIN
		self.scaleDirec = True
		self.theta = 1.0
		self.thetaDirec = True

		self.blankingSamplePts = 5
		self.trackingSamplePts = 10

		objCoords = importObj(OBJECTS,
				MULT_X/3.0, MULT_Y/3.0)

		for i in range(len(objCoords)):
			coords = objCoords[i]

			obj = SvgPath(coords=coords)
			obj.jitter = False
			obj.scale = self.scale
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

class HexAnimation(Animation):
	SCALE_MAX = 7.0
	SCALE_MIN = 5.5
	SCALE_RATE = 0.5

	TILT_THETA_MAX = 0.2
	TILT_THETA_MIN = -0.3
	TILT_THETA_RATE = 0.6

	def setup(self):
		from objs.hex import OBJECTS
		from objs.hex import MULT_X
		from objs.hex import MULT_Y

		self.hasAnimationThread = True
		self.scale = self.SCALE_MIN
		self.scaleDirec = True
		self.theta = 1.0
		self.thetaDirec = True

		self.blankingSamplePts = 5
		self.trackingSamplePts = 10

		objCoords = importObj(OBJECTS,
				MULT_X/3.0, MULT_Y/3.0)

		for i in range(len(objCoords)):
			coords = objCoords[i]

			obj = SvgPath(coords=coords)
			obj.jitter = False
			obj.scale = self.scale
			self.objects.append(obj)

	def animThreadFunc(self):
		"""
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
		"""

		#self.theta += self.TILT_THETA_RATE

		for obj in self.objects:
			obj.theta += self.TILT_THETA_RATE

class CostumesAnimation(Animation):

	SCALE_MAX = 4.2
	SCALE_MIN = 3.5
	SCALE_RATE = 0.02

	TILT_THETA_MAX = 0.3
	TILT_THETA_MIN = -0.3
	TILT_THETA_RATE = 0.02

	def setup(self):
		from objs.costumes import OBJECTS
		from objs.costumes import MULT_X
		from objs.costumes import MULT_Y

		self.hasAnimationThread = True
		self.scale = self.SCALE_MIN
		self.scaleDirec = True
		self.theta = 1.0
		self.thetaDirec = True

		self.blankingSamplePts = 5
		self.trackingSamplePts = 12

		objCoords = importObj(OBJECTS,
				MULT_X/3.0, MULT_Y/3.0)

		for i in range(len(objCoords)):
			coords = objCoords[i]

			obj = SvgPath(coords=coords)
			obj.jitter = False
			obj.scale = self.scale
			obj.b = 0
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

class GhostAnimation(Animation):

	SCALE_MAX = 3.0
	SCALE_MIN = 2.8
	SCALE_RATE = 0.04

	TILT_THETA_MAX = 1.0
	TILT_THETA_MIN = 0.2
	TILT_THETA_RATE = 0.04

	EDGE_X = 28000

	EDGE_Y = 22000
	EDGE_Y_MIN = 10000

	VEL_MAG_MIN = 1500
	VEL_MAG_MAX = 2000

	def setup(self):
		from objs.ghost import OBJECTS
		from objs.ghost import MULT_X
		from objs.ghost import MULT_Y

		self.hasAnimationThread = True
		self.scale = self.SCALE_MIN
		self.scaleDirec = True
		self.theta = 1.0
		self.thetaDirec = True

		self.blankingSamplePts = 20
		self.trackingSamplePts = 30

		objCoords = importObj(OBJECTS,
				MULT_X/3.0, MULT_Y/3.0)

		for i in range(len(objCoords)):
			coords = objCoords[i]

			obj = SvgPath(coords=coords)
			obj.jitter = False
			obj.scale = self.scale
			self.objects.append(obj)
			obj.xVel = 600
			obj.yVel = 600

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

		for obj in self.objects:
			obj.x += self.objects[0].xVel
			obj.y += self.objects[0].yVel

		obj = self.objects[0]

		if obj.x >= self.EDGE_X:
			for o in self.objects:
				o.x = self.EDGE_X
				o.xVel = -random.randint(self.VEL_MAG_MIN,
										self.VEL_MAG_MAX)
				o.flipX = True

		elif obj.x <= -self.EDGE_X:
			for o in self.objects:
				o.x = -self.EDGE_X
				o.xVel = random.randint(self.VEL_MAG_MIN,
										self.VEL_MAG_MAX)
				o.flipX = False

		"""
		if obj.y >= self.EDGE_Y:
			for o in self.objects:
				o.y = self.EDGE_Y
				o.yVel = -random.randint(self.VEL_MAG_MIN,
										self.VEL_MAG_MAX)
		elif obj.y <= self.EDGE_Y_MIN:
			for o in self.objects:
				o.y = -self.EDGE_Y_MIN
				o.yVel = random.randint(self.VEL_MAG_MIN,
										self.VEL_MAG_MAX)
		"""

		for o in self.objects:
			o.y = self.EDGE_Y_MIN

class AwesomeAnimation(Animation):
	"""
	Awesome face animation
	"""

	SCALE_MAX = 6.0
	SCALE_MIN = 1.5
	SCALE_RATE = 0.5

	def setup(self):
		from objs.awesome import OBJECTS
		from objs.awesome import MULT_X
		from objs.awesome import MULT_Y

		self.hasAnimationThread = True
		self.scale = self.SCALE_MIN
		self.scaleDirec = True
		self.theta = 1.0
		self.thetaDirec = True

		objCoords = importObj(OBJECTS, MULT_X/3.0, MULT_Y/3.0)

		for i in range(len(objCoords)):
			coords = objCoords[i]

			obj = SvgPath(coords=coords)
			obj.jitter = False
			obj.scale = self.scale
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

class BouncingCardShapesAnim(Animation):

	MAX_X = 27000
	MIN_X = -27000
	MAX_Y = 7000
	MIN_Y = 0

	def __init__(self):

		self.timeLast = datetime.now() # For timedelta

		super(BouncingCardShapesAnim, self).__init__()

	def setup(self):
		self.hasAnimationThread = True
		self.scale = 1.0
		self.theta = 1.0
		self.thetaDirec = True

		self.trackData = [] # Ball velocities, etc.

		# Pseudo-rotation
		self.scaleRateX = 0.002
		self.scaleXs = [-0.5, 0.0, 0.5, 1.0]
		self.scaleDirecX = [True for i in range(4)]

		self.objects.append(load_svg('shapeHeart'))
		self.objects.append(load_svg('shapeDiamond'))
		self.objects.append(load_svg('shapeSpade'))
		self.objects.append(load_svg('shapeClub'))

		self.objects[0].setColor(b=0)
		self.objects[1].setColor(b=0)
		self.objects[2].setColor(g=0)
		self.objects[3].setColor(g=0)

		self.MIN_VEL = 5
		self.MAX_VEL = 40

		for i in range(4):
			r = CMAX
			g = CMAX
			b = CMAX
			if i % 3 == 0:
				g = 0
				b = CMAX
			elif i % 3 == 1:
				g = CMAX
				b = 0

			self.objects[i].scale = 0.5

			self.trackData.append({
				'xAdd': random.randint(self.MIN_VEL, self.MAX_VEL),
				'yAdd': random.randint(self.MIN_VEL, self.MAX_VEL),
				'xDirec': random.randint(0, 1),
				'yDirec': random.randint(0, 1),
			})

	def animThreadFunc(self):
		MIN_VEL = self.MIN_VEL
		MAX_VEL = self.MAX_VEL

		if not self.timeLast:
			self.timeLast = datetime.now()

		last = self.timeLast
		now = datetime.now()

		delta = now - last
		delta2 = delta.microseconds / float(10**6)
		delta = delta.microseconds / float(10**3)

		for i in range(len(self.objects)):
			obj = self.objects[i]
			scaleX = self.scaleXs[i]

			if self.scaleDirecX[i]:
				scaleX += self.scaleRateX * delta
			else:
				scaleX -= self.scaleRateX * delta

			if scaleX <= -1.0:
				scaleX = -1.0
				self.scaleDirecX[i]= True

			elif scaleX >= 1.0:
				scaleX = 1.0
				self.scaleDirecX[i] = False

			self.scaleXs[i] = scaleX
			obj.setScaleIndep(x=scaleX)

		for i in range(4):
			obj = self.objects[i]
			t = self.trackData[i]

			if t['xDirec']:
				obj.x += int(t['xAdd'] * delta)
			else:
				obj.x -= int(t['xAdd'] * delta)

			if t['yDirec']:
				obj.y += int(t['yAdd'] * delta)
			else:
				obj.y -= int(t['yAdd'] * delta)

			if obj.x > self.MAX_X:
				obj.x = self.MAX_X
				t['xDirec'] = 0
				t['xAdd'] = random.randint(MIN_VEL, MAX_VEL)
			elif obj.x < self.MIN_X:
				obj.x = self.MIN_X
				t['xDirec'] = 1
				t['xAdd'] = random.randint(MIN_VEL, MAX_VEL)
			if obj.y > self.MAX_Y:
				obj.y = self.MAX_Y
				t['yDirec'] = 0
				t['yAdd'] = random.randint(MIN_VEL, MAX_VEL)
			elif obj.y < self.MIN_Y:
				obj.y = self.MIN_Y
				t['yDirec'] = 1
				t['yAdd'] = random.randint(MIN_VEL, MAX_VEL)

		self.timeLast = datetime.now() # For timedelta

class MusicAnim(Animation):

	MAX_X = 27000
	MIN_X = -27000
	MAX_Y = 7000
	MIN_Y = 0

	def __init__(self):

		self.timeLast = datetime.now() # For timedelta

		super(MusicAnim, self).__init__()

	def setup(self):
		self.hasAnimationThread = True
		self.scale = 1.0
		self.theta = 1.0
		self.thetaDirec = True

		self.trackData = [] # Ball velocities, etc.

		# Pseudo-rotation
		self.scaleRateX = 0.002
		self.scaleXs = [-0.5, 0.0, 0.5, 1.0]
		self.scaleDirecX = [True for i in range(4)]

		self.objects.append(load_svg('musicNote1'))
		self.objects.append(load_svg('musicNote2'))
		self.objects.append(load_svg('musicNote1'))
		self.objects.append(load_svg('musicNote1'))

		length = self.MAX_X - self.MIN_X
		trav = length / 4

		self.objects[0].x = self.MIN_X
		self.objects[1].x = self.MIN_X + trav
		self.objects[2].x = self.MIN_X + trav*2
		self.objects[3].x = self.MIN_X + trav*3

		self.MIN_VEL = 5
		self.MAX_VEL = 40

		for i in range(4):
			r = CMAX
			g = CMAX
			b = CMAX
			if i % 3 == 0:
				g = 0
				b = CMAX
			elif i % 3 == 1:
				g = CMAX
				b = 0

			self.trackData.append({
				'xAdd': random.randint(self.MIN_VEL, self.MAX_VEL),
				'yAdd': random.randint(self.MIN_VEL, self.MAX_VEL),
				'xDirec': random.randint(0, 1),
				'yDirec': random.randint(0, 1),
			})

	def animThreadFunc(self):
		MIN_VEL = self.MIN_VEL
		MAX_VEL = self.MAX_VEL

		if not self.timeLast:
			self.timeLast = datetime.now()

		last = self.timeLast
		now = datetime.now()

		delta = now - last
		delta2 = delta.microseconds / float(10**6)
		delta = delta.microseconds / float(10**3)

		for i in range(4):
			obj = self.objects[i]
			t = self.trackData[i]

			if t['yDirec']:
				obj.y += int(t['yAdd'] * delta)
			else:
				obj.y -= int(t['yAdd'] * delta)

			if obj.y > self.MAX_Y:
				obj.y = self.MAX_Y
				t['yDirec'] = 0
				t['yAdd'] = random.randint(MIN_VEL, MAX_VEL)
			elif obj.y < self.MIN_Y:
				obj.y = self.MIN_Y
				t['yDirec'] = 1
				t['yAdd'] = random.randint(MIN_VEL, MAX_VEL)

		self.timeLast = datetime.now() # For timedelta

"""
GML
"""

class GmlAnimation(Animation):
	def __init__(self, filename,
			theta=0, mul=20000, mulX=None, mulY=None):

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
	def __init__(self, numBalls=4):
		self.numBalls = numBalls
		super(BouncingBall, self).__init__()

	def setup(self):
		self.hasAnimationThread = True
		self.scale = 1.0
		self.theta = 1.0
		self.thetaDirec = True


		self.trackData = [] # Ball velocities, etc.

		for i in range(self.numBalls):
			r = CMAX
			g = CMAX
			b = CMAX
			if i % 3 == 0:
				g = 0
				b = CMAX
			elif i % 3 == 1:
				g = CMAX
				b = 0

			obj = Circle(r=r, g=g, b=b)
			self.objects.append(obj)

			self.trackData.append({
				'xAdd': random.randint(500, 1000),
				'yAdd': random.randint(500, 1000),
				'xDirec': random.randint(0, 1),
				'yDirec': random.randint(0, 1),
			})

	def animThreadFunc(self):
		MAX_X = 14000
		MIN_X = -14000

		MAX_Y = 7000
		MIN_Y = -7000

		for i in range(self.numBalls):
			obj = self.objects[i]
			t = self.trackData[i]

			if obj.x > MAX_X:
				t['xDirec'] = 0
				t['xAdd'] = random.randint(500, 1000)
			elif obj.x < MIN_X:
				t['xDirec'] = 1
				t['xAdd'] = random.randint(500, 1000)
			if obj.y > MAX_Y:
				t['yDirec'] = 0
				t['yAdd'] = random.randint(500, 1000)
			elif obj.y < MIN_Y:
				t['yDirec'] = 1
				t['yAdd'] = random.randint(500, 1000)

			if t['xDirec']:
				obj.x += t['xAdd']
			else:
				obj.x -= t['xAdd']

			if t['yDirec']:
				obj.y += t['yAdd']
			else:
				obj.y -= t['yAdd']

