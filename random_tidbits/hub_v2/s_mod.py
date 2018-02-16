from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, StringProperty
class Sensor(Widget):
	distance = NumericProperty(0)
	address = StringProperty()

	'''
	def __init__(self, addr=None):
		#self.address = addr
		#self.distance = None
		print "Creating sensor w/ address: " + str(addr)
		return
	'''
	
	def update_value_cb(self, val):
		self.value = val