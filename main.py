#!/usr/bin/env python

import os
import sys
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
from lib.gml import *
from lib.svg import *

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

# At 13, need 24.
# Wants animated dice...

def get_obj_filename():
	"""See if the named object file exists."""
	if len(sys.argv) < 2:
		return

	name = sys.argv[1]
	fname = 'objs/{}.py'.format(name)

	if os.path.exists(fname):
		return name.replace('/', '.')

def main():
	global SHOW
	global ps

	def next_anim_thread():
		global SHOW
		while True:
			SHOW.next()
			time.sleep(5.0)

	ps = PointStream()
	ps.scale = 0.0000001
	#ps.showBlanking = True
	#ps.showTracking = True
	ps.blankingSamplePts = 12
	ps.trackingSamplePts = 12
	ps.scale = 0.6
	#ps.rotate = math.pi / 4

	SHOW = Show()
	SHOW.stream = ps

	mike = SvgAnim('michael',
		anim = {
			'rotate': True,
			'rotateRate': 0.001,
			'rotateMin': -0.501,
			'rotateMax': 0.501, 'scale': True,
			'scaleRate': 0.0009,
			'scaleMin': 0.5,
			'scaleMax': 1.2,
		}
	)
	#s = snoo.objects[0]
	#s.trackingSamplePts = 5
	#s.blankingSamplePts = 50

	#for o in snoo.objects:
	#	o.scale = 2.0
	#	#o.showBlanking = True
	#snoo.showBlanking = True
	#snoo.scale = 2.0
	#SHOW.animations.append(mike)
	#SHOW.animations.append(AwesomeAnimation())
	#SHOW.animations.append(BatAnimation())
	#SHOW.animations.append(BouncingBall(numBalls=4))
	#SHOW.animations.append(GhostAnimation())
	#SHOW.animations.append(GhostAnimation())
	#SHOW.animations.append(BatAnimation())


	octo = SvgAnim('octocat',
		anim = {
			'rotate': True,
			'rotateRate': 0.001,
			'rotateMin': -0.501,
			'rotateMax': 0.501,
			'scale': True,
			'scaleRate': 0.0009,
			'scaleMin': 0.5,
			'scaleMax': 1.2,
		}
	)

	default = 'snoo'
	name = get_obj_filename()

	if not name:
		name = default

	obj = SvgAnim(name,
		anim = {
            #'rotate': True,
            #'rotateRate': 0.0005,
            #'rotateMin': -0.501,
            #'rotateMax': 0.501,
            #'scale': True,
            #'scaleRate': 0.0001,
            #'scaleMin': 0.1,
            #'scaleMax': 0.4,
		}
	)

	SHOW.animations.append(obj)
	#SHOW.animations.append(GmlAnim('gml/happy2.gml'))
	#SHOW.animations.append(GmlAnim('gml/birthday2.gml'))
	#SHOW.animations.append(GmlAnim('gml/i_heart_js.gml'))
	#SHOW.animations.append(octo)

	"""
	SHOW.animations.append(
			GmlAnim('gml/doritoslocos.gml')
	)
	SHOW.animations.append(ArrowAnim())
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
