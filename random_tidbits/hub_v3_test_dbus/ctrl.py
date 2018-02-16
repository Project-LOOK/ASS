# Look imports
from bt_ctrl import Bluetooth_Controller
#from gui import Hub_gui

from pydbus import SystemBus

# Kivy Imports
#from kivy.lang import Builder
#from kivy.app import App
#from kivy.core.video import Video
#from kivy.uix.floatlayout import FloatLayout
#from kivy.properties import ObjectProperty

# Glib imports
#from dbus.mainloop.glib import DBusGMainLoop
#try:
#  from gi.repository import GObject
#except ImportError:
#  import gobject as GObject
import sys
import time

class Controller:
	
	def __init__(self):
		self.sensors = {}
		self.sys_bus = SystemBus()
		self.bt = Bluetooth_Controller()
		self.bt.reg_sig()
		print "Registerd Signal"
		self.bt.cb = self.bt_cb
		# Add existing interfaces to list
		#self.bt.start_discovery()

		#self.bt = self.sys_bus.get()
		#self.our_gui = Hub_gui()
		'''
		self.handlers = {"window_close_sig": self.quit,
			"add_s_sig": self.add_sensor,
			"enter_s_menu_sig": self.enter_sensor_menu,
			"exit_s_menu_sig": self.exit_sensor_menu
		}
		'''
		#self.our_gui.set_handlers(self.handlers)
		#self.our_gui.conn_btns()


	def gui_cb(msg):
		print option

	def update_sensors():
		print "GUI wants senors"

	def add_sensor(self, btn):
		print 'GUI wants to add a sensor'
		print 'self: ' + str(self)
		Label = btn.get_property('label')

		print 'add sensor: ' + Label
		#sensor = Sensor(btn.get_property('label'))
		self.sensors[Label] = Sensor(Label)

		print "dictionary length: " + str(len(self.sensors))


	def sensor_available():
		#gui.update_sensor_list
		print "Update GUI sensor list"

	def redraw():
		print "Tell GUI to redraw?"

	def bt_cb(self, path, obj):
		print "ctrl got new obj"
		print path
		print obj

	def disco_on(self, btn):
		print "Disco"

	def enter_sensor_menu(self, btn):
		print "Get_sensor"
		self.bt.start_discovery()

	def exit_sensor_menu(self, btn):
		print "Leaving sensor menu ..."
		print "Discovery off"
		self.bt.stop_discovery()

	def quit(self, *args):
		print "QUIT"
		#self.our_gui.quit()
		mainloop.quit()

def main():
	#DBusGMainLoop(set_as_default=True)
	#global mainloop
	#mainloop = GObject.MainLoop()
	
	print "Main"
	ctrl = Controller()
	
	#our_gui = Hub_gui()

	print "setting handlers"
	#mainloop.run()


if __name__ == '__main__':
	main()