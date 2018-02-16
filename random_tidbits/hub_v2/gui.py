#import gi
#gi.require_version('Gtk', '3.0')
#from gi.repository import Gtk

class Hub_gui:
	def __init__(self):
		print "Creating gui"
		self.builder = Gtk.Builder()
		self.builder.add_from_file("hub_gui.glade")
		self.window = self.builder.get_object("window1")
		self.window.show_all()

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
