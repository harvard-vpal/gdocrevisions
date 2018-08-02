"""
Tests for gdocrevisions library

Usage:

>>> pytest
"""

import os
import pytest
from google.oauth2 import service_account
import gdocrevisions
from gdocrevisions.timeddoc import TimedDoc


FILE_ID = '14QhwN0vBkbC6u9PQ4j3iOOc-G89HkQEKkjz7GQvaCcc'  # file id of small test doc


@pytest.fixture(scope="module")
def credentials():
    print("my file: {}".format(__file__))
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # top level repo dir
    SCOPE = ['https://www.googleapis.com/auth/drive']
    # default credential file location is <repo>/credentials/serviceaccount.json
    DEFAULT_CREDENTIAL_FILE = os.path.join(BASE_DIR, 'credentials', 'serviceaccount.json')
    # can specify custom credential location using GDOCREVISIONS_GOOGLE_APPLICATION_CREDENTIALS env variable
    credential_file = os.getenv('GDOCREVISIONS_GOOGLE_APPLICATION_CREDENTIALS', DEFAULT_CREDENTIAL_FILE)
    return service_account.Credentials.from_service_account_file(credential_file, scopes=SCOPE)


@pytest.fixture(scope="module")
def doc(credentials):
    return gdocrevisions.GoogleDoc(FILE_ID, credentials)


def test_data_retrieval(credentials):
    assert gdocrevisions.GoogleDoc(FILE_ID, credentials)


def test_doc_content(doc):
    assert doc.content.render() == 'hello andrew ang'


def test_doc_timing(credentials):
    timed_doc = TimedDoc(FILE_ID, credentials)
    assert type(timed_doc.times['_download_revision_details']) == float
    assert type(timed_doc.times['_build_revisions']) == float
    assert type(timed_doc.times['_apply_all_revisions']) == float


def test_to_revision(doc):
    assert doc.at_revision(5)
