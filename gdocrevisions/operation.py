from element import Character


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

    def apply(self, elements):
        """
        elements is a list of Element instances
        """
        pass

    def iter_operations(self):
        yield self

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

    def apply(self, elements):
        """
        Delete string from document between specified indices
        """
        for i in range(self.end_index-self.start_index+1):
            elements.pop(self.start_index-1)


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
