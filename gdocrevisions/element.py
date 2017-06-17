class Element(object):
	"""
	Base Element class. 
	Is a list element in a document's content attribute.
	Associated with a revision
	"""
	def __init__(self, revision):
		self.revision = revision

	def render(self):
		return ""


class Character(Element):
	"""
	Character element
	Represents a single character
	"""
	def __init__(self, revision, char):
		# revision object reference
		self.revision = revision
		# character string
		self.char = char

	def render(self):
		return self.char


class EndOfBody(Element):
	"""
	Dummy element indicating end of document body
	Separates main content from footnote text
	"""
	def __init__(self):
		pass
