from operation import getOperation, MultiOperation
from datetime import datetime


class Revision(object):
    """
    Revision class
    Corresponds to Revision resource type in Google API: 
    https://developers.google.com/drive/v3/reference/revisions
    A Revision contains an Operation
    """
    def __init__(self, revision_raw):
        # timestamp
        self.time = datetime.fromtimestamp(revision_raw[1] / 1e3)
        # google user id of the revision author
        self.user_id = revision_raw[2]
        # numeric revision id, corresponding to id in the Google API
        self.revision_id = revision_raw[3]
        # session string identifier
        self.session_id = revision_raw[4]
        # index of the revision, within the user session
        self.session_revision_index = revision_raw[5]
        # array of raw revision metadata
        self.raw = revision_raw
        # dictionary of raw operation metadata
        self.operation_raw = revision_raw[0]
        # Operation object
        self.operation = getOperation(self.operation_raw)
        # Array of operations, with no multi operations
        self.operations = _flatten_multioperation(self.operation)

    def to_dict(self):
        dict_attributes = [
            'time',
            'user_id',
            'revision_id',
            'session_id',
            'session_revision_index',
            'raw',
            'operation_raw',
            'operation',
            'operations'
        ]
        return {attr:getattr(self,attr) for attr in dict_attributes}

def _flatten_multioperation(operation):
    operations = []
    if type(operation) is MultiOperation:
        for suboperation in operation.suboperations:
            operations.extend(_flatten_multioperation(suboperation))
    else:
        operations = [operation]
    return operations
    

