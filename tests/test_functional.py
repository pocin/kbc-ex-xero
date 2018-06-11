import pytest
from xeroex.extractor import main


def test_main_machinery(capsys):
    main()
    out, err = capsys.readouterr()
    assert out == 'Hello Keboola\n'
