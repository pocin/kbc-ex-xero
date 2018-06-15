import json
import os
import logging

import pytest
import xero.auth
import xero

import xeroex
from xeroex.extractor import main

@pytest.fixture(scope='module')
def xero_credentials():
    creds_type = os.environ["XERO_CREDENTIALS_TYPE"]
    if creds_type == 'public':
        credentials = xero.auth.PartnerCredentials(
            **json.loads(os.environ['XERO_CREDENTIALS_STATE'])
        )
    elif creds_type == 'private':
        credentials = xero.auth.PrivateCredentials(
            os.environ['XERO_CONSUMER_KEY'],
            eval(os.environ['XERO_PRIVATE_RSA_KEY']))
    else:
        raise NotImplementedError("not yet, choose public or private")
        # xero.auth.PartnerCredentials()

    return credentials


def test_main_machinery(caplog):
    with caplog.at_level(logging.DEBUG):
        main()
    assert 'Hello Keboola\n' in caplog.text



@pytest.mark.parametrize("endpoint,params", [
    ("Accounts", {}),
    ("CreditNotes",{}),
    ("Contacts", {}),
    ("Currencies", {}),
    ("BankTransfers", {}),
    ("Journals", {}),
])
def test_downloading_data_all_data_paginated(xero_credentials, endpoint, params):
    ex = xeroex.extractor.XeroEx(xero_credentials)
    for chunk in ex.get_endpoint_data(endpoint, params):
        # each chunk must be at least
        assert len(chunk) >= 1
