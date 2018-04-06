from __future__ import absolute_import

from datetime import datetime

from .operation import operation_factory


class Revision(object):
    """
    Revision class
    Corresponds to Revision resource type in Google API: 
    https://developers.google.com/drive/v3/reference/revisions
    A Revision contains an Operation
    """
    __slots__ = (
        'time', 'user_id', 'revision_id', 'session_id', 'session_revision_index',
        'raw', 'operation_raw', 'operation', 'iter_operations'
    )

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
        self.operation = operation_factory(self.operation_raw, self)
        # Iterator for operations
        self.iter_operations = self.operation.iter_operations
        
    @property
    def operations(self):
        """
        List of operations that make up this revision
        (MultiOperations are flattened into their base operations)
        """
        return list(self.iter_operations())

    def apply(self, elements):
        """
        Apply the revision to a list of elements

        Arguments:
            elements (list): usually the elements attribute of a Content instance
        """
        self.operation.apply(elements)

    def to_dict(self):
        DICT_ATTRIBUTES = [
            'time',
            'user_id',
            'revision_id',
            'session_id',
            'session_revision_index',
            'operation',
        ]
        return {attr: getattr(self,attr) for attr in DICT_ATTRIBUTES}
