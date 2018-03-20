from time import sleep
from collections import OrderedDict
import sys
import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gtk, Gst, GObject, GdkX11, GstVideo

class HubGUI:
	def __init__(self, sensors):

		# Setup Gtk builder for GUI
		self.builder = Gtk.Builder()
		self.builder.add_from_file("hub_gui.glade")
		self.window = self.builder.get_object("window1")

		self.sensors = sensors
		self.sensors.bind_to(self.db_changed)
		self.observers = {}

		self.menuPage = MenuPage(self.builder.get_object("page0"), "Menu")
		self.HUD = HUDPage(self.builder.get_object("page1"), self.sensors, "HUD")
		self.videoPage = VideoPage(self.builder.get_object("page2"), "Video", self.window)
		self.sensorPage = SensorPage(self.builder.get_object("page3"), self.sensors, "Sensor")
		self.add_menu = AddSensorMenu(self.builder.get_object("page4"), "AddSensor")
		self.remove_menu = RemoveSensorMenu(self.builder.get_object("page5"), "RemoveSensor")

		#Setup Carousel
		Page.stack = self.builder.get_object("myStack")
		self.carousel = Carousel(self.builder.get_object("myStack"), self.sensorPage)
		self.carousel.add(self.menuPage)
		self.carousel.add(self.HUD)
		self.carousel.add(self.videoPage)
		self.carousel.reload_current()
		# Allows frame to capture before buttons (for swiping)
		self.swipe = Gtk.GestureSwipe.new(self.window)
		self.swipe.set_propagation_phase(Gtk.PropagationPhase(1))
		self.swipe.connect("swipe", self.swipe_cb)

		# Drawing canvases for sensors
		self.canvases = {}
		self.canvases["Front right"] = self.builder.get_object("front_right")
		self.canvases["Middle right"] = self.builder.get_object("mid_right")
		self.canvases["Rear right"] = self.builder.get_object("rear_right")
		self.canvases["Front left"] = self.builder.get_object("front_left")
		self.canvases["Middle left"] = self.builder.get_object("mid_left")
		self.canvases["Rear left"] = self.builder.get_object("rear_left")
		self.angles = {"Front right": 3.14, "Middle right": -3.14/2, "Rear right": 0,
						"Front left": 3.14,	"Middle left": 3.14/2, "Rear left": 0}

		for canvas in self.canvases.values():
			canvas.radius = 0
			canvas.angle = 0

		self.sensorPage.btn_cb = self.select_sensor
		self.handlers = {"window_close_sig": self.quit,
						"cancel_add_sig": self.cancel_add,
						"radio_sig": self.add_menu.radio_toggled,
						"add_sig": self.add,
						"rm_sig": self.rm,
						"edit_sig": self.edit,
						"cancel_rm_sig": self.cancel_rm,
						"test_sig": self.test_btn,
						"draw": self.HUD.draw
		}
		self.builder.connect_signals(self.handlers)

		self.window.show_all()

	def bind_to(self, key, cb):
		if key not in self.observers.keys():
			self.observers[key] = []
		self.observers[key].append(cb)

	def swipe_cb(self, gesture_swipe, velocity_x, velocity_y):
		# This drops touches because we only want swipes
		direction = get_direction(velocity_x, velocity_y)
		if (direction == "LEFT"):
			#gesture_swipe.set_state(Gtk.EventSequenceState(1))
			self.carousel.rotate_right()
		elif (direction == "RIGHT"):
			#gesture_swipe.set_state(Gtk.EventSequenceState(1))
			self.carousel.rotate_left()
		elif (direction == "UP"):
			print("up swipe")
		elif (direction == "DOWN"):
			print("down swipe")

	def test_btn(self, *args):
		print("Test btn")

	def rm(self, *args):
		print("Remove: " + str(self.remove_menu.address))
		self.sensors[self.remove_menu.address].active = False
		self.carousel.reload_current()

	def cancel_rm(self, *args):
		self.carousel.reload_current()
		
	def edit(self, *args):
		print("Edit")
		address = self.remove_menu.address
		name = self.sensors[address].name
		position = self.sensors[address].position
		self.add_menu.load(address, name, position)

	def quit(self, *args):
		self.handle_cb("quit")

	def handle_cb(self, key, *args):
		for callback in self.observers[key]:
			callback(*args)

	def db_changed(self, *args):
		if self.carousel.current() == "Sensor":
			self.sensorPage.redraw()

	def select_sensor(self, btn):
		#print("Select sensor: " + str(btn.get_property("label")))
		address = btn.get_property('label')
		name = self.sensors[address].name
		if (address in self.sensors):
			if self.sensors[address].active:
				self.remove_menu.load(address)
			else:
				self.add_menu.load(address, name)

	def add(self, btn):
		name = self.add_menu.name_txt.get_text()
		address = self.add_menu.addr_txt.get_text()
		position = self.add_menu.position
		self.sensors[address].name = name
		self.sensors[address].active = True
		self.sensors[address].position = position
		self.sensors[address].canvas = self.canvases[position]
		self.sensors[address].canvas.angle = self.angles[position]
		self.sensors[address].address = address
		self.carousel.reload_current()

	def cancel_add(self, *args):
		self.carousel.reload_current()

class Page(object):
	stack = None
	def __init__(self, page, name=None):
		self.load_observers = []
		self.unload_observers = []
		self.page = page
		self.name = name

	def load(self):
		for callback in self.load_observers:
			callback()
		print("Loading " + str(self.name) + " page")
		self.stack.set_visible_child(self.page)

	def unload(self):
		print("Unoading " + str(self.name) + " page")
		for callback in self.unload_observers:
			callback()

	def bind_to(self, key, cb):
		if key=="load":
			self.load_observers.append(cb)
		elif key=="unload":
			self.unload_observers.append(cb)

class MenuPage(Page): 
	def stub_method(self):
		print("Stub method in Menu page")

class VideoPage(Page):
	def __init__(self, page, name="VideoPage", window=None):
		super(VideoPage, self).__init__(page, name)
		Gst.init(None)
		self.movie_window = Gtk.DrawingArea()
		self.window = window
		
		self.player = Gst.ElementFactory.make("playbin", None)
		self.player.set_property("uri", "http://192.168.3.7:8080/?action=stream")

		bus = self.player.get_bus()
		bus.add_signal_watch()
		bus.enable_sync_message_emission()
		bus.connect("message", self.on_message)
		bus.connect("sync-message::element", self.on_sync_message)

	def load(self):
		super(VideoPage, self).load()
		print("player: " + str(self.player))
		self.start_video()

	def unload(self):
		super(VideoPage, self).unload()
		self.stop_video()

	def add_video(self, btn):
		self.video_player = video_mod.VideoPlayer(self.window)
		#self.video_player.set_video_window(self.window)
		print "added_video"
		#self.video_player.set_video_window(self.window)

	def on_message(self, bus, message):
		a = 0
		'''
		t = message.type
		if t == Gst.MessageType.EOS:
			print "???"
			self.player.set_state(Gst.State.NULL)
		elif t == Gst.MessageType.ERROR:
			self.player.set_state(Gst.State.NULL)
			err, debug = message.parse_error()
			print "Error: %s" % err, debug
			self.button.set_label("Start")
		'''
	
	def on_sync_message(self, bus, message):
		print "On sync message"
		if message.get_structure().get_name() == 'prepare-window-handle':
			imagesink = message.src
			imagesink.set_property("force-aspect-ratio", True)
			imagesink.set_window_handle(self.window.get_property('window').get_xid())
			self.imagesink = imagesink

	def start_video(self):
		print("start video")
		self.player.set_state(Gst.State.PLAYING)

	def stop_video(self):
		print("stop video")
		self.player.set_state(Gst.State.PAUSED)

class SensorPage(Page):
	def __init__(self, page, items, name=None):
		super(SensorPage, self).__init__(page, name)
		self.btns = {}
		self.items = items
		self.btn_cb = None

	def add_btn(self, name):
		self.btns[name] = Gtk.Button(name)
		self.btns[name].connect("clicked", self.btn_cb)
		self.page.attach(self.btns[name],0,len(self.btns),1,1)
		self.page.show_all()

	def remove_btn(self, btn):
		btn_top = self.page.child_get_property(btn, 'top-attach')
		i = btn_top

		self.page.remove(self.page.get_child_at(0,i))
		for i in range(btn_top,len(self.btns)):
			self.page.child_set_property(self.page.get_child_at(0, i+1), 'top-attach', i)

		del(self.btns[btn.get_property("label")])
		self.page.show_all()

	def redraw(self, *args):
		item_keys = self.items.keys()
		btn_keys = self.btns.keys()

		for btn_name in btn_keys:
			if not (btn_name in item_keys):
				self.remove_btn(self.btns[btn_name])

		for item_name in item_keys:
			if not (item_name in btn_keys):
				self.add_btn(item_name)

class HUDPage(Page):
	def __init__(self, page, items, name=None):
		super(HUDPage, self).__init__(page, name)
		self.items = items

	def load(self):
		super(HUDPage, self).load()
		for item in self.items.values():
			if item.active:
				item.bind_to("value", self.update)		

	def unload(self):
		for item in self.items.values():
			if item.active:
				item.clear_binds("value")		

		super(HUDPage, self).unload()

	def update(self, obj, key, value):
		obj.canvas.radius = obj.avg_value
		obj.canvas.queue_draw()

	def draw(self, canvas, cr):
		w = canvas.get_allocated_width()
		h = canvas.get_allocated_height()
		size = min(w,h)
		
		cr.set_source_rgb(0.2, .5, 1.0)
		cr.arc(.5*w, .5*h, canvas.radius, canvas.angle-3.14/8, canvas.angle+3.14/8)
		cr.line_to(.5*w, .5*h)
		cr.fill()

class AddSensorMenu(Page):
	def __init__(self, page, name=None):
		super(AddSensorMenu, self).__init__(page, name)
		self.objs = self.page.get_children()
		self.radio_group = []
		for obj in self.objs:
			if (obj.get_property('name') == "radio_group"):
				self.radio_group.append(obj)
			elif (obj.get_property('name') == "name_txt"):
				self.name_txt = obj
			elif (obj.get_property('name') == "addr_txt"):
				self.addr_txt = obj

	def load(self, address, name, position=None):
		self.name_txt.set_text(name)
		self.addr_txt.set_text(address)
		self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		super(AddSensorMenu, self).load()
		if position:
			for radio_btn in self.radio_group:
				if radio_btn.get_property("label") == position:
					radio_btn.set_active(True)			
		else:
			self.radio_group[0].set_active(True)
			self.position = self.radio_group[0].get_property("label")

	def radio_toggled(self, radio):
		if (radio.get_active()):
			self.position = radio.get_property("label")
		
class RemoveSensorMenu(Page):
	def load(self, address):
		self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		super(RemoveSensorMenu, self).load()
		self.address = address

class Carousel(object):
	def __init__(self, stack, first, items=None):
		self.observers = []
		self.items = [first]
		self.stack = stack
		self.index = 0
		self.items[0].load()

	def rotate_left(self):
		#print("rotate left, " + str(self.index))
		self.stack.set_transition_duration(1000)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.items[self.index].unload()
		self.index = self.index + 1
		if (self.index == len(self.items)):
			self.index = 0
		self.items[self.index].load()

	def rotate_right(self):
		#print("rotate right")
		self.stack.set_transition_duration(1000)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
		self.items[self.index].unload()
		if (self.index == 0):
			self.index = len(self.items)
		self.index = self.index - 1
		self.items[self.index].load()

	def reload_current(self):
		self.items[self.index].load()

	def current(self):
		return self.items[self.index].name

	def bind_to(self, cb):
		self.observers.append(cb)

	def add(self, item):
		self.items.append(item)

def get_direction(x, y):
	if (x > 500):
		return "LEFT"
	elif(x < -500):
		return "RIGHT"
	elif (y < -500):
		return "UP"
	elif (y > 500):
		return "DOWN"
	return "PRESS"
