
#!/usr/bin/env python
import sys, os
import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import Gst, GObject, Gtk

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import GdkX11, GstVideo

class VideoPlayer(object):
	def __init__(self, window1):
		print "creating video"
		self.movie_window = Gtk.DrawingArea()
		self.window1 = window1

		self.player = Gst.ElementFactory.make("playbin", "player")
		self.player.set_property("uri", "http://192.168.3.14:8080/?action=stream")

		bus = self.player.get_bus()
		bus.add_signal_watch()
		bus.enable_sync_message_emission()
		bus.connect("message", self.on_message)
		bus.connect("sync-message::element", self.on_sync_message)

	def on_message(self, bus, message):
		a = 0
		'''
		t = message.type
		if t == Gst.MessageType.EOS:
			print "???"
			self.player.set_state(Gst.State.NULL)
		elif t == Gst.MessageType.ERROR:
			self.player.set_state(Gst.State.NULL)
			err, debug = message.parse_error()
			print "Error: %s" % err, debug
			self.button.set_label("Start")
		'''
		
	def on_sync_message(self, bus, message):
		print "On sync message"
		if message.get_structure().get_name() == 'prepare-window-handle':
			imagesink = message.src
			imagesink.set_property("force-aspect-ratio", True)
			imagesink.set_window_handle(self.window1.get_property('window').get_xid())
			self.imagesink = imagesink

	def start_video(self):
		self.player.set_state(Gst.State.PLAYING)

	def stop_video(self):
		self.player.set_state(Gst.State.PAUSED)
