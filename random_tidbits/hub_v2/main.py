# Look imports
from bt_ctrl import Bluetooth_Controller
#from gui import Hub_gui
from s_mod import Sensor
from pydbus import SystemBus
from ctrl import Controller

# Kivy imports
from kivy.lang import Builder
from kivy.app import App
from kivy.core.video import Video
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty

class RootWidget(FloatLayout):
    carousel = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)


class LookApp(App):
    def enter_sensor_menu(self, btn):
		print "Get Sensor"
		self.bt.start_discovery()

    def build(self):
    	root = RootWidget()
    	self.bt = Bluetooth_Controller()

    	slide2 = root.ids['sld2']
    	s = Sensor()
    	slide2.add_widget(s)

    	slide1 = root.ids['sld1']
    	add_s_btn = root.ids['add_s']
    	add_s_btn.bind(on_release=self.enter_sensor_menu)
    	print add_s_btn.text

    	#slide.text = 'abc'


        return root

def main():
	
	print "Main"
	ctrl = Controller()
	
	#our_gui = Hub_gui()

	print "setting handlers"
	LookApp().run()

if __name__ == '__main__':
    main()