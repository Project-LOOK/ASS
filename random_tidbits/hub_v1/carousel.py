from kivy.lang import Builder
from kivy.app import App
#from kivy.core.video import Video
#from kivy.clock import Clock

def testbtn(self, touch):
    print "Hello"


look=Builder.load_string('''
#:import os os

Carousel:
    direction: 'right'
    loop: 'True'

    BoxLayout:
        orientation: 'vertical'
        Button:
            text:' Run Me Hard'
            size_hint_y: None
            height:'60dp'
            on_release: os.system("")

    BoxLayout:
        orientation: 'vertical'
        AsyncImage:
            source: 'jup2.jpg'
            allow_stretch:'True'
        Label:
            text: "Sliding in the Settings?"
            size_hint_y: 0.1
''')

class MonAppli(App):

    def build(self):
        return look

MonAppli().run()