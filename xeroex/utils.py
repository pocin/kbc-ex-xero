import json
import xero
import dateparser
import voluptuous as vp
import logging


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
    parsed = dateparser.parse(dt_string)
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
