import json
import pytest
import datetime
import pytz
import voluptuous as vp
import time

import xeroex.utils

def test_de_encrypting_credentials_into_statefile(tmpdir):
    state = tmpdir.join("state.json")

    original_state = {
        'consumer_key': 'foo',
        'consumer_secret': 'bar',
        'verified': True,
        'oauth_token': 'baz',
        'oauth_token_secret': 'qux',
        'oauth_expires_at': datetime.datetime(2018, 6, 11, 12, 3, 25, 359935),
        'oauth_authorization_expires_at': datetime.datetime(2018, 6, 11, 12, 33, 25, 359949)}

    xeroex.utils.save_statefile(original_state, state.strpath)
    recovered_state = xeroex.utils.load_credentials_from_statefile(state.strpath)
    assert recovered_state == original_state


def test_parsing_datestring_raises_on_invalid_value():
    with pytest.raises(vp.Invalid):
        xeroex.utils.parse_datestring("invalid string")


@pytest.mark.parametrize("datestring,timezone", [
    ("now utc", pytz.utc),
    ("now PT", pytz.utc),
    ("now GMT+8", pytz.utc)
])
def test_parsing_datestrings(datestring, timezone):
    assert xeroex.utils.parse_datestring(datestring).tzinfo == timezone

@pytest.mark.parametrize("eps", [
    [{"endpoint": "Foopoint", "parametrs": {"foo_param": 42}}]
])
def test_validating_configs_raise_on_invalid(eps):
    cfg = {"endpoints": eps}
    with pytest.raises(vp.error.MultipleInvalid):
        xeroex.utils.validate_config(cfg)


@pytest.mark.parametrize("eps,expected", [
    (
        [{"endpoint": "Foopoint"}], #raw config
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
    assert xeroex.utils.validate_endpoints_config(eps) == expected

@pytest.mark.parametrize("config,message", [
    ({}, "endpoints|action"),
    ({"endpoints": []}, "action"), # missing action key
])
def test_validating_configs_fails_without_params(config, message):
    with pytest.raises(vp.MultipleInvalid) as excinfo:
        xeroex.utils.validate_config(config)
    if message:
        assert excinfo.match(r".*{}.*".format(message))


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
