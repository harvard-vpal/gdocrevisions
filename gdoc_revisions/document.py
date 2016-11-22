from apiclient.discovery import build
from httplib2 import Http
import json
from revision import Revision
import pickle

class Document(object):
    '''
    Basic Document class
    '''
    def __init__(self, revisions):
        self.revisions = revisions
        self.content = []
        self.current_revision_id = self.revisions[-1].revision_id if len(self.revisions)>1 else 1
        # populate content by applying all revisions
        self.apply_revisions(self.revisions)

    def render(self):
        return ''.join(self.content)

    def apply_revision(self, revision):
        for operation in revision.operations:
            operation.apply(self.content)

    def apply_revisions(self, revisions):
        for revision in revisions:
            self.apply_revision(revision)

    def at_time(self, datetime):
        revisions = filter(lambda revision: revision.time<=datetime, self.revisions)
        self.content = []
        self.apply_revisions(revisions)
        return self

    def at_revision(self, revision_id):
        revisions = filter(lambda revision: revision.revision_id<=revision_id, self.revisions)
        self.content = []
        self.apply_revisions(revisions)
        return self

    def to_pickle(self, path):
        '''
        Pickle a Document
        '''
        with open(path, 'wb') as f:
            document = pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)


class GoogleDoc(Document):
    '''
    Google doc class
    Contains document metadata and revision history
    '''
    def __init__(self, file_id, credentials):

        # oauth2client.service_account.ServiceAccountCredentials object
        self.credentials = credentials
        # dictionary of document metadata via Google API
        self.metadata = self._gdrive_api().files().get(fileId=file_id).execute()
        # doc title
        self.name = self.metadata['name']
        # file identifier string from the URL
        self.file_id = file_id
        # dict of raw revision metadata, containing keys "changelog" and "chunkedSnapshot"
        self.revisions_raw = self._download_revision_details()
        # array of Revision objects
        revisions = [Revision(r) for r in self.revisions_raw['changelog']]
        # initialize Document attributes
        super(GoogleDoc, self).__init__(revisions)

    def _gdrive_api(self):
        '''
        Return an authorized drive api service object
        '''
        return build('drive', 'v3', credentials=self.credentials)
        
    def _last_revision_id(self):
        '''
        Return the id of the last revision to a document, using the offical google api v3
        '''
        revision_metainfo = self._gdrive_api().revisions().list(fileId=self.file_id).execute()
        if len(revision_metainfo['revisions']) == 1:
            return revision_metainfo['revisions'][1]['id']
        else:
            return revision_metainfo['revisions'][-1]['id']
    
    def _generate_revision_url(self, start, end):
        '''
        Generates a url for downloading revision details (using undocumented google api endpoint)
        '''
        base_url = 'https://docs.google.com/document/d/{file_id}/revisions/load?id={file_id}&start={start}&end={end}'
        url = base_url.format(file_id=self.file_id,start=start,end=end)
        return url

    def _download_revision_details(self):
        '''
        download json-like data with revision info
        '''
        http_auth = self.credentials.authorize(Http())
        last_revision_id = self._last_revision_id()
        url = self._generate_revision_url(start=1,end=last_revision_id)
        raw_text = http_auth.request(url)[1][5:]
        return json.loads(raw_text)


def read_pickle(path):
    '''
    Load Document from pickle
    '''
    with open(path, 'rb') as f:
        document = pickle.load(f)
    return document

