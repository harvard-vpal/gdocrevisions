# gdocrevisions: Google Doc Revisions
[![pypi](https://img.shields.io/pypi/v/gdocrevisions.svg)](https://pypi.org/project/gdocrevisions)

Python package to retrieve and process google doc revision history data.

## Installation
```
pip install gdocrevisions
```

## Other setup
* Create a google service account and create a json credentials file.
* Share a google doc with the service account email (e.g. service-account@appspot.gserviceaccount.com)

## Documentation
[Documentation website for gdocrevisions](https://harvard-vpal.github.io/gdocrevisions/docs/)

## Example usage
```
from google.oauth2 import service_account
import gdocrevisions

# The file id can be found in the URL
# e.g. https://docs.google.com/document/d/<FILE_ID>
FILE_ID = 'abcdefg12345'

# Specify the service account credentials file
CREDENTIAL_FILE = 'my-credentials.json'
SCOPE = ['https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(CREDENTIAL_FILE, scopes=SCOPE)

# Initialize a GoogleDoc object instance, which retrieves revision data 
gdoc = gdocrevisions.GoogleDoc(FILE_ID, credentials)

# Doc and revision data is available in the object instance attributes
gdoc.metadata
gdoc.revisions
gdoc.revisions[0].operation
```
