from bt_ctrl import BluetoothController
from sensor_db import SensorDB, Sensor
from pydbus import SystemBus, Variant
from timeout import timeout
import time
import sys
from dbus.mainloop.glib import DBusGMainLoop

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject

def main():
	print "self test..."

	DBusGMainLoop(set_as_default=True)
	global mainloop
	mainloop = GObject.MainLoop()
	
	global mybt
	mybt = BluetoothController(SystemBus())

	builder = Gtk.Builder()
	builder.add_from_file("test_bt.glade")
	window = builder.get_object("window1")


	handlers = {"window_close_sig": mainloop.quit,
				"start_sig": start_disco,
				"stop_sig": stop_disco,
				"list_sig": list_devs,
				"conn_sig": connect_all,
				"scan_sig": scan
				}
	builder.connect_signals(handlers)
	window.show_all()

	mainloop.run()

def start_disco(*args):
	mybt.scan_devices()
	mybt.start_discovery()

def stop_disco(*args):
	mybt.stop_discovery()

def list_devs(*args):
	mybt.list_devs()

def connect_all(*args):
	print(mybt.devices.values())
	for sensor in mybt.devices.values():
		print("SENSOR: " + str(type(sensor.object)))
		mybt.connect_device(sensor)

def scan(*args):
	mybt.scan_devices()

def notify_on(*args):
	mybt.notify()
def notify_handler(*args):
	print("notify handler")
	print(args)

if __name__ == '__main__':
	main()
