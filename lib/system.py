import random

class Show(object):
	"""
	Laser Show
	This class controls the entire show and can switch
	between different animations (which have different
	backing code).
	"""
	def __init__(self):
		self.stream = None # Pointstream (prolly refactor)
		self.animations = []
		self.curIdx = 0
		self.isTimed = False

	# XXX: POOR DESIGN, UGH!
	def _switchBefore(self):
		anim = self.animations[self.curIdx]
		anim.stopThreads()

		# Remove all onscreen objects
		self.stream.objects = []

	def _switchAfter(self):
		anim = self.animations[self.curIdx]
		anim.startThreads()

		# Add all objects to be drawn
		for obj in anim.objects:
			self.stream.objects.append(obj)

	def next(self):
		self._switchBefore()
		self.curIdx = (self.curIdx+1) % \
						len(self.animations)
		self._switchAfter()

	def prev(self):
		self._switchBefore()
		self.curIdx = (self.curIdx-1) % \
						len(self.animations)
		self._switchAfter()

	def random(self):
		self._switchBefore()
		self.curIdx = random.randint(0,
						len(self.animations) - 1)
		self._switchAfter()

	def dac_thread(self):
		# TODO: Reoptimize below.
		# TODO: Does this belong here?
		# TODO: Where does anything belong?
		while True:
			try:
				d = dac.DAC(dac.find_first_dac())
				d.play_stream(self.stream)

			except KeyboardInterrupt:
				sys.exit()

			except Exception as e:
				import sys, traceback
				print '\n---------------------'
				print 'DacThread Exception: %s' % e
				print '- - - - - - - - - - -'
				traceback.print_tb(sys.exc_info()[2])
				print "\n"

	"""
	def getCurAnim(self):
		# TODO: This would manage the timer if
		# a timeout is currently set.
		return self.animations[self.curIdx]
	"""

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

	def startThreads(self):
		pass

	def stopThreads(self):
		pass

	"""
	def thread_dac(self):
		pass

	def getCurFrame(self):
		self.frames[self.curIdx]
	"""
