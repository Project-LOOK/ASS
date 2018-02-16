import test_video
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gst, GObject

class Hub_gui:
	def add_video(self, btn):
		self.video_player = test_video.Vid_Player(self.window)
		#self.video_player.set_video_window(self.window)
		print "added_video"
		#self.video_player.set_video_window(self.window)

	def swipe_left(self, gesture_swipe):
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		if (self.stack.get_visible_child() == self.page0):
			self.stack.set_visible_child(self.page1)
		elif (self.stack.get_visible_child() == self.page1):
			self.video_player.start_video()
			self.stack.set_visible_child(self.page2)
		else:
			self.stack.set_visible_child(self.page0)
			self.video_player.stop_video()

	def swipe_right(self, gesture_swipe):
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
		if (self.stack.get_visible_child() == self.page0):
			self.video_player.start_video()
			self.stack.set_visible_child(self.page2)
		elif (self.stack.get_visible_child() == self.page1):
			self.stack.set_visible_child(self.page0)
		else:
			self.stack.set_visible_child(self.page1)
			self.video_player.stop_video()

	def swipe_cb(self, gesture_swipe, velocity_x, velocity_y):
		# This drops touches because we only want swipes
		if (velocity_x > 500):
			gesture_swipe.set_state(Gtk.EventSequenceState(1))
			self.swipe_right(gesture_swipe)

		elif (velocity_x < -500):
			gesture_swipe.set_state(Gtk.EventSequenceState(1))
			self.swipe_left(gesture_swipe)

	def __init__(self):
		print "Creating gui"
		self.builder = Gtk.Builder()
		self.builder.add_from_file("hub_gui.glade")
		self.window = self.builder.get_object("window1")

		#Setup Stack
		self.stack = self.builder.get_object("myStack")
		self.stack.set_transition_duration(1000)

		self.page0 = self.builder.get_object("page0")
		self.page1 = self.builder.get_object("page1")
		self.page2 = self.builder.get_object("page2")
		self.stack.set_visible_child(self.page0)

		self.swipe = Gtk.GestureSwipe.new(self.window)
		# Sets prop_phase to capture, allows frame to capture over buttons
		self.swipe.set_propagation_phase(Gtk.PropagationPhase(1))
		self.swipe.connect("swipe", self.swipe_cb)

		self.car = self.builder.get_object("car_img")

		self.window.show_all()
		#GObject.threads_init()
		Gst.init(None)

	def hello(self, button):
		print "Clicked"
		print self
		print button
		print ""

	def conn_btns(self):
		#self.handlers = {"onDeleteWindow": Gtk.main_quit, "click_h": self.hello}
		self.builder.connect_signals(self.handlers)

	def set_handlers(self, handlers):
		self.handlers = handlers
