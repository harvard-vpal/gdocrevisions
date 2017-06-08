class Element(object):
	"""
	Base Element class. 
	Is a list element in a document's content attribute.
	Associated with a revision
	"""
	def __init__(self, revision):
		self.revision = revision


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

