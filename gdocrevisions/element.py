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
	__slots__ = ('char', 'revision_insert','revision_delete')
	def __init__(self, char, revision):
		# character string
		self.char = char
		# revision in which element is created
		self.revision_insert = revision
		# placeholder for revision in which element is deleted
		self.revision_delete = None

	@property
	def revision(self):
		"""
		Alias for revision_insert attribute
		"""
		return self.revision_insert

	def render(self):
		"""
		Render this element, typically called by content.render()
		"""
		return self.char


class EndOfBody(Element):
	"""
	Dummy element indicating end of document body
	Separates main content from footnote text
	"""
	__slots__ = ()
	def __init__(self):
		pass
