#!/usr/bin/env python
0
from sensor_db import SensorDB, Sensor
from bt_ctrl import BluetoothController
from gui import HubGUI
from pydbus import SystemBus

from dbus.mainloop.glib import DBusGMainLoop
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
import sys
import time
import os

PATH = os.path.dirname(os.path.realpath(__file__))

class Controller:
    def __init__(self):
        self.sensors = SensorDB()
        #self.sensors.bind_to(self.db_changed)

        self.sys_bus = SystemBus()

        self.gui_state = None
        """ Possible states are:
            Sensor
            Video
            HUD
            Add
            Remove
        """
        #self.bt.bind_to("new", self.new_sensor)
        self.our_gui = HubGUI(self.sensors)

        self.bt = BluetoothController(self.sys_bus)

        self.our_gui.bind_to("quit", self.quit)

        self.our_gui.HUD.bind_to("load", self.enter_HUD)
        self.our_gui.HUD.bind_to("unload", self.exit_HUD)
        self.our_gui.videoPage.bind_to("load", self.enter_video_page)
        self.our_gui.videoPage.bind_to("unload", self.exit_video_page)
        self.our_gui.sensorPage.bind_to("load", self.enter_sensor_menu)
        self.our_gui.sensorPage.bind_to("unload", self.exit_sensor_menu)       
        self.our_gui.add_menu.bind_to("load", self.enter_add_menu)
        self.our_gui.add_menu.bind_to("unload", self.exit_add_menu)
        self.our_gui.remove_menu.bind_to("load", self.enter_remove_menu)
        self.our_gui.remove_menu.bind_to("unload", self.exit_remove_menu)
        self.our_gui.carousel.reload_current()

        self.our_gui.bind_to("selected", self.sensor_selected)
        self.our_gui.bind_to("removed", self.sensor_removed)
        self.our_gui.bind_to("reconnect", self.sensor_reconnect)

        self.bt.bind_to("found", self.sensor_found)
        self.bt.bind_to("connected", self.sensor_connected)

    def sensor_removed(self, address):
        print("Please remove")
        self.sensors[address].active = False
        self.bt.task_queue.put_nowait(["connect", [address, False]])
        pass

    def sensor_reconnect(self, address):
        self.bt.task_queue.put_nowait(["connect", [address, True]])

    def enter_video_page(self):
        self.gui_state = "Video"

    def exit_video_page(self):
        pass

    def enter_add_menu(self):
        self.gui_state = "Add"

    def exit_add_menu(self):
        self.update_sensor_btns()
        pass

    def enter_remove_menu(self):
        self.gui_state = "Remove"

    def exit_remove_menu(self):
        self.update_sensor_btns()
        pass

    def update_sensor_btns(self):
        btn_items = {}
        for key, value in self.sensors.items():
            btn_items[key] = [value.name, value.connected]
        self.our_gui.sensorPage.items = btn_items

    def sensor_selected(self, name, address, position, canvas):
        print("SENSOR selected")
        sensor = self.sensors[address]
        sensor.position = position
        sensor.canvas = canvas
        print("NAME... = " + str(name))
        sensor.name = name
        sensor.active = True

        self.bt.task_queue.put_nowait(["connect", [sensor.address, True]])
        self.bt.bind_to_value(sensor.address, self.update_value)

    def sensor_found(self, address, state):
        if state:
            if address not in self.sensors.keys():
                self.sensors[address] = Sensor(address)
            self.sensors[address].present = True

        elif address in self.sensors.keys():
            self.sensors[address].present = False

        if self.gui_state == "Sensor":
            btn_items = {}
            for key, value in self.sensors.items():
                btn_items[key] = [value.name, value.connected]
            self.our_gui.sensorPage.items = btn_items

    def sensor_connected(self, address, is_connected):
        if is_connected:
            if address not in self.sensors.keys():
                self.sensors[address] = Sensor(address)
            self.sensors[address].connected = True

        elif address in self.sensors.keys() and (not is_connected):
            self.sensors[address].connected = False

        if self.gui_state == "Sensor":
            btn_items = {}
            for key, value in self.sensors.items():
                btn_items[key] = [value.name, value.connected]
            self.our_gui.sensorPage.items = btn_items
            
        if self.gui_state == "HUD":
            pass

    def enter_sensor_menu(self):
        self.gui_state = "Sensor"
        self.bt.task_queue.put_nowait(["discovery", []])

    
    def exit_sensor_menu(self):
        pass

    def enter_HUD(self):
        self.gui_state = "HUD"
        for sensor in self.sensors.values():
            if sensor.position:
                self.bt.task_queue.put_nowait(["notify", [sensor.address, True]])
           

    def exit_HUD(self):
        self.our_gui.clear_cr()
        for sensor in self.sensors.values():
            if sensor.position:
                print("Start notify: " +str(sensor.address))
                self.bt.task_queue.put_nowait(["notify", [sensor.address, False]])

    def update_value(self, address, value):
        self.sensors[address].value = value

    def quit(self, *args):
        mainloop.quit()

def main():
    DBusGMainLoop(set_as_default=True)
    global mainloop
    mainloop = GObject.MainLoop()
    
    ctrl = Controller()
    
    mainloop.run()

if __name__ == '__main__':
    main()