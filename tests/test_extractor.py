import pytest
import csv
import json
import xeroex
import io

def testing_saving_and_serializing_json_responses(tmpdir):
    def data():
        # paginated api returns chunks
        yield [{"Name":1}, {"Name":2}] #chunk
        yield [{"Name":3}, {"Name":4}] #chunk
        yield [{"Name":5}, {"Name":6}] #chunk

    # expected = tmpdir.join("EXPECTED_NL_DELIMITED_JSONS.csv")
    # with open(expected.strpath) as f:
    #     wr = csv.DictWriter(f, fieldnames=['data'])
    #     for row in raw_rows:
    #         wr.writerow({"data": json.dumps(row)})


    outpath = tmpdir.join('one_big_list.csv')
    out = xeroex.extractor.XeroEx.write_json_data(data(), outpath.strpath, )


    expected = [
        {"Name":1}, {"Name":2}, {"Name":3},
        {"Name":4}, {"Name":5}, {"Name":6}]

    with open(out) as f:
        data = [json.loads(line['data']) for line in csv.DictReader(f)]
    assert data == expected
