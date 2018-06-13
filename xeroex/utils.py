import json
import xero
import time
import dateparser
import voluptuous as vp
import logging
import collections


def encrypt_credentials(state):
    """Prefix keys in the credentials dictionary with #"""
    return {"#" + k: v for k, v in state.items()}


def decrypt_credentials(state):
    """remove # from keys in the credentials dictionary"""
    return {k.lstrip("#"): v for k, v in state.items()}


def load_statefile(path):
    with open(path) as io:
        return decrypt_credentials(json.load(io))


def save_statefile(path, contents):
    with open(path, 'w') as io:
        return json.dump(encrypt_credentials(contents), io)

def parse_datestring(dt_string):
    """Convert human readable string or any string to UTC datetime object
    """
    parsed = dateparser.parse(dt_string, settings={'TIMEZONE': 'UTC'})
    if parsed is None:
        raise ValueError("Couldn't parse '{}' into datetime!".format(dt_string))
    logging.info("Parsing '%s' as '%s'", dt_string, parsed)
    return parsed


def validate_config(cfg):
    """See readme for the structure"""
    expected = vp.Schema(
        {
            # vp.Optional("global_parameters"): dict,
            vp.Optional("debug"): bool,
            vp.Required("endpoints"): [
                {
                    "endpoint": str,
                    vp.Optional("parameters"): vp.Schema(
                        {"since": parse_datestring},
                        extra=True)
                }
            ]
        }
    )
    return expected(cfg)


class Throttler(collections.deque):
    """

    Counts number of requests made within last `window_seconds`
    """
    def __init__(self, requests_limit=60, window_seconds=60, delay_seconds=1):
        super().__init__(self)
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.delay_seconds =  delay_seconds

    @property
    def can_make_request(self):
        """Return True if we can make more requests

        That is - there were < 60 requests made since the oldest request
        """
        if len(self) < self.requests_limit:
            return True
        else:
            return self.wait_until_can_make_request()

    def add_request(self):
        # current timestampe
        self.append(time.time())
        # what happens when we try to add request when the queue is full?
        # is it responsibility of the caller to make sure he can call it?

    def wait_until_can_make_request(self):
        oldest_request = self.popleft()
        while (time.time() - self.window_seconds) <= oldest_request:
            time.sleep(self.delay_seconds)
        return True
