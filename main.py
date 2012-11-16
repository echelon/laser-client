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

def main():
	global SHOW
	global ps

	def next_anim_thread():
		global SHOW
		while True:
			SHOW.next()
			time.sleep(6.0)

	ps = PointStream()
	#ps.showBlanking = True
	#ps.showTracking = True
	ps.blankingSamplePts = 12
	ps.trackingSamplePts = 12
	ps.scale = 0.6
	#ps.rotate = math.pi / 4

	SHOW = Show()
	SHOW.stream = ps

	# LOGO
	#partyAnim = PartyAnimation()

	# SVG SHAPES
	#arrowAnim = ArrowAnimation()
	batAnim = BatAnimation()
	ghostAnim = GhostAnimation()
	awesomeAnim = AwesomeAnimation()
	costumesAnim = CostumesAnimation()

	# GML
	helloAnim = GmlAnimation('gml/hello.gml', mul=50000)

	# MISC
	#ballAnim1 = BouncingBall(numBalls=1)
	#ballAnim4 = BouncingBall(numBalls=4)
	#ballAnim10 = BouncingBall(numBalls=10)
	#squareAnim = SquareAnimation()

	"""
	SHOW.animations.append(SquareAnimation())
	SHOW.animations.append(BouncingBall(numBalls=20))
	SHOW.animations.append(ghostAnim)
	SHOW.animations.append(awesomeAnim)
	SHOW.animations.append(batAnim)
	SHOW.animations.append(HexAnimation())
	SHOW.animations.append(BouncingBall(numBalls=6))
	#SHOW.animations.append(helloAnim)
	SHOW.animations.append(ArrowAnimation())
	"""
	SHOW.animations.append(costumesAnim)

	"""
	SHOW.animations.append(partyAnim)
	SHOW.animations.append(costumesAnim)
	SHOW.animations.append(partyAnim)
	SHOW.animations.append(arrowAnim)
	SHOW.animations.append(partyAnim)

	SHOW.animations.append(partyAnim)
	SHOW.animations.append(partyAnim)
	SHOW.animations.append(arrowAnim)
	SHOW.animations.append(partyAnim)
	"""

	SHOW.next()
	SHOW.prev()

	SHOW.start_dac_thread()
	time.sleep(1.0)
	thread.start_new_thread(next_anim_thread, ())

	while True:
		time.sleep(100000)

if __name__ == '__main__':
	main()
