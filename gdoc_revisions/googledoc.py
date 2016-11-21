from apiclient.discovery import build
from httplib2 import Http
import json
from revision import Revision


class GoogleDoc(object):
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
        self.revisions = [Revision(r) for r in self.revisions_raw['changelog']]

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
