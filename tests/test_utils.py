import json
import pytest
import datetime
import pytz
import voluptuous as vp
import time

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


def test_throttling():
    window_seconds = 5
    requests_limit = 3

    t = xeroex.utils.Throttler(requests_limit=requests_limit,
                  window_seconds=window_seconds) # requests / sliding 60s window
    # make 3 quick requests
    for _ in range(3):
        t.add_request()
    start = time.time()
    # it should take +-(window_seconds) before we can make request (limit is 3)
    assert t.can_make_request
    elapsed = time.time() - start
    assert len(t) == 2
    delta_threshold = .1 # s -> account for some overhead
    assert (window_seconds - delta_threshold) < elapsed < (window_seconds + delta_threshold)

    # we should be able to make a new request right away

    start_2 = time.time()

    assert t.can_make_request

    elapsed_2 = time.time() - start_2
    # still 2, because there wasn't a popleft() invoked
    assert len(t) == 2

    assert elapsed_2 < delta_threshold

def test_throttling_first_request_is_ok():
    throttler = xeroex.utils.Throttler(requests_limit=60,
                                                window_seconds=60,
                                                delay_seconds=1)

    start = time.time()
    throttler.wait_until_can_make_request()
    elapsed = time.time() - start
    # first call should be instant
    assert elapsed < 0.5
