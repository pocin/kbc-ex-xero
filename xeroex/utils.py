import json
import os
import xero
import time
import dateparser
import voluptuous as vp
import logging
import collections

logger = logging.getLogger(__name__)

# PATH_STATE_OUT = os.path.join(os.getenv("KBC_DATADIR"), 'out', 'state.json')

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
    """Back up credentials for next run"""
    logger.info("Backing up credentials to statefile")
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
        self.total_requests = 0

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
        self.total_requests += 1
        # what happens when we try to add request when the queue is full?
        # is it responsibility of the caller to make sure he can call it?

    def wait_until_can_make_request(self):
        """When this gets called it's assumed that the queue is full and we have to wait
        """
        logger.debug("Waiting until I can make request")
        try:
            logger.debug("No requests made so far, go ahead!")
            oldest_request = self.popleft()
        except IndexError:
            # empty queue, go ahead and make requests!
            return True
        else:
            s_since_oldest_request = (time.time() - oldest_request)
            logger.debug("oldest request was done before %s seconds",
                         s_since_oldest_request)
            required_waiting_time = self.window_seconds - s_since_oldest_request
            if  required_waiting_time > 0:
                logging.debug("we have to wait %s seconds", s_since_oldest_request)
                time.sleep(required_waiting_time)
            return True
