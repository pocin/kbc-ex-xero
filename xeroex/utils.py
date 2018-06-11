import json


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
