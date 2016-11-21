
class Operation(object):
    '''
    Base Operation class
    Represents action(s) that occur as part of a revision
    '''
    def __init__(self, operation_raw):
        '''
        operation_raw is a dictionary of raw operation metadata
        '''
        self.raw = operation_raw

    def apply(document):
        pass


def getOperation(operation_raw):
    '''
    Factory method that returns Operation or subclass instance
    takes as input a single dict with change info
    '''
    operation_types = {
        'is': InsertString,
        'ds': DeleteString,
        'mlti': MultiOperation,
    }
    operation = operation_types.get(operation_raw['ty']) or Operation
    return operation(operation_raw)


class InsertString(Operation):
    '''
    Operation subclass representing an "Insert String" operation
    '''
    def __init__(self, operation_raw):
        super(InsertString, self).__init__(operation_raw)
        self.string = operation_raw['s']
        self.start_index = operation_raw['ibi']
        self.type = 'insert string'

    def apply(document):
        '''
        insert string into document at specified index
        '''
        for i,char in enumerate(string):
            document.insert(self.start_index+i, self.string)


class DeleteString(Operation):
    '''
    Operation subclass representing a "Delete String" operation
    '''
    def __init__(self, operation_raw):
        super(DeleteString, self).__init__(operation_raw)
        self.start_index = operation_raw['si']
        self.end_index = operation_raw['ei']
        self.type = 'delete string'

    def apply(document):
        '''
        Delete string from document between specified indices
        '''
        del document[self.start_index:self.end_index]
        

class MultiOperation(Operation):
    '''
    Operation subclass representing a "Multiple Operation" operation
    Contains an array of Operation objects
    '''
    def __init__(self, operation_raw):
        super(MultiOperation, self).__init__(operation_raw)
        self.suboperations = [getOperation(x) for x in operation_raw['mts']]
        self.type = 'multiple operations'

    def apply(document):
        '''
        Apply each of the suboperations comprising the Multioperation
        '''
        for suboperation in self.suboperations:
            self.suboperation.apply(document)
            
