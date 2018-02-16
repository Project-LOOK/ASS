


class Sensor:
	
	def __init__(self, addr=None):
		self.address = addr
		self.value = None
		print "Creating sensor w/ address: " + str(addr)

	def update_value_cb(self, dict1, array1):
		print "UPdate value"
		self.value = val