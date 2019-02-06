"""
Tests for gdocrevisions library

Usage:

pytest
"""

import os
import json
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
    # GOOGLE_APPLICATION_CREDENTIAL_INFO is an env variable containing the text content of a service account credential file
    credential_info = os.getenv('GOOGLE_SERVICE_ACCOUNT_INFO')
    if not credential_info:
        raise ValueError('No google credential info specified (GOOGLE_SERVICE_ACCOUNT_INFO)')
    return service_account.Credentials.from_service_account_info(json.loads(credential_info), scopes=SCOPE)


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
