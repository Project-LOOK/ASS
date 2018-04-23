#!/usr/bin/env python

from pydbus import SystemBus, Variant
import Queue
import time
import sys
import threading
from dbus.mainloop.glib import DBusGMainLoop

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib

BT_ADAPTOR_HINT = None 
BLUEZ_SVC_NAME = 'org.bluez'
ADAPTER_IFACE = 'org.bluez.Adapter1'
DEVICE_IFACE = 'org.bluez.Device1'

DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

GATT_SVC_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE = 'org.bluez.GattCharacteristic1'

LIDAR_SVC_UUID = '19b10012-e8f2-537e-4f6c-d104768a1214'
SONAR_SVC_UUID = '19b10010-e8f2-537e-4f6c-d104768a1214'
DIST_CHRC_UUID = '19b10011-e8f2-537e-4f6c-d104768a1214'

UUIDs = ['19b10012-e8f2-537e-4f6c-d104768a1214',
         '19b10010-e8f2-537e-4f6c-d104768a1214', 
         '19b10011-e8f2-537e-4f6c-d104768a1214']

class BluetoothSensor(object):
    def __init__(self, address, path):
        self.address = address
        self.path = path
        self._chrc_path = None
        self.object = None
        self._connected = False
        self.pending_connection = False

        self._observers = {"connected": [],
                           "value": []}
                           #"active": []}
    
    @property
    def chrc_path(self):
        return self._chrc_path

    @chrc_path.setter
    def chrc_path(self, path):
        self._chrc_path = path
        self.en_notifications(path)
    
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        print("Value: " + str(new_value))
        self._value = new_value
        self.handle_cb("value", new_value)

    @property
    def connected(self):
        return self._connected

    @connected.setter
    def connected(self, value):
        #print(str(self.address) + ".connected = " + str(value))
        self._connected = value
        self.handle_cb("connected", value)

    def connect(self):
        self.pending_connection = True
        try:
            self.object['org.bluez.Device1'].Connect()
            print(str(self.address) + ": connected.")
        except Exception as err:
            print(str(self.address) + ": connect ERROR: " + str(err))
        finally:
            self.pending_connection = False

    def disconnect(self):
        self.pending_connection = True
        try:
            self.object['org.bluez.Device1'].Disconnect()
            print(str(self.address) + ": disconnected.")
        except Exception as err:
            print(str(self.address) + ": disconnect ERROR: " + str(err))
        finally:
            self.pending_connection = False

    def handle_cb(self, key, value):
        for callback in self._observers[key]:
            callback(self.address, value)

    def on_properties_changed(self, adapter, path, dbus_iface, sig, data):
        """ Watch for dropped connections,
            possibly other properties changed
            data is a tuple containing:
                (Interface="", Properties={}, *Unknown=[])
        """
        iface = data[0]
        properties = data[1]
        if iface == DEVICE_IFACE:
            for key, value in properties.items():
                if key == "Connected":
                    self.connected = value
        elif iface == GATT_CHRC_IFACE:
            for key, value in properties.items():
                if key == "Value":
                    #print("***" + str(key) + ", " + str(value))
                    self.value = value[0] + 256*value[1]

    def en_notifications(self, path):
        # This binds to properties changed...
        self.sys_bus.subscribe(iface=DBUS_PROP_IFACE,
                      signal='PropertiesChanged',
                      object=path,
                      signal_fired=self.on_properties_changed)

    def start_notify(self, bus):
        #print("CHRC: " + str(chrc))
        chrc = bus.get(BLUEZ_SVC_NAME, self.chrc_path)
        try:
            print(str(self.address) + " notifying.")
            chrc.StartNotify()
        except Exception as err:
            print("Unable to start notifying: " + str(self.address) + ", " + str(chrc))

    def stop_notify(self, bus):
        """ Need to put in check to see if already notifying
        """
        chrc = bus.get(BLUEZ_SVC_NAME, self.chrc_path)
        try:
            chrc.StopNotify()
        except Exception as err:
            print("Unable to stop notifying")

    def bind_to(self, key, cb):
        self._observers[key].append(cb)

    def clear_binds(self, key):
        self._observers[key] = []

class BluetoothController:
    def __init__(self, sys_bus=None):
        if sys_bus == None:
            sys_bus = SystemBus()
        self.bus = sys_bus
        BluetoothSensor.sys_bus = sys_bus

        self.bluez = self.bus.get(BLUEZ_SVC_NAME, '/')
        self.adapter = self.find_adapter()
        self.bluez.InterfacesAdded.connect(self._iface_added)
        self.bluez.InterfacesRemoved.connect(self._iface_removed)
        
        self.sensors = []       
        self._observers = {
                           "found": [],
                           "connected": []
                          }

        self.task_handlers = {"connect": self.handle_connect,
                              "notify": self.handle_notify,
                              "discovery": self.handle_discovery
                             }

        self.purge_cache()

        self.task_queue = Queue.Queue()
        self.task_thread = threading.Thread(target=self.bt_monitor)
        self.task_thread.setDaemon(True)
        self.task_thread.start()

    def notify_on(self):
        for device in self.sensors:
            print("notify dev: " + str(device))
            device.start_notify()

    def notify_off(self):
        for device in self.sensors:
            device.stop_notify()

    def bind_to_value(self, address, callback):
        device = self.find_device(address)
        device.bind_to("value", callback)

    def bt_monitor(self):
        while(1):
            key, args = self.task_queue.get()
            self.task_handlers[key](*args)

    def handle_connect(self, address, want_connected):
        device = self.find_device(address)
        if device == None:
            print(str(address) + " not found in devices")
            return
        print("Pending connection? " + str(device.pending_connection))
        if device.pending_connection:
            print(str(address) + " pending connection")
            return
        if want_connected:
            if device.connected:
                print(str(address) + " already connected.")
                return
            else:
                threading.Thread(target=device.connect).start()
                return
        else:
            if device.connected:
                threading.Thread(target=device.disconnect).start()
            else:
                print(str(address) + " already disconnected.")
                return

    def handle_notify(self, address, want_notify):
        device = self.find_device(address)
        if device:
            if want_notify:
                #if device.connected:
                device.start_notify(self.bus)
            else:
                device.stop_notify(self.bus)
        else:
            print("ERROR: handle_notify failed, invalid address. "+ str(address))

    def handle_discovery(self):
        discovering = self.adapter.Get("org.bluez.Adapter1", "Discovering")
        if (not discovering):
            threading.Thread(target=self.start_discovery).start()
        else:
            print("Already discovering...")

    def start_discovery(self):
        self.scan_devices()
        UUIDs_Variant = Variant('as', UUIDs)
        self.adapter.SetDiscoveryFilter({'UUIDs': UUIDs_Variant})
        try:
            self.purge_cache()
            self.adapter.StartDiscovery()
            print("Started disco")
            time.sleep(10)
        except:
            print("Unable to start discovery")
        self.stop_discovery()

    def stop_discovery(self):
        try:
            self.adapter.StopDiscovery()
            print("Stopped disco")
        except:
            print("Unable to stop discovery")
            
    def purge_cache(self):
        objs = self.bluez.GetManagedObjects()
        objs = self.filter_by_uuid_and_iface(objs, SONAR_SVC_UUID, DEVICE_IFACE)

        for path, ifaces in objs.items():
            properties = ifaces[DEVICE_IFACE]
            if (properties["Connected"]):
                continue
            try:
                #print("Purge " + str(path))
                threading.Thread(target=self.adapter.RemoveDevice, args=[path]).start()
            except Exception as err:
                print("Doesn't exist")
                continue
            #del(objs[path])

    def remove_device(self, path):
        """ move thread to here, call add to queue before doing this method
        """
        pass


    def filter_by_uuid_and_iface(self, objects, uuid, iface):
        """ Takes a list of bluetooth objects and returns 
            a subset of our devices
        """
        return_objects = {}
        for path, ifaces in objects.items():
            if iface in ifaces.keys():
                properties = ifaces[iface]
                if "UUIDs" in properties:
                    uuid_list = properties["UUIDs"]
                    if uuid in uuid_list:
                        return_objects[path] = objects[path]
                        continue
                elif "UUID" in properties:
                    if uuid == properties["UUID"]:
                        return_objects[path] = objects[path]
                        #print("Found " + str(path))
                        continue
        return return_objects


    def find_adapter(self, pattern=None):
        objs = self.bluez.GetManagedObjects()
        for path, ifaces in objs.iteritems():
            adapter = ifaces.get(ADAPTER_IFACE)
            if adapter is None:
                continue
            if (not pattern or pattern == adapter["Address"]
                    or path.endswith(pattern)):
                obj = self.bus.get(BLUEZ_SVC_NAME, path)
                return obj
        raise Exception("Bluetooth adapter not found")

    def find_device(self, address):
        for dev in self.sensors:
            if dev.address == address:
                break
        else:
            dev = None
        return dev

    def scan_devices(self, purge=True):
        #print "Scanning devices..."
        if purge:
            self.purge_cache()
        
        objs = self.bluez.GetManagedObjects()
        dev_objs = self.filter_by_uuid_and_iface(objs, SONAR_SVC_UUID, DEVICE_IFACE)
        chrc_objs = self.filter_by_uuid_and_iface(objs, DIST_CHRC_UUID, GATT_CHRC_IFACE)
        
        for path, ifaces in chrc_objs.iteritems():
            address = address_from_path(path)
            device_path = path_from_gatt_path(path)
            chrc_path = path
            self.update_device(address=address, device_path=device_path,
                chrc_path=chrc_path)

        for path, ifaces in dev_objs.iteritems():
            address = address_from_path(path)
            device_path = path_from_gatt_path(path)
            self.update_device(address=address, device_path=device_path)

    def update_device(self, address, device_path, chrc_path=None):
        #print("update device: " + str(address))
        device = self.find_device(address)
        if device == None:
            device = BluetoothSensor(address, device_path)
            device.bind_to("connected", self.on_connection)
            device.object = self.bus.get(BLUEZ_SVC_NAME, device_path)
            device.connected = device.object.Get(DEVICE_IFACE, "Connected")

            self.sensors.append(device)
            self.handle_cb("found", device.address, True)
            device.en_notifications(device_path)
            #print("en_notifications: " + str(kwargs["path"]))

        if chrc_path and (device.chrc_path == None):
            device.chrc_path = chrc_path

    def on_connection(self, address, state):
        self.handle_cb("connected", address, state)

    def _iface_added(self, path, obj_dict):
        #print("IFACE added: " + str(path))
        self.scan_devices(purge=False)

    def _iface_removed(self, path, interfaces):
        address = address_from_path(path)
        device = self.find_device(address)
        if device:
            #print("Iface removed: " + str(path))
            self.sensors.remove(device)
    
    def bind_to(self, key, cb):
        self._observers[key].append(cb)

    def clear_binds(self, key):
        self._observers[key] = []

    def handle_cb(self, key, *args):
        for callback in self._observers[key]:
            GLib.idle_add(callback, *args)

def address_from_path(path):
    return path[20:37].replace("_",":")

def path_from_gatt_path(gatt_path):
    return gatt_path[0:37]
