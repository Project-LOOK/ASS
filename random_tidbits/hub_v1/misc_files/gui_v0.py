#!/usr/bin/env python

# example drawingarea.py

############  graphics Imports ################ 
import pygtk
pygtk.require('2.0')
import gtk
import operator
import time
import string
############  End graphics imports ############ 


############  Bluetooth Imports ################ 
import bluezutils
import dbus
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject
import sys
from dbus.mainloop.glib import DBusGMainLoop
############  End bluetooth imports ############ 

import math

############  Bluetooth GLOBAL declarations ###############
distance = 0

bus = None
mainloop = None

BLUEZ_SERVICE_NAME = 'org.bluez'
DBUS_OM_IFACE =      'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE =    'org.freedesktop.DBus.Properties'

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE =    'org.bluez.GattCharacteristic1'

DEV_ADDR = "DC:D3:01:DA:2D:3E"
SONAR_SVC_UUID =        '19b10010-e8f2-537e-4f6c-d104768a1214'
DIST_MSRMT_UUID =      '19b10012-e8f2-537e-4f6c-d104768a1214'

# The objects that we interact with.
ble_device = None
dist_svc = None
dist_msrmt_chrc = None

global SIN_9_DEG 
SIN_9_DEG = math.sin(math.radians(9))
COS_9_DEG = math.cos(math.radians(9))
global RADIUS
RADIUS = 2
global LAST_FEW
LAST_FEW = [0,0,0,0,0,0,0,0,0,0]

############  End Bluetooth GLOBAL declarations ############


###############  Class Definition #########################
class DrawingAreaExample:
    def __init__(self):
        # Set up the main loop.
        DBusGMainLoop(set_as_default=True)
        global bus
        bus = dbus.SystemBus()
        global mainloop
        mainloop = GObject.MainLoop()

        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("Sensor Hub")
        window.connect("destroy", lambda w: mainloop.quit())
        self.area = gtk.DrawingArea()
        self.area.set_size_request(100, 300)
        self.pangolayout = self.area.create_pango_layout("")
        self.table = gtk.Table(2,3)
        self.hruler = gtk.HRuler()
        self.vruler = gtk.VRuler()
        self.hruler.set_range(0, 400, 0, 400)
        self.vruler.set_range(0, 300, 0, 300)
        self.img = gtk.Image()
        self.img.set_from_file("car.png")

        self.table.attach(self.hruler, 1, 3, 0, 1, yoptions=0)
        self.table.attach(self.vruler, 0, 1, 1, 2, xoptions=0)
        self.table.attach(self.area, 1, 2, 1, 2)
        self.table.attach(self.img, 2, 3, 1, 2)
        self.img.show()
        window.add(self.table)
        self.area.connect("expose-event", self.area_expose_cb)

        def motion_notify(obj, event):
            return obj.emit("motion_notify_event", event)
        
        def val_cb(adj, ruler, horiz):
            return

        def size_allocate_cb(wid, allocation):
             return

        self.area.show()
        self.hruler.show()
        self.vruler.show()
        self.table.show()
        window.show()

    ##########  DrawingAreaExample -> internal functions #############
    def area_expose_cb(self, area, event):
        self.style = self.area.get_style()
        self.gc = self.style.fg_gc[gtk.STATE_NORMAL]
        self.draw_polygon(200, 200)
        self.draw_rgb_image(110, 200)
        return True

    def draw_polygon(self, x, y):
        self.points = [(x+40,y+70),
                  (x+30,y+30), (x+50,y+40)]
        self.tri = self.area.window.draw_polygon(self.gc, True, self.points)

        self.area.window.draw_layout(self.gc, x+5, y+80, self.pangolayout)

        return

    def draw_rgb_image(self, x, y):
        b = 80*3*80*['\0']
        for i in range(80):
            for j in range(80):
                b[3*80*i+3*j] = chr(255-3*i)
                b[3*80*i+3*j+1] = chr(255-3*abs(i-j))
                b[3*80*i+3*j+2] = chr(255-3*j)
        buff = string.join(b, '')
        self.area.window.draw_rgb_image(self.gc, x, y, 80, 80,
                                 gtk.gdk.RGB_DITHER_NONE, buff, 80*3)
        self.pangolayout.set_text("RGB Image")
        self.area.window.draw_layout(self.gc, x+5, y+80, self.pangolayout)
        return


    def update_triangle(self, val):
        val = max(100 - val, 0)/2
        LAST_FEW[0] = LAST_FEW[1]
        LAST_FEW[1] = LAST_FEW[2]
        LAST_FEW[2] = LAST_FEW[3]
        LAST_FEW[3] = LAST_FEW[4]
        LAST_FEW[4] = LAST_FEW[5]
        LAST_FEW[5] = LAST_FEW[6]
        LAST_FEW[6] = LAST_FEW[7]
        LAST_FEW[7] = LAST_FEW[8]
        LAST_FEW[8] = LAST_FEW[9]
        LAST_FEW[9] = val
        average = (LAST_FEW[0]+LAST_FEW[1]+LAST_FEW[2]+LAST_FEW[3]+LAST_FEW[4])/5

        origin = self.points[0]
        xc = 100
        yc = 100
        x1 = int(xc-RADIUS*val*COS_9_DEG)
        y1 = int(yc+RADIUS*val*SIN_9_DEG)
        x2 = int(xc-RADIUS*val*COS_9_DEG)
        y2 = int(yc-RADIUS*val*SIN_9_DEG)
 

        #self.points[2] = origin - 
        #print(self.points)
        #help(self.area.window)

        self.points = [(xc,yc), (x1, y1), (x2, y2)]
        self.area.window.clear()

        self.gc.set_foreground(gtk.gdk.Color(0, 65535, 0))
        self.gc.set_background(gtk.gdk.Color(0, 65535, 0))
        self.area.window.draw_polygon(self.gc, True, self.points)
        self.area.window.draw_layout(self.gc, xc+5, yc+80, self.pangolayout)
        return


    def on_destroy(self, widget=None, *data):
        mainloop.go()
        # return True --> no, don't close

        messagedialog = gtk.MessageDialog(parent=self, flags= gtk.DIALOG_MODAL & gtk.DIALOG_DESTROY_WITH_PARENT, 
                                          type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_OK_CANCEL, message_format="Click on 'Cancel' to leave the application open.")
        messagedialog.show_all()
        result=messagedialog.run()
        messagedialog.destroy()
        if result==gtk.RESPONSE_CANCEL:
            return True
        return False
    ##########  END DrawingAreaExample -> internal functions #########
################  END DrawingAreaExample Definition ##################

################  Bluetooth internal functions ########################
def generic_error_cb(error):
    print('D-Bus call failed: ' + str(error))
    mainloop.quit()

def dist_msrmt_start_notify_cb():
    print('Distance Measurement notifications enabled')

def dist_msrmt_changed_cb(iface, changed_props, invalidated_props):

    if iface != GATT_CHRC_IFACE:
        return

    if not len(changed_props):
        return

    value = changed_props.get('Value', None)
    if not value:
        return

    dist_msrmt = value[0]
    print('\tDistance: ' + str(int(dist_msrmt*2)))

    # Update triangle
    GUI.update_triangle(dist_msrmt)

def start_client():

    # Listen to PropertiesChanged signals from the Heart Measurement
    # Characteristic.
    dist_msrmt_prop_iface = dbus.Interface(dist_msrmt_chrc[0], DBUS_PROP_IFACE)
    dist_msrmt_prop_iface.connect_to_signal("PropertiesChanged",
                                          dist_msrmt_changed_cb)

    # Subscribe to Heart Rate Measurement notifications.
    dist_msrmt_chrc[0].StartNotify(reply_handler=dist_msrmt_start_notify_cb,
                                 error_handler=generic_error_cb,
                                 dbus_interface=GATT_CHRC_IFACE)
    #gtk.main_quit()

def process_chrc(chrc_path):
    chrc = bus.get_object(BLUEZ_SERVICE_NAME, chrc_path)
    chrc_props = chrc.GetAll(GATT_CHRC_IFACE,
                             dbus_interface=DBUS_PROP_IFACE)

    uuid = chrc_props['UUID']

    if uuid == DIST_MSRMT_UUID:
        global dist_msrmt_chrc
        dist_msrmt_chrc = (chrc, chrc_props)
    else:
        print('Unrecognized characteristic: ' + uuid)

    return True

def process_dist_svc(service_path, chrc_paths):
    service = bus.get_object(BLUEZ_SERVICE_NAME, service_path)
    service_props = service.GetAll(GATT_SERVICE_IFACE,
                                   dbus_interface=DBUS_PROP_IFACE)

    uuid = service_props['UUID']

    if uuid != SONAR_SVC_UUID:
        return False

    print('Heart Rate Service found: ' + service_path)

    # Process the characteristics.
    for chrc_path in chrc_paths:
        print(chrc_path)
        process_chrc(chrc_path)

    global dist_svc
    dist_svc = (service, service_props, service_path)

    return True


def interfaces_removed_cb(object_path, interfaces):
    if not dist_svc:
        return

    if object_path == dist_svc[2]:
        print('Service was removed')
        mainloop.quit()
##################  END Bluetooth nternal functions ###################

##################  Added functions #################


def connect_ble():
    # Connect to our adapter
    ble_device = bluezutils.find_device(DEV_ADDR)
    ble_device.Connect()
    return ble_device

def disconnect_ble(ble_device):
    ble_device.Disconnect()
    return

##################  Added functions #################

##################  END  Main Loop ###################
def main():
    LAST_FEW = [0,0,0,0,0]
     # Set up the main loop.
    DBusGMainLoop(set_as_default=True)
    global bus
    bus = dbus.SystemBus()
    global mainloop
    mainloop = GObject.MainLoop()

    # Pobably needs try / catch
    ble_device = connect_ble()
    
    om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'), DBUS_OM_IFACE)
    om.connect_to_signal('InterfacesRemoved', interfaces_removed_cb)


    print('Getting objects...')
    objects = om.GetManagedObjects()
    chrcs = []

    # List characteristics found
    for path, interfaces in objects.items():
        if GATT_CHRC_IFACE not in interfaces.keys():
            continue
        chrcs.append(path)

    # List sevices found
    for path, interfaces in objects.items():
        if GATT_SERVICE_IFACE not in interfaces.keys():
            continue

        chrc_paths = [d for d in chrcs if d.startswith(path + "/")]

        if process_dist_svc(path, chrc_paths):
            break

    if not dist_svc:
        print('No Heart Rate Service found')
        sys.exit(1)

    start_client()

    # Setup the GUI
    global GUI
    GUI = DrawingAreaExample()
    
    # Start the program
    mainloop.run()
    
    # Cleanup
    disconnect_ble(ble_device)

##################  END Main Loop ###################

if __name__ == "__main__":
    main()
