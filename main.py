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
			time.sleep(7.0)

	ps = PointStream()
	#ps.showBlanking = True
	#ps.showTracking = True
	ps.blankingSamplePts = 12
	ps.trackingSamplePts = 12

	SHOW = Show()
	SHOW.stream = ps

	#SHOW.animations.append(LogoAnimation())
	SHOW.animations.append(NameAnimation())
	SHOW.animations.append(GmlAnimation('gml/2years.gml',
		mul=20000))
	#SHOW.animations.append(NameAnimation())
	SHOW.animations.append(GmlAnimation('gml/happy.gml',
		mul=20000))
	#SHOW.animations.append(NameAnimation())
	SHOW.animations.append(AwesomeAnimation())

	SHOW.next()
	SHOW.prev()

	SHOW.start_dac_thread()
	time.sleep(1.0)
	thread.start_new_thread(next_anim_thread, ())

	while True:
		time.sleep(100000)

if __name__ == '__main__':
	main()
