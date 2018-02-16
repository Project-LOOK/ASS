import pydbus
from pydbus import SystemBus
from timeout import timeout
import time
import sys

BT_ADAPTOR_HINT = None 
BLUEZ_SVC_NAME = 'org.bluez'
ADAPTER_IFACE = 'org.bluez.Adapter1'
DEVICE_INTERFACE = 'org.bluez.Device1'

DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE =    'org.bluez.GattCharacteristic1'

DEV_ADDR = "DC:D3:01:DA:2D:3E"
SONAR_SVC_UUID = '19b10010-e8f2-537e-4f6c-d104768a1214'
DIST_MSRMT_UUID = '19b10011-e8f2-537e-4f6c-d104768a1214'


class Bluetooth_Controller:
	def __init__(self, adapter_hint=None):
		self.bus = SystemBus()
		self.bluez = self.bus.get(BLUEZ_SVC_NAME, '/')
		self.objs = self.bluez.GetManagedObjects()
		self.adapter = self.find_adapter_in_objects()

	def find_adapter_in_objects(self, pattern=None):
		for path, ifaces in self.objs.iteritems():
			adapter = ifaces.get(ADAPTER_IFACE)
			if adapter is None:
				continue
			if not pattern or pattern == adapter["Address"] or path.endswith(pattern):
				obj = self.bus.get(BLUEZ_SVC_NAME, path)
				print "Found Adapter: " + obj.Get("org.bluez.Adapter1", "Name")
				return obj
		raise Exception("Bluetooth adapter not found")

	def find_device(self, device_address, adapter_pattern=None):
		return self.find_device_in_objects(self.objs, device_address, adapter_pattern) 

	def find_device_in_objects(self, device_address, adapter_pattern=None):
		path_prefix = ""
		if adapter_pattern:
			adapter = self.find_adapter_in_objects(adapter_pattern)
			path_prefix = adapter.object_path
		for path, ifaces in objects.iteritems():
			device = ifaces.get(DEVICE_INTERFACE)
			if device is None:
				continue
			if (device["Address"] == device_address and
							path.startswith(path_prefix)):
				obj = self.bus.get(BLUEZ_SVC_NAME, path)
				return obj
		raise Exception("Bluetooth device not found")

	def start_discovery(self):
		self.adapter.StartDiscovery()
		print "Discovery on"

	def stop_discovery(self):
		self.adapter.StopDiscovery()

	def check_discovery(self):
		discovering = self.adapter.Get("org.bluez.Adapter1", "Discovering")
		return discovering

	def new_dev_cb(self, path, obj):
		self.cb(path, obj)

	def find_service_in(self):
		print "Finding service"

	def new_iface(self, path, obj):
		print 'obj[org.bluez.Device1][Name]: ' + str(obj['org.bluez.Device1'])
		print 'keys: ' + str(obj['org.bluez.Device1'].keys())
		dict = obj['org.bluez.Device1']
		keys = dict.keys()
		if 'Name' in keys:
			print 'yes'
			if dict['Name'] == 'Sonar Module 1':
				print 'this is our mod'
				self.new_dev_cb(path, obj)
			else:
				print 'not our obj'
		else:
			print "doesn't have name key"
			#self.find_service_in()
		#print "Object: " + str(obj)
		#print "Dictionary: " + str(dict)	

	def reg_sig(self):
		self.bluez.InterfacesAdded.connect(self.new_iface)

# find device matching name
# Get address of device
# Connect to device
# Disconnect from device
# Notify device changes

if __name__ == '__main__':
	print "self test..."

	a = BluezUtil()
	#adapter = a.find_adapter()

	try:
		a.start_discovery()
	except Exception as e:
		print e



	# List devices with correct Name
	#device = a.find_device(DEV_ADDR)

	#device.Connect()

	#print device.GetAll(DBUS_PROP_IFACE)