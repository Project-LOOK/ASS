from dbus.mainloop.glib import DBusGMainLoop
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
import inspect

class Swipe(Gtk.GestureSwipe):
	
	def __init__(self, window):
		self.observers = []

		Gtk.GestureSwipe.__init__(self)
		print("Window: " + str(window))

		self.direction = None
		#super(Swipe, self).__new__(Gtk.GestureSwipe, window)
		#super(Swipe, self).__init__()
		self.connect("swipe", self._cb)
	
	def connect2(self, name, cb):
		self.observers.append(cb)
		print("connect obs")

	def _cb(self):
		print("_cb")
		for callback in observers:
			callback()

	def is_left_swipe(self, velocity):
		return (velocity > 500)

class TestGUI():
	def __init__(self):
		print "Creating gui"

		self.builder = Gtk.Builder()
		self.builder.add_from_file("hub_gui.glade")
		self.window = self.builder.get_object("window1")

		self.pages = []
		self.pages.append(Page(self.builder.get_object("page0"), "Menu"))
		self.pages.append(Page(self.builder.get_object("page1"), "HUD"))
		self.pages.append(Page(self.builder.get_object("page2"), "Video"))
		self.pages.append(Page(self.builder.get_object("page3"), "Sensor"))

		#Setup Carousel
		Page.stack = self.builder.get_object("myStack")
		self.carousel = Carousel(self.pages, self.builder.get_object("myStack"))

		# Sets prop_phase to capture, allows frame to capture over buttons
		self.swipe = Swipe(self.window)
		#self.swipe = Gtk.GestureSwipe.new(self.window)

		t1 = inspect.getmro(Gtk.GestureSwipe)
		#t2 = inspect.getmro(Swipe)
	
		print("")
		print("Page: " + str(t1))
		print("")
		#print("Page: " + str(t2))
		print("")

		self.swipe.set_propagation_phase(Gtk.PropagationPhase(1))
		self.swipe.connect("swipe", self.swipe_cb)

		self.window.show_all()

	def swipe_cb(self, gesture_swipe, velocity_x, velocity_y):
		print("swipe_cb (" + str(velocity_x) + ", " + str(velocity_y) + ")")

	def conn_btns(self):
		self.builder.connect_signals(self.handlers)

class Page(object):
	stack = None
	def __init__(self, page, name=None):
		self.page = page
		self.name = name
		print("Creating " + str(name) + " page")

	def load(self):
		print("Loading " + str(self.name) + " page")
		self.stack.set_visible_child(self.page)

	def unload(self):
		print("Unoading " + str(self.name) + " page")

class Carousel(object):
	def __init__(self, items, stack):
		self.items = items
		self.stack = stack
		self.index = 0
		self.stack.set_transition_duration(1000)
		self.items[self.index].load()

	def rotate_left(self):
		print("rotate left, " + str(self.index))
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.items[self.index].unload()
		self.index = self.index + 1
		if (self.index == len(self.items)):
			self.index = 0
		self.items[self.index].load()

	def rotate_right(self):
		print("rotate right")
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
		self.items[self.index].unload()
		if (self.index == 0):
			self.index = len(self.items)
		self.index = self.index - 1
		self.items[self.index].load()

	def current(self):
		print("current")

if __name__ == '__main__':
	DBusGMainLoop(set_as_default=True)
	global mainloop
	mainloop = GObject.MainLoop()

	myGUI = TestGUI()


	def dummy(self, btn):
		print("dummy")

	def quit(self, *args):
		mainloop.quit()

	myGUI.handlers = {"window_close_sig": quit,
			"add_s_sig": dummy,
			"remove_s_sig": dummy,
			"edit_s_sig": dummy,
			"cancel_remove_sig": dummy,
			"cancel_sig": dummy,
			"select_s_sig": dummy,
			"radio_toggled": dummy
			}
	myGUI.conn_btns()

	mainloop.run()