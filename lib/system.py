import time
import thread
import random

from lib import dac
import fakedac

class Show(object):
	"""
	Laser Show
	This class controls the entire show and can switch
	between different animations (which have different
	backing code).
	"""
	def __init__(self):
		# Pointstream (prolly refactor)
		self.stream = None

		self.animations = []
		self.curIdx = 0
		self.isTimed = False

	# XXX: POOR DESIGN, UGH!
	def _switchBefore(self):
		anim = self.animations[self.curIdx]
		anim.stopAnimThread()

		# Remove all onscreen objects
		self.stream.objects = []

	def _switchAfter(self):
		anim = self.animations[self.curIdx]
		anim.startAnimThread()

		# Add all objects to be drawn
		for obj in anim.objects:
			self.stream.objects.append(obj)

		# Switch stream parameters
		self.stream.blankingSamplePts = \
				anim.blankingSamplePts
		self.stream.trackingSamplePts = \
				anim.trackingSamplePts

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

	def start_dac_thread(self):
		"""
		Start the DAC / PointStream thread.
		It is self-healing and should tolerate all kinds
		of errors.
		"""

		def t():
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

		thread.start_new_thread(t, ())

	def start_testdac_thread(self):
		"""
		This is just a test -- it'll just print points and
		never send to a laser projector.
		"""

		def t():
			# TODO: Reoptimize below.
			# TODO: Does this belong here?
			# TODO: Where does anything belong?
			while True:
				try:
					d = fakedac.Dac2()
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

		thread.start_new_thread(t, ())



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

	# Scaling animations (defaults)
	SCALE_MAX = 1.75
	SCALE_MIN = 0.5
	SCALE_RATE = 0.1

	# Tilting animations - oscillating theta (defaults)
	TILT_THETA_MAX = 0.4
	TILT_THETA_MIN = -0.4
	TILT_THETA_RATE = 0.05

	def __init__(self):
		# Frames *OR* objects, I suppose? 
		# Figure it out later. Depends on what PointStr 
		# eventually does. Which will PS take? 
		self.frames = []
		self.objects = []
		self.curIdx = 0
		self.timeDelta = None
		self.timeLast = None

		self.hasAnimationThread = False
		self.animationSleep = 0.05
		self._doRunThread = True # To turn on/off

		self.blankingSamplePts = 12
		self.trackingSamplePts = 12

		self.setup()

	def setup(self):
		"""
		Performs the work of main() for the animation.
		This typically is used to parameterize, setup,
		spawn threads.
		"""
		pass

	def animThreadFunc(self):
		"""
		Performs any animation processing in an independent
		thread. Override if necessary. See the relevant member
		vars for controlling.
		"""
		pass

	def startAnimThread(self):
		"""
		Launch Thread. (And thread def.)
		"""
		def t():
			self._doRunThread = True
			while self._doRunThread:
				self.animThreadFunc()
				time.sleep(self.animationSleep)

		if not self.hasAnimationThread:
			return

		thread.start_new_thread(t, ())

	def stopAnimThread(self):
		"""
		Exit Thread.
		"""
		self._doRunThread = False

