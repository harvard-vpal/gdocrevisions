# gdocrevisions: Google Doc Revisions
[![pypi](https://img.shields.io/pypi/v/gdocrevisions.svg)](https://pypi.org/project/gdocrevisions)

Python package to retrieve and process google doc revision history data.

## Documentation
Documentation website: https://harvard-vpal.github.io/gdocrevisions/docs

## Setup

### Requirements
* python 3

### Installation
```
pip install gdocrevisions
```

### Other steps
* Create a google service account and create a json credentials file.
* Share a google doc with the service account email (e.g. service-account@appspot.gserviceaccount.com)


## Usage

Code example demonstrating how to:
* generate credentials with the [google-auth](https://google-auth.readthedocs.io/en/latest/) library
* load a document with the gdocrevisions `GoogleDoc` class
* inspect a few attributes of the `GoogleDoc` object instance

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
