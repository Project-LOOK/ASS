#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

LightOn = False

def deleted(self, *args):
        return True

def onClicked(button,drawingArea):
    global LightOn
    LightOn = True
    drawingArea.queue_draw()


def offClicked(button,drawingArea):
    global LightOn
    LightOn = False
    drawingArea.queue_draw()


def draw(drawingArea,cr):
    w = drawingArea.get_allocated_width()
    h = drawingArea.get_allocated_height()
    size = min(w,h)

    cr.set_source_rgb(0.0,0.2,0.0)
    cr.paint()

    if LightOn == True:
        cr.set_source_rgb(1.0,0.0,0.0)
    else:
        cr.set_source_rgb(0.2,0.0,0.0)
    cr.arc(0.5*w,0.5*h,0.5*size,0.0,6.3)
    cr.fill()



builder = Gtk.Builder.new_from_file("demo1.glade")

da    = builder.get_object("drawingarea1")

handlers = {
    "on_quitButton_clicked": Gtk.main_quit,
    "on_window1_delete_event" : deleted,
    "on_onButton_clicked": (onClicked,da),
    "on_offButton_clicked": (offClicked,da),
    "on_drawingarea1_draw": draw,
}

builder.connect_signals(handlers)

Gtk.main()
