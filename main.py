from xeroex.extractor import main
from xeroex.exceptions import XeroexError
import os
import sys
import requests
import logging
from keboola.docker import Config

if __name__ == "__main__":
    try:

        datadir = os.getenv("KBC_DATADIR")
        cfg = Config(datadir)
        params = cfg.get_parameters()
        # try:
        #     image_params = cfg.config_data['image_parameters']
        # except KeyError:
        #     # after we start using partner app
        #     logging.error("image_parameters must be set in dev portal")
        #     sys.exit(2)
        logging.getLogger('oauthlib').setLevel(logging.WARNING)
        logging.getLogger('requests_oauthlib').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

        logging.basicConfig(level=logging.DEBUG if params.get("debug") else logging.INFO,
                            format='%(name)s - %(levelname)s - %(message)s',
                            stream=sys.stdout)

        credentials = dict(
            consumer_key=cfg.get_oauthapi_appkey(),
            consumer_secret=cfg.get_oauthapi_appsecret(),
            oauth_token=cfg.get_oauthapi_data()['oauth_token'],
            oauth_token_secret=cfg.get_oauthapi_data()['oauth_token_secret']
        )
        main(datadir, params, credentials)
    except (ValueError, KeyError, requests.HTTPError, XeroexError) as err:
        logging.error(err)
        sys.exit(1)
    except:
        logging.exception("Internal error")
        sys.exit(2)
