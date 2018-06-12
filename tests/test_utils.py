import json
import pytest
import datetime
import pytz
import voluptuous as vp

import xeroex.utils

def test_de_encrypting_credentials():
    """Before we save it to statefile we need to prefix them with #"""

    # retrieved from credentials.state
    original_state = {
        'consumer_key': 'foo',
        'consumer_secret': 'bar',
        'verified': True,
        'oauth_token': 'baz',
        'oauth_token_secret': 'qux',
        'oauth_expires_at': datetime.datetime(2018, 6, 11, 12, 3, 25, 359935),
        'oauth_authorization_expires_at': datetime.datetime(2018, 6, 11, 12, 33, 25, 359949)}

    encrypted_state = xeroex.utils.encrypt_credentials(original_state)

    expected_encrypted_state = {
        '#consumer_key': 'foo',
        '#consumer_secret': 'bar',
        '#verified': True,
        '#oauth_token': 'baz',
        '#oauth_token_secret': 'qux',
        '#oauth_expires_at': datetime.datetime(2018, 6, 11, 12, 3, 25, 359935),
        '#oauth_authorization_expires_at': datetime.datetime(2018, 6, 11, 12, 33, 25, 359949)}
    assert encrypted_state == expected_encrypted_state

    decrypted_state = xeroex.utils.decrypt_credentials(encrypted_state)

    assert decrypted_state == original_state

def test_saving_statefile(tmpdir):
    state = tmpdir.join("state.json")

    contents = {"foo": "bar", "baz": 42}
    xeroex.utils.save_statefile(state.strpath, contents)

    # make sure the keys of the statefile on disk are prefixed with #
    # keboola will handle actual encryption upon import
    assert state.read() == '{"#foo": "bar", "#baz": 42}'


def test_loading_encrypted_statefile(tmpdir):
    state = tmpdir.join("state.json")
    state.write(json.dumps({"#foo": "bar", "#baz": 42}))

    contents = xeroex.utils.load_statefile(state.strpath)

    # make sure that the keys are "unencrypted" so we can
    # restore the credentials like xero.PartnerCredentials(**contents)
    assert contents == {"foo": "bar", "baz": 42}


def test_parsing_datestring_raises_on_invalid_value():
    with pytest.raises(ValueError):
        xeroex.utils.parse_datestring("invalid string")


def test_parsing_datestring_works():
    assert isinstance(xeroex.utils.parse_datestring("now utc"), datetime.datetime)

def test_validating_minimal_config():
    cfg = {"endpoints": []}
    assert xeroex.utils.validate_config(cfg)

@pytest.mark.parametrize("eps", [
    [{"endpoint": "Foopoint", "parametrs": {"foo_param": 42}}]
])
def test_validating_configs_raise_on_invalid(eps):
    cfg = {"endpoints": eps}
    with pytest.raises(vp.error.MultipleInvalid):
        xeroex.utils.validate_config(cfg)


@pytest.mark.parametrize("eps,expected", [
    (
        [{"endpoint": "Foopoint"}], #expected
        [{"endpoint": "Foopoint"}]  #expected
    ),
    (
        [{"endpoint": "Foopoint",
          "parameters": {"foo_param": 42}}], #endpoints
        [{"endpoint": "Foopoint",            #expected
          "parameters": {"foo_param": 42}}]
    ),
    ( # converting "since" parameter to datetime
        [{"endpoint": "Foopoint",
          "parameters": {"foo_param": 42,
                         "since": "2018-01-31 21:00:00 UTC"}}], #endpoints
        [{"endpoint": "Foopoint",
          "parameters": {"foo_param": 42,
                         "since": datetime.datetime(2018, 1, 31, 21, 0,0, tzinfo=pytz.utc)}}] #expected
    )
])
def test_validating_configs_valid_succeeds(eps, expected):
    cfg = {"endpoints": eps}
    assert xeroex.utils.validate_config(cfg)['endpoints'] == expected
