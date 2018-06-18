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
        try:
            image_params = cfg.config_data['image_parameters']
        except KeyError:
            logging.error("image_parameters must be set in dev portal")
            sys.exit(2)
        logging.getLogger('oauthlib').setLevel(logging.WARNING)
        logging.getLogger('requests_oauthlib').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

        logging.basicConfig(level=logging.DEBUG if params.get("debug") else logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            stream=sys.stdout)
        main(datadir, params, image_params)
    except (ValueError, KeyError, requests.HTTPError, XeroexError) as err:
        logging.error(err)
    except:
        logging.exception("Internal error")
