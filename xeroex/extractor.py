from xero import Xero
import xeroex.utils
import xeroex.exceptions
import operator
import json
from functools import reduce
import csv

def main():
    print("Hello Keboola")


class XeroEx:
    """
    Implements
    - pagination
    - throttling (60 reqs/1 minute rolling window)
    - credentials refreshing

    """
    def __init__(self, credentials):
        self.client = Xero(**credentials)
        self.throttler = xeroex.utils.Throttler(requests_limit=60,
                                                window_seconds=60,
                                                delay_seconds=1)


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
                    writer.writerow({"data": json.dumps(entity)})
        return destination_path
