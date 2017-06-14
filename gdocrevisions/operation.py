from element import Character


def getOperation(operation_raw, revision):
    """
    Factory method that returns Operation or subclass instance
    takes as input a single dict with change info
    """
    operation_types = {
        'is': InsertString,
        'ds': DeleteString,
        'mlti': MultiOperation,
    }
    operation = operation_types.get(operation_raw['ty']) or Operation
    return operation(operation_raw, revision)


class Operation(object):
    """
    Base Operation class
    Represents action(s) that occur as part of a revision
    """
    def __init__(self, operation_raw, revision):
        """
        operation_raw is a dictionary of raw operation metadata
        """
        self.raw = operation_raw
        self.type = 'operation'
        self.revision = revision

    def apply(self, elements):
        """
        elements is a list of Element instances
        """
        pass


class InsertString(Operation):
    """
    Operation subclass representing an "Insert String" operation
    """
    def __init__(self, operation_raw, revision):
        super(InsertString, self).__init__(operation_raw, revision)
        self.string = operation_raw['s']
        self.start_index = operation_raw['ibi']
        self.type = 'insert string'
        self.elements = [Character(self.revision, char) for char in self.string]

    def apply(self, elements):
        """
        Insert string into document at specified index
        """
        for i,element in enumerate(self.elements):
            elements.insert(self.start_index-1+i, element)


class DeleteString(Operation):
    """
    Operation subclass representing a "Delete String" operation
    """
    def __init__(self, operation_raw, revision):
        super(DeleteString, self).__init__(operation_raw, revision)
        self.start_index = operation_raw['si']
        self.end_index = operation_raw['ei']
        self.type = 'delete string'

    def apply(self, elements):
        """
        Delete string from document between specified indices
        """
        del elements[self.start_index-1:self.end_index]


class MultiOperation(Operation):
    """
    Operation subclass representing a "Multiple Operation" operation
    Contains an array of Operation objects
    """
    def __init__(self, operation_raw, revision):
        super(MultiOperation, self).__init__(operation_raw, revision)
        self.suboperations = [getOperation(suboperation_raw, revision) for suboperation_raw in operation_raw['mts']]
        self.type = 'multiple operations'

    def apply(self, elements):
        """
        Apply each of the suboperations comprising the MultiOperation
        """
        for suboperation in self.suboperations:
            self.suboperation.apply(elements)

