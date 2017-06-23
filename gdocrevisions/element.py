class Element(object):
	"""
	Base Element class. 
	Is a list element in a document's content attribute.
	Associated with a revision
	"""
	__slots__ = ('revision')
	def __init__(self, revision):
		self.revision = revision

	def render(self):
		return ""


class Character(Element):
	"""
	Character element
	Represents a single character
	"""
	__slots__ = ('revision','char')
	def __init__(self, char, revision):
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
	__slots__ = ()
	def __init__(self):
		pass
