# Profile
# 	 ^---Service
#   	    ^---Characteristic

from sensor_db import SensorDB
from pydbus import SystemBus, Variant
from timeout import timeout
import time
import sys
import threading

from dbus.mainloop.glib import DBusGMainLoop
try:
  from gi.repository import GObject, Gtk
except ImportError:
  import gobject as GObject

BT_ADAPTOR_HINT = None 
BLUEZ_SVC_NAME = 'org.bluez'
ADAPTER_IFACE = 'org.bluez.Adapter1'
DEVICE_IFACE = 'org.bluez.Device1'

DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

GATT_SVC_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE =    'org.bluez.GattCharacteristic1'

LIDAR_SVC_UUID = '19b10012-e8f2-537e-4f6c-d104768a1214'
SONAR_SVC_UUID = '19b10010-e8f2-537e-4f6c-d104768a1214'
DIST_CHRC_UUID = '19b10011-e8f2-537e-4f6c-d104768a1214'


UUIDs = Variant('as', ['19b10012-e8f2-537e-4f6c-d104768a1214',
		 '19b10010-e8f2-537e-4f6c-d104768a1214', 
		 '19b10011-e8f2-537e-4f6c-d104768a1214'])

class BluetoothController:
	def __init__(self, sys_bus):
		self.bus = sys_bus
		self.bluez = self.bus.get(BLUEZ_SVC_NAME, '/')
		self.adapter = self.find_adapter()
		self.sensors = None

	def async_connect(self, object):
		object['org.bluez.Device1'].Connect()

	def find_adapter(self, pattern=None):
		objs = self.bluez.GetManagedObjects()
		for path, ifaces in objs.iteritems():
			adapter = ifaces.get(ADAPTER_IFACE)
			if adapter is None:
				continue
			if not pattern or pattern == adapter["Address"] or path.endswith(pattern):
				obj = self.bus.get(BLUEZ_SVC_NAME, path)
				print "Found Adapter: " + obj.Get("org.bluez.Adapter1", "Name")
				return obj
		raise Exception("Bluetooth adapter not found")

	def find_device(self, device_address):
		objects = self.bluez.GetManagedObjects()
		path_prefix = self.adapter.object_path
		for path, ifaces in objects.iteritems():
			device = ifaces.get(DEVICE_IFACE)
			if device is None:
				continue
			if (device["Address"] == device_address and
							path.startswith(path_prefix)):
				obj = self.bus.get(BLUEZ_SVC_NAME, path)
				return obj
		raise Exception("Bluetooth device not found")

	def start_discovery(self):
		self.adapter.SetDiscoveryFilter({'UUIDs': UUIDs})
		self.adapter.StartDiscovery()

		print "Discovery on"

	def stop_discovery(self):
		self.adapter.StopDiscovery()
		self.adapter.SetDiscoveryFilter()

	def check_discovery(self):
		discovering = self.adapter.Get("org.bluez.Adapter1", "Discovering")
		return discovering

	def reg_sig(self):
		self.bluez.InterfacesAdded.connect(self.iface_added)
		self.bluez.InterfacesRemoved.connect(self.iface_removed)

	def connect_to_dev(self, dev): 
		print "Connecting to sensor: " + str(dev.address)

		if not(dev.object.Get('org.bluez.Device1', 'Connected')):
			dev.work_thread = threading.Thread(group=None, target=self.async_connect(dev.object))
			dev.running = True
			dev.work_thread.start()
			#dev.object['org.bluez.Device1'].Connect()asy
			print "*****connected******"
		else:
			print "already connected"

	def setup_new_sensor(self, address):
		dev = self.devices[address]
		print dev
		self.connect_to_dev(dev)
		#self.en_notifications(dev)

	def en_notifications(self, address, update_cb):
		print "Enabling notifications..."
		SONAR_SVC_UUID

		char = self.bus.get(BLUEZ_SVC_NAME, char_addr)
		print "Char: " + str(char)

		self.bus.subscribe(iface=DBUS_PROP_IFACE,
                      signal='PropertiesChanged',
                      object=char_addr,
                      signal_fired=update_cb)

		char.StartNotify()
		print "Done?"
		#.InterfacesAdded.connect(self.iface_added)

	def iface_added(self, path, obj):
		print "type: " + str(type(path))
		if GATT_CHRC_IFACE in obj.keys():
			print "Gatt chrc: " + str(obj[GATT_CHRC_IFACE]["Service"])
			found_new_chrc = self.process_chrc(path, obj[GATT_CHRC_IFACE])
			if (found_new_chrc):
				self.new_chrc_cb()

		elif GATT_SVC_IFACE in obj.keys():
			print "Gatt svc: " + str(obj[GATT_SVC_IFACE]["Includes"])
			found_new_svc = self.process_svc(path, obj[GATT_SVC_IFACE])

		elif DEVICE_IFACE in obj.keys():
			print "Device: " + str(path)
			found_new_device = self.process_dev(path, obj[DEVICE_IFACE])
			if found_new_device:
				self.new_dev_cb(self.address_from_path(path))
		
		print str(path) + ": " + str(obj)

	def scan_devices(self):
		print "Scanning devices..."

		objects = self.bluez.GetManagedObjects()
		for path, ifaces in self.objs.iteritems():
			self.iface_added(path, ifaces)

	def address_from_path(self, path):
		return path[20:37].replace("_",":")

	def path_from_gatt_path(self, gatt_path):
		return gatt_path[0:38]

	def process_dev(self, path, dev):
		found_new_device = False
		dev_uuids = dev["UUIDs"]
		dev_addr = dev["Address"]

		if (dev_uuids != None):
			for uuid in dev_uuids:
				print uuid
				# Add interface to dictionary if it has our UUID
				if (uuid == SONAR_SVC_UUID):
					self.devices[dev_addr] = Bluetooth_Device(dev_addr)
					self.devices[dev_addr].object = self.find_device_in_objects(dev_addr)
					self.devices[dev_addr].path = path
					found_new_device = True
					if (True): # Print Stuff
						print "******************"
						print "Device: " + str(self.devices[dev_addr])
						print "Address: " + str(self.devices[dev_addr].address)
						print "Object: " + str(self.devices[dev_addr].object)
						print "Path: " + str(self.devices[dev_addr].path)
						print "******************"
		return found_new_device

	def process_svc(self, path, svc):
		print "process_svc"

		address = self.address_from_path(path)
		if svc["UUID"] == SONAR_SVC_UUID:
			if not(address in self.devices.keys()):
				self.devices[address] = Bluetooth_Device(address)
				self.devices[address].path = self.path_from_gatt_path(path)
				self.devices[dev_addr].object = self.find_device_in_objects(address)
			self.devices[address].svc_path = path

	def process_chrc(self, path, chrc):
		print "process_chrc"
		address = self.address_from_path(path)

		if chrc["UUID"] == DIST_CHRC_UUID:
			if not(address in self.devices.keys()):
				self.devices[address] = Bluetooth_Device(address)
				self.devices[address].path = self.path_from_gatt_path(path)
				self.devices[dev_addr].object = self.find_device_in_objects(address)
			self.devices[address].svc_path = path

	def iface_removed(self, path, interfaces):
		print "One of our sensors was removed"
		print "path: " + str(path)
		print "interfaces" + str(interfaces)

if __name__ == '__main__':
	print "self test..."

	DBusGMainLoop(set_as_default=True)
	global mainloop
	mainloop = GObject.MainLoop()
	
	a = BluetoothController(SystemBus())
	a.sensors = SensorDB()
	a.reg_sig()

	def test_new_dev_cb():
		for dev in a.devices.keys():
			if dev in sensors:
				continue
			else:
				sensors[dev] = Sensor(dev)
				print dev
				a.setup_new_sensor(sensors[dev])
	
		print "Test cb"
		print a.devices.keys()

	def test_new_chrc_cb():
		for dev in a.devices.keys():
			if dev in sensors:
				continue
			else:
				sensors[dev] = Sensor(dev)
				print dev
				a.setup_new_sensor(sensors[dev])
	
		print "Test cb"
		print a.devices.keys()

	a.new_dev_cb = test_new_dev_cb
	a.new_chrc_cb = test_new_chrc_cb

	try:
		a.start_discovery()
	except Exception as e:
		print e

	mainloop.run()


