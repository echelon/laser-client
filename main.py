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
from lib.svg import *
from lib.stream import PointStream
from lib.system import *
from lib.shape import Shape

from animations import *
from objects import *

"""
Configuration
"""
LASER_POWER_DENOM = 1.0 # TODO


"""
Globals
"""
SHOW = None
ps = None

"""
Bootstrap it all! Go, go, go!
"""

# At 9, need 24.
# Wants animated dice...
# Work on 'craft' slide

def addLD(SHOW):
	SHOW.animations.append(BouncingCardShapesAnim())
	SHOW.animations.append(ObjectAnimation('luckydraw'))
	SHOW.animations.append(ObjectAnimation('cardAce',
		init = {
			'theta': 0.1
		},
		anim = {
			'scale_x_mag': 1.0,
			'scale_x_rate': 0.006
		}
	))
	SHOW.animations.append(ObjectAnimation('tattoo'))
	SHOW.animations.append(ObjectAnimation('piercing'))
	SHOW.animations.append(ObjectAnimation('ldlogo',
		anim = {
			'rotate': True,
			'rotateRate': 0.002,
		}
	))

def addMC(SHOW):
	return
	SHOW.animations.append(
			ObjectAnimation('maccrackens', b=0,
		anim = {
			'scale': True,
			'scaleRate': 0.001,
			'scaleMin': 0.5,
			'scaleMax': 1.6,
		}
	))
	SHOW.animations.append(ShamrockAnimation())
	SHOW.animations.append(
			ObjectAnimation('craftbeer', b=0,
		anim = {
			'rotate': True,
			'rotateRate': 0.0006,
			'rotateMax': 0.3,
			'rotateMin': -0.3,
		}
	))
	SHOW.animations.append(
			ObjectAnimation('celticpub', b=0,
		anim = {
			#'scale_x_mag': 1.0,
			#'scale_x_rate': 0.001,
			'scale_y_mag': 1.0,
			'scale_y_rate': 0.004
		}
	))

def main():
	global SHOW
	global ps

	def next_anim_thread():
		global SHOW
		while True:
			SHOW.next()
			time.sleep(3.0)

	ps = PointStream()
	#ps.showBlanking = True
	#ps.showTracking = True
	ps.blankingSamplePts = 12
	ps.trackingSamplePts = 12
	ps.scale = 0.6
	#ps.rotate = math.pi / 4

	SHOW = Show()
	SHOW.stream = ps

	#helloAnim = GmlAnimation('gml/hello.gml', mul=50000)
	#ballAnim4 = BouncingBall(numBalls=4)
	#squareAnim = SquareAnimation()

	# Make the show order 'fair' while restarting program.
	if random.randint(0, 1):
		addMC(SHOW)
		addLD(SHOW)
	else:
		addLD(SHOW)
		addMC(SHOW)

	SHOW.next()
	SHOW.prev()

	SHOW.start_dac_thread()
	time.sleep(1.0)
	thread.start_new_thread(next_anim_thread, ())

	while True:
		time.sleep(100000)

if __name__ == '__main__':
	main()
