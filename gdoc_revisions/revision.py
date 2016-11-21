from operations import getOperation


class Revision(object):
    '''
    Revision class
    Corresponds to Revision resource type in Google API: 
    https://developers.google.com/drive/v3/reference/revisions
    A Revision contains an Operation
    '''
    def __init__(self, revision_raw):
        # timestamp
        self.time = datetime.datetime.fromtimestamp(revision_raw[1] / 1e3)
        # google user id of the revision author
        self.user_id = revision_raw[2]
        # numeric revision id, corresponding to id in the Google API
        self.revision_id = revision_raw[3]
        # session string identifier
        self.session = revision_raw[4]
        # index of the revision, within the user session
        self.session_revision = revision_raw[5]
        # array of raw revision metadata
        self.raw = revision_raw
        # dictionary of raw operation metadata
        self.operation_raw = revision_raw[0]
        # Operation object
        self.operation = getOperation(self.operation_raw)