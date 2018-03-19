import inspect

class Page(object):
	def __init__(self, page=None, name=None):
		print("Super init called...")
		self.page = page
		self.name = name

	def load(self):
		print("S-L")

	def unload(self):
		print("S-U")

class SubPage(Page):
	def __new__(self, page=None, name=None):
		print("Super new called...")

	def unload(self):
		print("U")

if __name__ == '__main__':
	
	obj1 = Page()
	#("page1", "p1_nm")
	obj1.load()
	obj1.unload()

	obj2 = SubPage("page2", "p2_nm")
	obj2.load()
	obj2.unload()

	t1 = inspect.getmro(Page)
	t2 = inspect.getmro(SubPage)

	print("Page: " + str(t1))
	print("Page: " + str(t2))