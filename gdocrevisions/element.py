# constants for suggestion status
SUGGEST_INSERT = 1
SUGGEST_DELETE = -1
SUGGEST_NONE = 0


class Element(object):
    """
    Base Element class. 
    Is a list element in a document's content attribute.
    Associated with a revision
    Suggest attribute denotes whether element is suggested for insertion (1), suggested for
    deletion (-1), or not part of a suggestion (0).
    """
    __slots__ = ('revision', 'suggest')

    def __init__(self, revision, suggest=SUGGEST_NONE):
        self.revision = revision
        self.suggest = suggest

    def render(self):
        return ""


class Character(Element):
    """
    Character element
    Represents a single character
    """
    __slots__ = ('char', 'revision_insert', 'revision_delete', 'suggest')

    def __init__(self, char, revision, suggest=SUGGEST_NONE):
        # character string
        self.char = char
        # revision in which element is created
        self.revision_insert = revision
        # placeholder for revision in which element is deleted
        self.revision_delete = None
        # indicator whether this is a suggestion, can take values -1, 0, or 1
        self.suggest = suggest

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
        if self.suggest == SUGGEST_DELETE:
            return u'{}\u0336'.format(self.char)
        elif self.suggest == SUGGEST_INSERT:
            return self.char.upper()
        else:
            return self.char


class EndOfBody(Element):
    """
    Dummy element indicating end of document body
    Separates main content from footnote text
    """
    __slots__ = ()

    def __init__(self):
        pass
