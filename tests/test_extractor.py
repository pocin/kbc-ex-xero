import pytest
import csv
import json
import xeroex
import io
import datetime

def testing_saving_and_serializing_json_responses(tmpdir):
    NOW = datetime.datetime.now()
    def data():
        # paginated api returns chunks
        yield [{"Name":1}, {"Name":2, "modified": NOW}] #chunk
        yield [{"Name":3}, {"Name":4}] #chunk
        yield [{"Name":5}, {"Name":6}] #chunk


    outpath = tmpdir.join('one_big_list.csv')
    out = xeroex.extractor.XeroEx.write_json_data(data(), outpath.strpath)


    # after serializing back from csv
    expected = [
        {"Name":1}, {"Name":2, "modified": NOW.isoformat()},
        {"Name":3}, {"Name":4}, {"Name":5}, {"Name":6}]

    with open(out) as f:
        loaded_data = [json.loads(line['data']) for line in csv.DictReader(f)]
    assert loaded_data == expected
