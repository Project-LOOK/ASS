
class Page(object):
	data = "old_data"
	def __init__(self, page, name=None):
		self.page = page
		self.name = name
		print("Creating super " + str(self.name) + " page")

	def load(self):
		print("Loading " + str(self.name) + " page")
		print("DATA: " + self.data)

	def unload(self):
		print("Unoading " + str(self.name) + " page")

class MenuPage(Page):
	def __init__(self, page, name=None):
		print("creating sub Menupage")
		super(MenuPage, self).__init__(page, name)
	def unload(self):
		print("menu sub Unoading " + str(self.name) + " page")

class NewPage(Page):
	def unload(self):
		print("new - sub Unoading " + str(self.name) + " page")
		print("DATA: " + self.data)

if __name__ == '__main__':
	print(Page.data)
	Page.data = "new_data"
	print(Page.data)
	print("")

	obj1 = MenuPage("page1", "p1_nm")
	obj1.load()
	obj1.unload()
	print("")

	Page.data = "NuNU"
	obj2 = MenuPage("page2", "p2_nm")
	obj2.load()
	obj2.unload()
	print("")

	obj3 = NewPage("page3", "p3_nm")
	obj3.load()
	obj3.unload()
