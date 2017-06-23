from element import Character

class Suboperation(object):
    """
    Base Suboperation class
    Represents action that are associated with single Element
    """
    __slots__ = ('element')
    def __init__(self, element):
        """
        Arguments:
            element (Element): element associated with this suboperation
        """
        self.element = element

    @property
    def type(self):
        return self.__class__.__name__

    def apply(self, elements):
        """
        Apply this suboperation to document content elements
        """
        pass

    def undo(self, elements):
        """
        Undo this suboperation from document content elements
        """
        pass


class InsertElement(Suboperation):
    """
    Insert Character Suboperation class
    """
    __slots__ = ('index','element')
    def __init__(self, index, element):
        """
        Arguments:
            index (int): document index (1-indexed) where insertion occurs
            element (Element): element to insert
        """
        self.index = index
        self.element = element

    def apply(self, elements):
        """
        Apply this insertion suboperation to document content elements
        """
        elements.insert(self.index-1,self.element)

    def undo(self, elements):
        """
        Undo this insertion suboperation from document content elements
        """
        elements.pop(self.index-1)


class DeleteElement(Suboperation):
    """
    Delete Character Suboperation class
    """
    __slots__ = ('index', 'element')
    def __init__(self, index):
        """
        Arguments:
            index (int): document index (1-indexed) where deletion occurs
        """
        self.index = index
        # this gets populated on first use of apply
        self.element = None

    def apply(self, elements):
        """
        Apply this deletion suboperation to docuement content elements
        Also save the element that was deleted in the suboperation's element attribute
        """
        self.element = elements.pop(self.index-1)

    def undo(self, elements):
        """
        Undo this deletion suboperation from document content elements
        """
        elements.insert(self.index-1,self.element)
