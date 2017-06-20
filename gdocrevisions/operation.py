from element import Character
from suboperation import InsertElement, DeleteElement


def operation_factory(operation_raw, revision):
    """
    Factory method that returns Operation or subclass instance

    Arguments:
        operation_raw (dict): raw operation data
        revision (Revision): revision instance, which gets associated with any created Element objects
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
        self.type = self.__class__.__name__
        self.revision = revision
        self.suboperations = []

    def apply(self, elements):
        """
        elements is a list of Element instances
        """
        for suboperation in self.suboperations:
            suboperation.apply(elements)

    def iter_operations(self):
        yield self

    def iter_suboperations(self):
        for suboperation in self.suboperations:
            yield suboperation

    def to_dict(self):
        DICT_ATTRIBUTES = [
            'type',
            'revision',
        ]
        return {attr:getattr(self,attr) for attr in DICT_ATTRIBUTES}


class InsertString(Operation):
    """
    Operation subclass representing an "Insert String" operation
    """
    def __init__(self, operation_raw, revision):
        super(InsertString, self).__init__(operation_raw, revision)
        self.string = operation_raw['s']
        self.start_index = operation_raw['ibi']
        # self.elements = [Character(self.revision, char) for char in self.string]
        self.suboperations = [InsertElement(self.start_index+i, Character(char, self.revision)) for i,char in enumerate(self.string)]


class DeleteString(Operation):
    """
    Operation subclass representing a "Delete String" operation
    """
    def __init__(self, operation_raw, revision):
        super(DeleteString, self).__init__(operation_raw, revision)
        self.start_index = operation_raw['si']
        self.end_index = operation_raw['ei']
        self.suboperations = [DeleteElement(self.end_index-i) for i in range(self.end_index-self.start_index+1)]


class MultiOperation(Operation):
    """
    Operation subclass representing a "Multiple Operation" operation
    Contains an array of Operation objects
    """
    def __init__(self, operation_raw, revision):
        super(MultiOperation, self).__init__(operation_raw, revision)
        self.operations = [operation_factory(operation_raw, revision) for operation_raw in operation_raw['mts']]

    def apply(self, elements):
        """
        Apply each of the operations comprising the MultiOperation
        """
        for operation in self.operations:
            self.operation.apply(elements)

    def iter_operations(self):
        """
        Generator that iterates through base operations.
        Does a depth-first search of the operations tree,
        yielding leaf (non-Multioperation) nodes
        """
        for operation in self.operations:
            if hasattr(operation, 'operations'):
                for operation in operation.iter_operations():
                    yield operation
            else:
                yield operation

    def iter_suboperations(self):
        for operation in self.iter_operations():
            for iter_suboperation in operation.iter_suboperations():
                yield suboperation
