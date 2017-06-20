from element import Character

class Suboperation(object):
    """
    Base Suboperation class
    Represents action that are associated with single Element
    """
    def __init__(self, element):
        """
        operation_raw is a dictionary of raw operation metadata
        """
        self.element = element

    @property
    def type(self):
        return self.__class__.__name__

    def apply(self, elements):
        """
        elements is a list of Element instances
        """
        pass


class InsertElement(Suboperation):
    """
    Insert Character Suboperation class
    """
    def __init__(self, index, element):
        self.index = index
        self.element = element

    def apply(self, elements):
        elements.insert(self.index-1,self.element)


class DeleteElement(Suboperation):
    """
    Delete Character Suboperation class
    """
    def __init__(self, index):
        self.index = index
        # self.element = element

    def apply(self, elements):
        element = elements.pop(self.index-1)

        # TODO could modify popped element here?
        # would revision need to be passed in then?
