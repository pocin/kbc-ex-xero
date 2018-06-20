import json
import csv
import os
import logging
import sys

from xero import Xero
import xero
import xero.auth
import xeroex.utils
import xeroex.exceptions

logger = logging.getLogger(__name__)
# add this
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# sh = logging.StreamHandler()
# sh.setFormatter(formatter)
# logger.addHandler(sh)

def main(datadir, params, image_params):
    logger.info("Starting extractor")
    logger.debug("Debug mode active")

    action = params.get("action")

    # contains the RSA key and client secrets

    consumer_key = image_params['#consumer_key']
    consumer_secret = image_params['#consumer_secret']


    if action == 'get_authorization_url':
        credentials = xero.auth.PublicCredentials(consumer_key, consumer_secret)
        logger.info("Visit this url to get authorization code %s", credentials.url)
        return credentials.url
    elif action == 'verify':
        credentials = xero.auth.PublicCredentials(consumer_key, consumer_secret)
        try:
            code = str(params["verification_code"])
        except KeyError:
            raise xeroex.exceptions.XeroexUserConfigError(
                'missing "verification_code": "123456" parameter, '
                'since you set "action": "verify"')
        credentials.verify(code)
        logger.info("verification_code exchanged for tokens. Feel free to configure extractor as required")
        xeroex.utils.save_statefile(credentials.state)

    elif action == 'extract':
        logger.info("Proceeding to extraction")
        logger.debug("Verifying endpoints configuration")
        validated_endpoint_params = xeroex.utils.validate_endpoints_config(params['endpoints'])
        # all credentials are in statefile until oauth-bundle implements it
        creds = xeroex.utils.load_credentials_from_statefile(os.path.join(datadir, 'in', 'state.json'))
        credentials = xero.auth.PublicCredentials(**creds)
        ex = XeroEx(credentials)
        try:
            do_extraction(ex, validated_endpoint_params, datadir=datadir)
        except:
            logging.error(
                "Something went wrong. We won't be able to refresh the access "
                "tokens upon next run. Please REAUTHORIZE the application!")
            raise
        else:
            xeroex.utils.save_statefile(credentials.state, path=os.path.join(datadir, 'out', 'state.json'))
    else:
        raise xeroex.exceptions.XeroexUserConfigError('Unknown "action": {}'.format(action))

def do_extraction(ex, endpoints, datadir='/data'):
    for endpoint in endpoints:
        outpath = os.path.join(datadir, 'out', 'tables', endpoint['endpoint'] + '.csv')
        ex.download_endpoint_to_file(
            endpoint['endpoint'],
            endpoint.get('params', {}),
            outpath=outpath)

class XeroEx:
    """
    Implements
    - pagination
    - throttling (60 reqs/1 minute rolling window)
    - credentials refreshing

    """
    OFFSET_ENDPOINTS = {'journals'}
    def __init__(self, credentials):
        self.client = Xero(credentials)
        self.throttler = xeroex.utils.Throttler(requests_limit=60,
                                                window_seconds=60,
                                                delay_seconds=1)

    def _get_paginated_data(self, endpoint, parameters, pagination):

        if pagination == 'offset':
            #something
            paging_param = 'offset'
            paging_counter = 0
        elif pagination == 'page':
            paging_param = 'page'
            paging_counter = 1
        else:
            raise xeroex.exceptions.XeroexUserConfigError(
                "Unknown pagination method, {}".format(pagination))

        try:
            # we use the xero.Endpoint.filter method for everything
            # (can parse pagination there)
            method = getattr(self.client, endpoint.lower()).filter
        except AttributeError:
            raise xeroex.exceptions.XeroexUserConfigError(
                        "Couldn't find endpoint {}".format(endpoint))

        params = parameters.copy()
        # forces pagination for all endpoints
        params[paging_param] = paging_counter
        logger.debug("Getting %s with params %s", endpoint, params)
        while True:
            logger.debug("Made %s requests so far", self.throttler.total_requests)
            # this waits until API limits pass so I can make a request
            self.throttler.can_make_request
            try:
                response = method(**params)
            except xero.exceptions.XeroUnauthorized:
                # make 1 attempt to refresh tokens
                try:
                    # assume we are using partner credentials
                    self.client.credentials.refresh()
                except AttributeError:
                    # We are using PublicCredentials which expire after 30 mins and can't be refreshed
                    raise xeroex.exceptions.XeroexAuthorizationExpired(
                        "Used PublicCredentials expired, "
                        "please reauthorize the extractor!")
                else:
                    # tokens refreshed
                    response = method(**params)
            self.throttler.add_request()

            # the api response looks like # {"<ENDPOINT>":[{actual_items...}]}
            # but the xero client already parses this out so we response is
            # [{actual_items...}]}
            yield response
            if len(response) < 100:
                # 100 is a full response
                # 99 would mean that there shouldn't be more pages
                # stop paging if empty
                break
            else:
                if paging_param == 'offset':
                    # if i use offset=1
                    # it will return first 100 results of journals with JN >= 100
                    # we guess that the next set of journals
                    # will have JN 100 (=page_size) + largest JN from previous set
                    params[paging_param] = max(j['JournalNumber'] for j in response) + 100
                elif paging_param == 'page':
                    paging_increment = 1
                    params[paging_param] += 1

    def get_endpoint_data(self, endpoint, parameters):
        """Given an endpoint and parameters, get all pages

        Args:
            endpoint (str): the endpoint you want to get
            parameters (dict): additional parameters the api requires.

        Returns:
            a generator returning pages of the endpoint, one by one
            each yield is something like [{"Name":1}, {"Name":2}] (==chunk)
        """

        if endpoint.lower() in self.OFFSET_ENDPOINTS:
            paging_method = 'offset'
        else:
            paging_method = 'page'
        yield from self._get_paginated_data(endpoint, parameters, paging_method)



    @staticmethod
    def write_json_data(source, destination_path, column_name='data', header=True):
        """Serialize chunks of jsons into a new line delimited json packets

        Arguments:
            source: an iterable of json chunks, where chunk is an
                array of dicts (entities), i.e:
                [{"Name": "Robin"}, {"Name": "Tony"}]
            destination_path (str): /path/to/output.csv
        """

        with open(destination_path, 'w') as fout:
            # we load it all to memory. Optimize and figure it out later
            # maybe new line delimited jsons is ok?
            writer = csv.DictWriter(fout, fieldnames=[column_name])
            if header:
                writer.writeheader()
            for chunk in source:
                for entity in chunk:
                    # isoformat because of datetimes
                    writer.writerow({"data": json.dumps(entity, default=lambda x: x.isoformat())})
        return destination_path

    def download_endpoint_to_file(self, endpoint, parameters, outpath):
        logging.info("Downloading %s %s", endpoint, parameters)
        stream_of_chunks = self.get_endpoint_data(endpoint, parameters)
        self.write_json_data(stream_of_chunks, outpath, column_name='data', header=True)
        # manifest maybe?
        return outpath
