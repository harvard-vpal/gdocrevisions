# Google doc revision analytics
Prototyping tools to extract and analyze google doc revision history data.

Example usage of gdoc_revisions module:
```
from oauth2client.service_account import ServiceAccountCredentials
import gdoc_revisions

CREDENTIAL_FILE = 'my-credentials.json'
FILE_ID = 'abcdefg12345'

scope = ['https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_FILE, scope)

gdoc = gdoc_revisions.GoogleDoc(FILE_ID, credentials)

gdoc.metadata
gdoc.revisions
gdoc.revisions[0].operation
```