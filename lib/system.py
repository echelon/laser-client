import random

class Show(object):
	"""
	Laser Show
	This class controls the entire show and can switch
	between different animations (which have different
	backing code).
	"""
	def __init__(self):
		self.animations = []
		self.curIdx = 0
		self.isTimed = False

	def getCurAnim(self):
		# TODO: This would manage the timer if 
		# a timeout is currently set. 
		return self.animations[self.curIdx]

	def next(self):
		self.curIdx = (self.curIdx+1) % \
						len(self.animations)

	def prev(self):
		self.curIdx = (self.curIdx-1) % \
						len(self.animations)

	def random(self):
		self.curIdx = random.randint(0,
						len(self.animations) - 1)

	def dac_thread(self):
		# TODO: Reoptimize below.
		ps = None # TODO

		while True:
			try:
				d = dac.DAC(dac.find_first_dac())
				d.play_stream(ps)

			except KeyboardInterrupt:
				sys.exit()

			except Exception as e:
				import sys, traceback
				print '\n---------------------'
				print 'DacThread Exception: %s' % e
				print '- - - - - - - - - - -'
				traceback.print_tb(sys.exc_info()[2])
				print "\n"

class Animation(object):
	"""
	Animation

	This class controls the animation setup, thread
	spawing and shutdown, configuration, etc.
	"""

	def __init__(self):
		# Frames *OR* objects, I suppose? 
		# Figure it out later. Depends on what PointStr 
		# eventually does. Which will PS take? 
		self.frames = []
		self.objects = []
		self.curIdx = 0
		self.timeDelta = None
		self.timeLast = None

		self.setup()

	def setup(self):
		"""
		Performs the work of main() for the animation.
		This typically is used to parameterize, setup,
		spawn threads.
		"""
		pass

	def thread_dac(self):
		pass

	def getCurFrame(self):
		self.frames[self.curIdx]

