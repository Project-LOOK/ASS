# Look imports
import bluezutils

import dbus.service

# Kivy imports
from kivy.lang import Builder
from kivy.app import App
from kivy.core.video import Video
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty

from dbus.mainloop.glib import DBusGMainLoop

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

def new_iface(self, path, interfaces=None):
        print "Found new iface"

class RootWidget(FloatLayout):
    carousel = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.setup_bt()


    def setup_bt(self):
        DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        self.adapter = bluezutils.find_adapter()
        print "Adapter: " + str(self.adapter)
        self.manager = dbus.Interface(self.bus.get_object("org.bluez", "/"),
                "org.freedesktop.DBus.ObjectManager")
        #self.manager.connect_to_signal("InterfacesAdded", self.new_iface)
        self.bus.add_signal_receiver(new_iface, bus_name="org.bluez",
            dbus_interface="org.freedesktop.DBus.ObjectManager",
            signal_name="InterfacesAdded")
        
        self.adapter.StartDiscovery()
        print "Manager: " + str(self.manager)


class LookApp(App):

    def enter_sensor_menu(self, btn):
        
        print "Get Sensor..."
        #self.adapter.StartDiscovery()


    def build(self):

        #self.adapter.StartDiscovery()

     	root = RootWidget()

    	slide1 = root.ids['sld1']
    	add_s_btn = root.ids['add_s']
    	add_s_btn.bind(on_release=self.enter_sensor_menu)
    	print add_s_btn.text

        return root

def main():
	print "Main"
	LookApp().run()

if __name__ == '__main__':
    main()