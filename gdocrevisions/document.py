from apiclient.discovery import build
from httplib2 import Http
import json
from revision import Revision
from session import Session
import pickle
from collections import defaultdict
import copy
import logging
from element import EndOfBody
from oauth2client.client import OAuth2Credentials
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger('gdocrevisions')

# suppress warnings from google api client library
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

class Content(object):
    """
    Represents document content with a list of Element objects
    """
    def __init__(self):
        self.elements = [EndOfBody()]

    def apply_operation(self, operation):
        operation.apply(self.elements)

    def apply_revision(self, revision):
        """
        apply a revision to content, by applying all of its operations
        """
        for operation in revision.operations:
            self.apply_operation(operation)

    def apply_revisions(self, revisions):
        for revision in revisions:
            self.apply_revision(revision)
    
    def render(self):
        return ''.join([element.render() for element in self.elements])

    def reset(self):
        self.__init__()


class Document(object):
    """
    Basic Document class

    Attributes:
        revisions
        content
        current_revision_id
        operations
        sessions
    """
    def __init__(self, revisions, apply_revisions=True):
        """
        Arguments:
            revisions (list): list of revision objects
            latest (bool): indicates whether to build the content state on initialization
        """
        logger.debug("[Document.__init__()]: Start")
        self.revisions = revisions
        """ List of Revision objects """
        self.content = Content()
        """ Content object """
        self.current_revision_id = self.revisions[-1].revision_id if len(self.revisions)>1 else 1
        # populate content by applying all revisions
        if apply_revisions:
            logger.debug("[Document.__init__()]: Applying revisions")
            self.content.apply_revisions(self.revisions)
        logger.debug("[Document.__init__()]: Finished")

    def at_time(self, datetime):
        """
        Revert document content to a point in time 
        """
        revisions = filter(lambda revision: revision.time<=datetime, self.revisions)
        self.content.reset()
        self.content.apply_revisions(revisions)
        return self

    def at_revision(self, revision_id):
        """
        Revert document content to a revision id
        """
        revisions = filter(lambda revision: revision.revision_id<=revision_id, self.revisions)
        self.content.reset()
        self.content.apply_revisions(revisions)
        return self

    def to_pickle(self, path):
        """
        Pickle a Document
        """
        with open(path, 'wb') as f:
            document = pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    @property
    def sessions(self):
        """
        Return a list of Session objects
        """
        sessions = []
        session_revisions = defaultdict(list)
        for revision in self.revisions:
            session_revisions[revision.session_id].append(revision)
        for session_id, revisions in session_revisions.items():
            if session_id:
                sessions.append(Session(revisions))
        # sort by start time attribute
        sessions.sort(key=lambda x: x.start_time)
        return sessions

    def replay(self, by="revision"):
        """
        iterator/generator that returns document states
        """
        content_state = Content()
        if by == 'operation':
            for revision in self.revisions:
                content_state.apply_revision(revision)
                yield content_state
        elif by == 'revision':
            for operation in self.iter_operations():
                content_state.apply_operation(operation)
                yield content_state
        else:
            raise ValueError("'by' not in accepted values (revision, operation)")

    def iter_operations(self):
        """
        Generator that iterates over operations
        """
        for revision in self.revisions:
            for operation in revision.iter_operations():
                yield operation

    @property
    def operations(self):
        """
        Return a flattened array of revision operations
        """
        return list(self.iter_operations())


class GoogleDoc(Document):
    """
    Google doc class
    Contains document metadata and revision history
    """
    def __init__(self, file_id, credentials=None, keyfile=None, **kwargs):
        """
        Create a GoogleDoc instance
        Requires either credentials or keyfile arguments to be specified

        Arguments:
            file_id (str): ID string that can be found in the Google Doc URL
            credentials (oauth2client.OAuth2Credentals): credentials object
            keyfile (str): Path to a service account json keyfile
        """
        logger.debug("[GoogleDoc.__init__()]: Start")
        # google credentials object instance (oauth2client.OAuth2Credentials or subclass)
        self.credentials = self._get_credentials(credentials, keyfile)
        # dictionary of document metadata via Google API
        self.metadata = self._gdrive_api().files().get(fileId=file_id).execute()
        # doc title
        self.name = self.metadata['name']
        # file identifier string from the URL
        self.file_id = file_id
        # dict of raw revision metadata, containing keys "changelog" and "chunkedSnapshot"
        self.revisions_raw = self._download_revision_details()
        # array of Revision objects
        logger.debug("[GoogleDoc.__init__()]: Initializing revisions")
        revisions = [Revision(r) for r in self.revisions_raw['changelog']]
        # initialize Document attributes
        super(GoogleDoc, self).__init__(revisions, **kwargs)

    def _get_credentials(self, credentials, keyfile):
        if credentials:
            if isinstance(credentials, OAuth2Credentials):
                return credentials
            else:
                raise TypeError("Credential object is not a valid OAuth2Credentials object")
        elif keyfile:
            scope = ['https://www.googleapis.com/auth/drive']
            return ServiceAccountCredentials.from_json_keyfile_name(keyfile, scope)
        else:
            raise ValueError("No credentials provided")

    def _gdrive_api(self):
        """
        Return an authorized drive api service object
        """
        return build('drive', 'v3', credentials=self.credentials)
        
    def _last_revision_id(self):
        """
        Return the id of the last revision to a document, using the offical google api v3
        """
        revision_metainfo = self._gdrive_api().revisions().list(fileId=self.file_id).execute()
        if len(revision_metainfo['revisions']) == 1:
            return revision_metainfo['revisions'][0]['id']
        else:
            return revision_metainfo['revisions'][-1]['id']
    
    def _generate_revision_url(self, start, end):
        """
        Generates a url for downloading revision details (using undocumented google api endpoint)
        """
        base_url = 'https://docs.google.com/document/d/{file_id}/revisions/load?id={file_id}&start={start}&end={end}'
        url = base_url.format(file_id=self.file_id,start=start,end=end)
        return url

    def _download_revision_details(self):
        """
        download json-like data with revision info
        """
        http_auth = self.credentials.authorize(Http())
        last_revision_id = self._last_revision_id()
        url = self._generate_revision_url(start=1,end=last_revision_id)
        raw_text = http_auth.request(url)[1][5:]
        return json.loads(raw_text)


def read_pickle(path):
    """
    Load Document from pickle
    """
    with open(path, 'rb') as f:
        document = pickle.load(f)
    return document

