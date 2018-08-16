from __future__ import absolute_import

import json
import pickle
import logging
from collections import defaultdict

from apiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession

from .revision import Revision
from .session import Session
from .element import EndOfBody


# suppress warnings from google api client library
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)


class Content(object):
    """
    Represents document content with a list of Element objects
    """
    def __init__(self):
        self.elements = [EndOfBody()]

    def apply(self, change):
        """
        Apply some change (could be a revision or operation) to the content elements

        Arguments:
            change (Revision or Operation instance): object whose changes should be applied to the content instance
        """
        change.apply(self.elements)
        
    def render(self):
        return ''.join([element.render() for element in self.elements])

    def reset(self):
        self.__init__()


class Document(object):
    """
    Basic Document class
    """
    def __init__(self, revisions):
        """
        Arguments:
            revisions (list): list of Revision objects
        """
        self.revisions = revisions
        """ List of Revision objects """
        self.content = Content()
        """ Content object """
        self.latest_revision_id = self.revisions[-1].revision_id if len(self.revisions) > 1 else 1
        # populate content by applying all revisions
        # this also populates the elements on delete suboperations
        self._apply_all_revisions()

    def _apply_all_revisions(self):
        for revision in self.revisions:
            self.content.apply(revision)

    def at_time(self, datetime):
        """
        Revert document content to a point in time
        TODO may consider returning a copy
        """
        revisions = list(filter(lambda revision: revision.time <= datetime, self.revisions))
        self.content.reset()
        for revision in revisions:
            self.content.apply(revision)
        return self

    def at_revision(self, revision_id):
        """
        Revert document content to a revision id
        TODO may consider returning a copy
        """
        revisions = list(filter(lambda revision: revision.revision_id <= revision_id, self.revisions))
        self.content.reset()
        for revision in revisions:
            self.content.apply(revision)
        return self

    def to_pickle(self, path):
        """
        Pickle a Document
        """
        with open(path, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

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
                content_state.apply(revision)
                yield content_state
        elif by == 'revision':
            for operation in self.iter_operations():
                content_state.apply(operation)
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

    def iter_suboperations(self):
        """
        Generator that iterates over suboperations
        """
        for revision in self.revisions:
            for suboperation in revision.iter_suboperations():
                yield suboperation

    @property
    def operations(self):
        """
        List of all operations that make up this document
        (MultiOperations are flattened into their base operations)
        """
        return list(self.iter_operations())

    @property
    def suboperations(self):
        """
        List of all suboperations that make up this document
        """
        return list(self.iter_suboperations())


class GoogleDoc(Document):
    """
    Google doc class
    Contains document metadata and revision history
    """
    def __init__(self, file_id=None, credentials=None, metadata=None, data=None, **kwargs):
        """
        Create a GoogleDoc instance
        Requires either (file_id, credentials) or (metadata, data) are provided

        :param file_id: ID string that can be found in the Google Doc URL
        :param credentials: Credentials object
        :param dict of doc-level metadata, e.g. title. if not provided, metadata will be fetched
        :param data: raw json dict for revisions; providing this will skip data download step and instead use provided data
        :param kwargs: Additional kwargs to pass to Document constructor

        :type file_id: str
        :type credentials: google.auth.credentials.Credentials
        :type metadata: dict
        :type data: dict
        """
        # arg validation
        if not (file_id and credentials) or (metadata and data):
            raise ValueError("Invalid arguments: Provide either (file_id, credentials) or (metadata, data)")

        self.credentials = credentials
        """Google credentials object"""

        self.file_id = file_id or metadata.get('id')
        """file identifier string from the URL"""

        self.metadata = metadata or self._fetch_metadata()
        """dictionary of document metadata via Google API"""

        self.revisions_raw = data or self._download_revision_details()
        """dict of raw revision metadata, containing top-level keys "changelog" and "chunkedSnapshot" """

        self.name = self.metadata.get('name')
        """document title, taken from metadata"""

        revisions = self._build_revisions()
        """list of Revision objects constructed from raw data"""

        # initialize Document attributes
        super(GoogleDoc, self).__init__(revisions, **kwargs)

    def _gdrive_api(self):
        """
        Return an authorized drive api service object
        """
        return build('drive', 'v3', credentials=self.credentials)

    def _fetch_metadata(self):
        """
        Fetch a dictionary of document-level metadata via Google API
        """
        return self._gdrive_api().files().get(fileId=self.file_id).execute()

    def _last_revision_id(self):
        """
        Return the id of the last revision to a document, using the offical google api v3
        """
        revision_metainfo = self._gdrive_api().revisions().list(fileId=self.file_id).execute()
        if len(revision_metainfo['revisions']) == 0:
            # detailed metadata endpoint will have a revision corresponding to doc creation
            return 1
        else:
            return revision_metainfo['revisions'][-1]['id']
    
    def _generate_revision_url(self, start, end):
        """
        Generates a url for downloading revision details (using undocumented google api endpoint)
        """
        base_url = 'https://docs.google.com/document/d/{file_id}/revisions/load?id={file_id}&start={start}&end={end}'
        url = base_url.format(file_id=self.file_id, start=start, end=end)
        return url

    def _download_revision_details(self):
        """
        Downloads raw revision data json-like data with revision info
        :return: json
        :rtype: dict
        """
        last_revision_id = self._last_revision_id()
        url = self._generate_revision_url(start=1, end=last_revision_id)
        response = AuthorizedSession(self.credentials).get(url)
        response.raise_for_status()
        data = json.loads(response.text[5:])  # cleans out first few characters so it becomes valid json
        return data

    def _build_revisions(self):
        return [Revision(r) for r in self.revisions_raw['changelog']]


def read_pickle(path):
    """
    Load Document from pickle
    """
    with open(path, 'rb') as f:
        document = pickle.load(f)
    return document
