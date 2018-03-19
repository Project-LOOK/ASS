import video_mod
from time import sleep
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gst, GObject

class HubGUI:
	def __init__(self):

		self.test_sensor_btn = True	

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
		self.page3 = self.builder.get_object("page3")
		self.page4 = self.builder.get_object("page4")

		self.name_txt_box = self.builder.get_object("name_txt")
		self.addr_box = self.builder.get_object("addr_box")

		self.radio_btn = self.builder.get_object("radio1")

		self.stack.set_visible_child(self.page0)
		self.swipe = Gtk.GestureSwipe.new(self.window)

		# Sets prop_phase to capture, allows frame to capture over buttons
		self.swipe.set_propagation_phase(Gtk.PropagationPhase(1))
		self.swipe.connect("swipe", self.swipe_cb)

		self.ctrl_cb = None

		self.sensor_btns = {}

		self.video_player = None

		self.window.show_all()

		Gst.init(None)


	def add_video(self, btn):
		self.video_player = video_mod.VideoPlayer(self.window)
		#self.video_player.set_video_window(self.window)
		print "added_video"
		#self.video_player.set_video_window(self.window)

	def swipe_left(self, gesture_swipe):
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		if (self.stack.get_visible_child() == self.page0):
			self.unload_page0()
			self.load_page1()
		elif (self.stack.get_visible_child() == self.page1):
			self.unload_page1()
			self.load_page2()
		elif (self.stack.get_visible_child() == self.page2):
			self.unload_page2()
			self.load_page3()
		elif (self.stack.get_visible_child() == self.page3):
			self.unload_page3()
			self.load_page0()

	def swipe_right(self, gesture_swipe):
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
		if (self.stack.get_visible_child() == self.page0):
			self.unload_page0()
			self.load_page3()
		elif (self.stack.get_visible_child() == self.page1):
			self.unload_page1()
			self.load_page0()
		elif (self.stack.get_visible_child() == self.page2):
			self.unload_page2()
			self.load_page1()
		elif(self.stack.get_visible_child() == self.page3):
			self.unload_page3()
			self.load_page2()

	def load_page0(self):
		self.stack.set_visible_child(self.page0)

	def unload_page0(self):
		print "Unloaded page0"

	def load_page1(self):
		self.stack.set_visible_child(self.page1)

	def unload_page1(self):
		print "Unloaded page1"

	def load_page2(self):
		#self.video_player.start_video()
		self.stack.set_visible_child(self.page2)

	def unload_page2(self):
		#self.video_player.stop_video()
		print "Unloaded page2"

	def load_page3(self):
		self.stack.set_visible_child(self.page3)
		self.ctrl_cb("start_disco")

	def unload_page3(self):
		self.ctrl_cb("stop_disco")
		print "Unloaded page3"

	def load_page4(self):
		print("HERE")
		self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		self.previous_page = self.stack.get_visible_child()
		self.stack.set_visible_child(self.page4)

	def unload_page4(self):
		self.stack.set_visible_child(self.previous_page)
		self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

	def swipe_cb(self, gesture_swipe, velocity_x, velocity_y):
		# This drops touches because we only want swipes
		if (velocity_x > 500):
			gesture_swipe.set_state(Gtk.EventSequenceState(1))
			self.swipe_right(gesture_swipe)

		elif (velocity_x < -500):
			gesture_swipe.set_state(Gtk.EventSequenceState(1))
			self.swipe_left(gesture_swipe)

	def list_sensor(self, addr, cb):
		print "List sensor that has been found: " + addr
		if not(addr in self.sensor_btns):
			print "Adding button"
			self.sensor_btns[addr] = Gtk.Button(addr)
			print self.page3
			self.page3.attach(self.sensor_btns[addr], 0, len(self.sensor_btns)+2, 1, 1)
	        self.sensor_btns[addr].connect("clicked", cb)
	        self.window.show_all()

	def selection_menu(self, address):
		print("Selection Menu")
		self.name_txt_box.set_text(address)
		self.addr_box.set_text(address)
		self.load_page4()

	def remove_menu(self, address):
		print("Remove Menu")


	def set_handlers(self, handlers):
		self.handlers = handlers

	def conn_btns(self):
		self.builder.connect_signals(self.handlers)

	def bind_to(self, key, cb):
		self.builder.connect_signals({key, cb})

	def radio_toggled(self, radio): 
		print("Active: " + str(radio.get_active()))

class MenuPage(object):
	def __init__(self, page):
		self.page = page
		print("Creating Menu page")

class VideoPage(object):
	def __init__(self, page):
		self.page = page
		print("Creating Video page")

class SensorPage(object):
	def __init__(self, page):
		self.page = page
		print("Creating Sensor page")

class HUDPage(object):
	def __init__(self, page):
		self.page = page
		print("Creating HUD page")

