import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject

class TestDraw:
	def __init__(self):

		self.builder = Gtk.Builder.new_from_file("demo1.glade")
		self.handlers = {"on_window1_delete_event": self.quit,
						 "on_onButton_clicked": self.on_clicked,
						 "on_offButton_clicked": self.off_clicked,
						 "on_quitButton_clicked": self.quit,
						 "draw": self.on_draw
						}
		self.builder.connect_signals(self.handlers)


		self.canvases = []
		self.canvases.append(self.builder.get_object("da1"))
		self.canvases.append(self.builder.get_object("da2"))
		self.canvases.append(self.builder.get_object("da3"))
		self.canvases.append(self.builder.get_object("da4"))
		self.canvases.append(self.builder.get_object("da5"))
		self.canvases.append(self.builder.get_object("da6"))

		angs = [3.14, -3.14/2, 0, 3.14, 3.14/2, 0]
		i = 0
		for canvas in self.canvases:
			canvas.light = False
			canvas.ang2 = angs[i]
			i = i+1

		self.overlay1 = self.builder.get_object("over1")
		self.image = self.builder.get_object("img1")
		self.grid = self.builder.get_object("grid1")


	def quit(*args):
		print("QUIT")
		mainloop.quit()

	def on_clicked(self, btn):
		for canvas in self.canvases:
			canvas.light = True
			canvas.queue_draw()
		print("\n")
		
	def off_clicked(self, btn):
		for canvas in self.canvases:
			canvas.light = False
			canvas.queue_draw()
		print("\n")
		
	def on_draw(self, drawing_area, cr):
		w = drawing_area.get_allocated_width()
		h = drawing_area.get_allocated_height()
		print("w: " + str(w) + ", h: " + str(h) +
			 ", ang2: " + str(drawing_area.ang2))

		size = min(w,h)
		
		if drawing_area.light:
			cr.set_source_rgb(.5, 1, .2)
		else:
			cr.set_source_rgb(0.2, .5, 1.0)
		
		#cr.arc(  x,    y,     r, rad1, rad2)
		cr.arc(.5*w, .5*h, .3*size, drawing_area.ang2-3.14/8, drawing_area.ang2+3.14/8)
		cr.line_to(.5*w, .5*h)
		cr.fill()


def main():
	global mainloop
	mainloop = GObject.MainLoop()

	my_draw = TestDraw()
	mainloop.run()

if __name__ == '__main__':
	main()