import pytest
from xeroex.extractor import main


def test_main_machinery():
    with pytest.raises(NotImplementedError):
        main()
