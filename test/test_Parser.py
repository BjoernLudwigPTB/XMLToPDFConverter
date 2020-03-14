import pytest

from pyxml2pdf.Core.Parser import Parser


def test_collect_xml_data_empty_call():
    """Parser should warm us if data will not be printed, because it lacks content"""
    parser = Parser()
    with pytest.warns(RuntimeWarning):
        parser.collect_xml_data(events=None)
