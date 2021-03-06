import json
import os
import logging

import pytest
import xero.auth
import xero
import voluptuous as vp

import xeroex
from xeroex.extractor import main

@pytest.fixture(scope='module')
def image_parameters():
    return {
        "#consumer_key": os.environ['XERO_PUBLIC_CONSUMER_KEY'],
        "#consumer_secret": os.environ['XERO_PUBLIC_CONSUMER_SECRET']
    }

@pytest.fixture(scope='module')
def kbc_credentials():
    return {
        "consumer_key": os.environ['XERO_PUBLIC_CONSUMER_KEY'],
        "consumer_secret": os.environ['XERO_PUBLIC_CONSUMER_SECRET'],
        "oauth_token": os.getenv("XERO_KBC_OAUTH_TOKEN"),
        "oauth_token_secret": os.getenv("XERO_KBC_OAUTH_TOKEN_SECRET")
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
                "parameters": {"since": "2 years ago UTC"}
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
        try:
            raw_rsa_key = os.environ['XERO_PRIVATE_RSA_KEY']
            rsa_key = eval(raw_rsa_key)
        except (SyntaxError, NameError):
            # travis
            rsa_key = raw_rsa_key.replace('\\n', '\n')
        credentials = xero.auth.PrivateCredentials(
            os.environ['XERO_CONSUMER_KEY'],
            rsa_key)
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


@pytest.mark.skipif(not os.getenv("XERO_PUBLIC_CREDENTIALS_STATE"),
                    reason='requires manualy setting XERO_PUBLIC_CREDENTIALS_STATE')
def test_main_downloading_data(tmpdir, image_parameters):
    datadir = tmpdir.mkdir("data")
    outtables = datadir.mkdir("out").mkdir("tables")
    instate = datadir.mkdir("in").join("state.json")
    instate.write(os.getenv("XERO_PUBLIC_CREDENTIALS_STATE"))
    xeroex.extractor.main(datadir.strpath, CONFIGS['extract'], image_parameters)

    assert 'Contacts.csv' in outtables.listdir()[0].strpath
    assert os.path.isfile(os.path.join(datadir.strpath, 'out','state.json'))


@pytest.mark.skipif(not os.getenv("XERO_KBC_OAUTH_TOKEN") and not os.getenv("XERO_KBC_OAUTH_TOKEN_SECRET"),
                    reason="Needs manual setting")
def test_main_downloading_data_with_kbc_token(tmpdir, kbc_credentials):
    datadir = tmpdir.mkdir("data")
    outtables = datadir.mkdir("out").mkdir("tables")
    instate = datadir.mkdir("in").join("state.json").write('{}')
    xeroex.extractor.main(datadir.strpath, CONFIGS['extract'], kbc_credentials)

    assert 'Contacts.csv' in outtables.listdir()[0].strpath
    assert os.path.isfile(os.path.join(datadir.strpath, 'out','state.json'))
