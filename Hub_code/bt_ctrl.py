# Profile
# 	 ^---Service
#   	    ^---Characteristic

from sensor_db import SensorDB, Sensor
from pydbus import SystemBus, Variant
import time
import sys
import threading
from dbus.mainloop.glib import DBusGMainLoop

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject

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

UUIDs = ['19b10012-e8f2-537e-4f6c-d104768a1214',
		 '19b10010-e8f2-537e-4f6c-d104768a1214', 
		 '19b10011-e8f2-537e-4f6c-d104768a1214']

class BluetoothController:
	def __init__(self, sys_bus, devices=None):
		self.bus = sys_bus
		self.bluez = self.bus.get(BLUEZ_SVC_NAME, '/')
		self.adapter = self.find_adapter()
		self.bluez.InterfacesAdded.connect(self._iface_added)
		self.bluez.InterfacesRemoved.connect(self._iface_removed)
		self._observer = None
		if devices == None:
			self.devices = SensorDB()
		else:
			self.devices = devices

	def find_adapter(self, pattern=None):
		objs = self.bluez.GetManagedObjects()
		for path, ifaces in objs.iteritems():
			adapter = ifaces.get(ADAPTER_IFACE)
			if adapter is None:
				continue
			if not pattern or pattern == adapter["Address"] or path.endswith(pattern):
				obj = self.bus.get(BLUEZ_SVC_NAME, path)
				#print "Found Adapter: " + obj.Get("org.bluez.Adapter1", "Name")
				return obj
		raise Exception("Bluetooth adapter not found")

	def check_discovery(self):
		discovering = self.adapter.Get("org.bluez.Adapter1", "Discovering")
		return discovering

	def start_discovery(self):
		#print("Setting disco filter")
		if not (self.check_discovery()):
			UUIDs_Variant = Variant('as', UUIDs)
			self.adapter.SetDiscoveryFilter({'UUIDs': UUIDs_Variant})
			#print("Starting disco")
			self.adapter.StartDiscovery()
		#print "Discovery on"

	def stop_discovery(self):
		#print("disco off")
		self.adapter.StopDiscovery()

	def scan_devices(self):
		#print "Scanning devices..."
		objects = self.bluez.GetManagedObjects()
		for path, ifaces in objects.iteritems():
			if GATT_CHRC_IFACE in ifaces.keys():
				self._process_chrc(path, ifaces[GATT_CHRC_IFACE])

			elif GATT_SVC_IFACE in ifaces.keys():
				self._process_svc(path, ifaces[GATT_SVC_IFACE])

			elif DEVICE_IFACE in ifaces.keys():
				self._process_dev(path, ifaces[DEVICE_IFACE])

	def connect_device(self, dev): 
		#print "Connecting to sensor: " + str(dev.name)
		if not(dev.object.Get('org.bluez.Device1', 'Connected')):
			work_thread = threading.Thread(group=None, target=dev.object['org.bluez.Device1'].Connect)
			work_thread.start()

	def disconnect_device(self, dev):
		print("Disconnect device **STUB**")

	def notify_on(self, dev):
		#print "Enabling notifications..."
		self.bus.subscribe(iface=DBUS_PROP_IFACE,
                      signal='PropertiesChanged',
                      object=dev.chrc_path,
                      signal_fired=self.update_cb)

		chrc = self.bus.get(BLUEZ_SVC_NAME, dev.chrc_path)
		chrc.StartNotify()

	def update_cb(self, adapter, chrc_path, dbus_iface, signal1, prop_tuple):
		address = self._address_from_path(chrc_path)
		if "Value" in prop_tuple[1]:
			value_array = prop_tuple[1]["Value"]
			self.devices[address].value = value_array[0] + 16*value_array[1]

	def notify_off(self, address):
		print("Notify off **STUB**")

	def _iface_added(self, path, obj_dict):
		#print("Ifaces added___ " + str(path))
		address = self._address_from_path(path)
		o_path = self._path_from_gatt_path(path)
		
		if GATT_CHRC_IFACE in obj_dict.keys():
			self.update_device(address=address, path=o_path, chrc_path=path, object=self.bus.get(BLUEZ_SVC_NAME, o_path))

		elif GATT_SVC_IFACE in obj_dict.keys():
			self.update_device(address=address, path=o_path, svc_path=path, object=self.bus.get(BLUEZ_SVC_NAME, o_path))
		
		elif DEVICE_IFACE in obj_dict.keys():
			object=self.bus.get(BLUEZ_SVC_NAME, path)
			self.update_device(address=address, path=path, object=self.bus.get(BLUEZ_SVC_NAME, path))

	def _iface_removed(self, path, interfaces):
		#print("Iface removed: " + str(path))
		address = self._address_from_path(path)

		if address in self.devices.keys():
			print("YES")
			del(self.devices[address])

	def _process_dev(self, path, dev):
		#print("Process dev: " + str(path))
		uuids = dev["UUIDs"]
		address = dev["Address"]
		
		if (uuids != None):
			for uuid in uuids:
				if (uuid == SONAR_SVC_UUID):
					self.update_device(address=address, path=path, object=self.bus.get(BLUEZ_SVC_NAME, path))
					break

	def update_device(self, address, **kwargs):
		#print("update device: " + str(address))
		if(address not in self.devices.keys()):
			self.devices[address] = Sensor(address)

		device = self.devices[address]

		if "path" in kwargs:
			device.path = kwargs["path"]
		if "svc_path" in kwargs:
			device.svc_path = kwargs["svc_path"]
		if "chrc_path" in kwargs:
			device.chrc_path = kwargs["chrc_path"]
		if "object" in kwargs:
			device.object = kwargs["object"]

	def _process_svc(self, path, svc):
		address = self._address_from_path(path)
		if svc["UUID"] == SONAR_SVC_UUID:
			self.update_device(address=address, svc_path=path)

	def _process_chrc(self, path, chrc):
		address = self._address_from_path(path)
		if chrc["UUID"] == DIST_CHRC_UUID:
			self.update_device(address=address, chrc_path=path)

	def _address_from_path(self, path):
		return path[20:37].replace("_",":")

	def _path_from_gatt_path(self, gatt_path):
		return gatt_path[0:37]
