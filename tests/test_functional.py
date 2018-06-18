import json
import os
import logging

import pytest
import xero.auth
import xero
import voluptuous as vp

import xeroex
from xeroex.extractor import main

@pytest.fixture
def image_parameters():
    return {
        "consumer_key": os.environ['XERO_PUBLIC_CONSUMER_KEY'],
        "#consumer_secret": os.environ['XERO_PUBLIC_CONSUMER_SECRET']
    }

#valid configs
CONFIGS = {
    'get_authorization_url': {
        "debug": True,
        "action": "get_authorization_url",
    },
    'verify': {
        "debug": True,
        "action": "verify",
    },
    'extract': {
        "debug": True,
        "action": "extract",
        "endpoints": [
            {
                "endpoint": "Contacts",
                "parameters": {"since": "2 days ago UTC"}
            },
            {
                "endpoint": "Something"
            }
        ]
    }
}

@pytest.fixture(scope='module')
def xero_credentials():
    creds_type = os.environ["XERO_CREDENTIALS_TYPE"]
    if creds_type == 'public':
        credentials = xero.auth.PublicCredentials(
            **json.loads(os.environ['XERO_PUBLIC_CREDENTIALS_STATE'])
        )
    elif creds_type == 'private':
        credentials = xero.auth.PrivateCredentials(
            os.environ['XERO_CONSUMER_KEY'],
            eval(os.environ['XERO_PRIVATE_RSA_KEY']))
    else:
        raise NotImplementedError("not yet, choose public or private")
        # xero.auth.PartnerCredentials()

    return credentials


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
        assert len(chunk) >= 0 # just make sure we don't get error and a deadlock


@pytest.mark.parametrize("config",[
    CONFIGS['get_authorization_url'],
    CONFIGS['verify'],
    CONFIGS['extract']
])
def test_validating_real_valid_configs(config):
    xeroex.utils.validate_config(config)


def test_main_getting_authorization_url(caplog, image_parameters):
    with caplog.at_level(logging.DEBUG):
        url = main('/nonexistent', CONFIGS['get_authorization_url'], image_parameters)
        assert url in caplog.text
        assert vp.Schema(vp.Url)(url)

# I should test exchanging verification code for auth url but this
# can't be done as this needs manual intervention
