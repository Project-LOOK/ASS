import threading
from pydbus import SystemBus
from dbus.mainloop.glib import DBusGMainLoop
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
import time

class Tester(object):
	def __init__(self):
		time.sleep(2)

		self.func()

	def func(self):
		print("start")
		self.work_thread = threading.Thread(group=None, target=self.async, obj="XBY")
		self.running = True
		self.work_thread.start()
		print("stop")


	def async(self, obj="ABC"):
		time.sleep(4)
		print("obj: " + str(obj))

def main():
	DBusGMainLoop(set_as_default=True)
	global mainloop
	mainloop = GObject.MainLoop()
	
	tester = Tester()
	mainloop.run()

if __name__ == '__main__':
	main()