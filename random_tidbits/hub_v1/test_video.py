#!/usr/bin/env python
import sys, os
import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import Gst, GObject, Gtk

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import GdkX11, GstVideo

class Vid_Player(object):
	def __init__(self, window1):
		self.movie_window = Gtk.DrawingArea()
		self.window1 = window1
		#self.gst_element = Gst.ElementFactory.find("playbin")
		#print self.gst_element

		#self.player = self.gst_element.make("playbin", "player")
		self.player = Gst.ElementFactory.make("playbin", "player")
		print self.player
		bus = self.player.get_bus()
		bus.add_signal_watch()
		print "added_signal"
		bus.enable_sync_message_emission()
		bus.connect("message", self.on_message)
		print "conn_1"
		bus.connect("sync-message::element", self.on_sync_message)
		print "conn_2"
		self.player.set_property("uri", "http://192.168.3.14:8080/?action=stream")

	def start_stop(self, w):
		print "Start/stop"
		if self.button.get_label() == "Start":
			filepath = self.entry.get_text().strip()
			print filepath
			print os.path.isfile(filepath)
			if (True):
			#if os.path.isfile(filepath):
				print "real path"
				print os.path.realpath(filepath)
				print "final_path"
				filepath = os.path.realpath(filepath)
				self.button.set_label("Stop")
				#self.player.set_property("uri", "file://" + filepath)
				self.player.set_property("uri", "http://192.168.3.14:8080/?action=stream")
				self.player.set_state(Gst.State.PLAYING)
			else:
				self.player.set_state(Gst.State.NULL)
				self.button.set_label("Start")


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
			print message.src
			imagesink = message.src
			imagesink.set_property("force-aspect-ratio", True)
			#print "movie_window: " + str(self.movie_window)
			#print "m-w poperty: " + str(self.movie_window.get_property('window'))
			#print "m-w prop xid: " + str(self.window.get_property('window').get_xid())
			
			#imagesink.set_window_handle(self.movie_window.get_property('window').get_xid())
			imagesink.set_window_handle(self.window1.get_property('window').get_xid())
			self.imagesink = imagesink
			print "Image sink ***************"
			print imagesink

	def start_video(self):
		self.player.set_state(Gst.State.PLAYING)

	def stop_video(self):
		self.player.set_state(Gst.State.NULL)

#GObject.threads_init()
#Gst.init(None)
#GTK_Main()
#Gtk.main()