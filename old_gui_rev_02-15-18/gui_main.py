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
        
        origin = self.points[0]
        xc = 100
        yc = 100
        x1 = int(xc-RADIUS*val*COS_9_DEG)
        y1 = int(yc+RADIUS*val*SIN_9_DEG)
        x2 = int(xc-RADIUS*val*COS_9_DEG)
        y2 = int(yc-RADIUS*val*SIN_9_DEG)
 
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



##################  END  Main Loop ###################
def main():
     # Set up the main loop.
    DBusGMainLoop(set_as_default=True)
    global bus
    bus = dbus.SystemBus()
    global mainloop
    mainloop = GObject.MainLoop()

    # Setup the GUI
    global GUI
    GUI = DrawingAreaExample()
    
    # Start the program
    mainloop.run()
    

##################  END Main Loop ###################

if __name__ == "__main__":
    main()
