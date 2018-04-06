from element import Character, SUGGEST_INSERT, SUGGEST_DELETE, SUGGEST_NONE


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
        'iss': InsertStringSuggestion,
        'dss': DeleteStringSuggestion,
        'msfd': MarkStringForDeletion,
        'usfd': UnmarkStringForDeletion,
    }
    operation = operation_types.get(operation_raw['ty']) or Operation
    return operation(operation_raw, revision)


class Operation(object):
    """
    Base Operation class
    Represents action(s) that occur as part of a revision
    """
    __slots__ = ('raw', 'type', 'revision')

    def __init__(self, operation_raw, revision):
        """
        operation_raw is a dictionary of raw operation metadata
        """
        # could remove self.raw (dict) to save memory
        self.raw = operation_raw
        self.type = self.__class__.__name__
        self.revision = revision

    def apply(self, elements):
        """
        Apply this operation to document content elements
        
        Arguments:
            elements (list): list of Elements
        """
        pass

    def iter_operations(self):
        yield self

    def to_dict(self):
        DICT_ATTRIBUTES = [
            'type',
            'revision',
        ]
        return {attr: getattr(self, attr) for attr in DICT_ATTRIBUTES}


class RangeOperation(Operation):
    """
    Generic subclass representing an operation that modifies elements within a particular range
    Range is defined by start and end indexes, and is 1-indexed and inclusive
    e.g. DeleteString with start=1 and end=3 means delete elements 1, 2 and 3 (1-indexed)
    """
    __slots__ = ('raw', 'type', 'revision', 'start_index', 'end_index')

    def __init__(self, operation_raw, revision):
        self.start_index = operation_raw['si']  # 1-indexed
        self.end_index = operation_raw['ei']  # 1-indexed
        super(RangeOperation, self).__init__(operation_raw, revision)


class InsertString(Operation):
    """
    Operation subclass representing an "Insert String" operation
    New elements are inserted at position defined by start_index (1-indexed)
    e.g. InsertString with start=3 denotes that new elements will start at the 3rd position
    i.e. ['a','b','new1','new2',...,'c','d',...]
    """
    __slots__ = ('raw', 'type', 'revision', 'string', 'start_index')

    def __init__(self, operation_raw, revision):
        self.string = operation_raw['s']
        self.start_index = operation_raw['ibi']  # 1-indexed
        super(InsertString, self).__init__(operation_raw, revision)

    def apply(self, elements):
        new_elements = [Character(char, self.revision) for char in self.string]
        elements[self.start_index-1:self.start_index-1] = new_elements


class InsertStringSuggestion(InsertString):
    """
    Suggest the insertion of string elements
    """

    def apply(self, elements):
        new_elements = [Character(char, self.revision, suggest=SUGGEST_INSERT) for char in self.string]
        elements[self.start_index-1:self.start_index-1] = new_elements


class DeleteString(RangeOperation):
    """
    Delete a range of string elements
    """

    def apply(self, elements):
        for i in reversed(range(self.start_index, self.end_index+1)):
            elements.pop(i-1)


class DeleteStringSuggestion(RangeOperation):
    """
    Delete a range of suggested string elements
    """
    def apply(self, elements):
        for i in reversed(range(self.start_index, self.end_index+1)):
            elements.pop(i-1)


class MarkStringForDeletion(RangeOperation):
    """
    Suggest deletion of a range of suggested string elements
    """
    def apply(self, elements):
        for i in range(self.start_index, self.end_index+1):
            elements[i-1].suggest = SUGGEST_DELETE


class UnmarkStringForDeletion(RangeOperation):
    """
    For string previously marked for deletion in a suggestion, unmark for deletion
    """
    def apply(self, elements):
        for i in range(self.start_index, self.end_index+1):
            elements[i-1].suggest = NORMAL


class MultiOperation(Operation):
    """
    Operation subclass representing a "Multiple Operation" operation
    Contains an array of Operation objects
    """
    __slots__ = ('raw', 'type', 'revision', 'operations')

    def __init__(self, operation_raw, revision):
        super(MultiOperation, self).__init__(operation_raw, revision)
        self.operations = [operation_factory(operation_raw, revision) for operation_raw in operation_raw['mts']]

    def apply(self, elements):
        """
        Apply each of the operations comprising the MultiOperation

        Arguments:
            elements (list): list of Elements
        """
        for operation in self.operations:
            operation.apply(elements)

    def iter_operations(self):
        """
        Generator that iterates through base operations.
        Does a depth-first search of the operations tree,
        yielding leaf (non-Multioperation) nodes
        """
        for operation in self.operations:
            if hasattr(operation, 'operations'):
                for child_operation in operation.iter_operations():
                    yield child_operation
            else:
                yield operation
