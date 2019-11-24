from typing import Callable
from xml.etree.ElementTree import Element

import pytest
from reportlab.platypus.tables import Table

from Core.events import Event
from PdfVisualisation.TableStyle import TableStyle


@pytest.fixture
def test_element() -> Element:
    """Create a test element

    :returns: and element
    """
    test_tag = "test"
    test_attrib1 = "attrib1"
    test_attrib_2 = "attrib2"
    test_attrib = {"1": test_attrib1, "2": test_attrib_2}
    test_element = Element(test_tag, test_attrib)
    return test_element


@pytest.fixture
def subtable_title() -> str:
    """Create a title for a test subtable

    :returns: a test subtable's title
    """
    return "Test subtable title"


@pytest.fixture
def test_event(test_element) -> Event:
    """Create a test event related to the test_element

    :returns: an event matching the test_element
    """
    return Event(test_element)


@pytest.fixture
def table_style() -> TableStyle:
    return TableStyle()


def test_event_init(test_event):
    """Test initialization of :py:mod:`Event` and check for all expected members"""
    assert test_event._categories
    assert test_event._full_row
    assert isinstance(test_event._init_reduced_row, Callable)
    assert isinstance(test_event.get_full_row, Callable)


def test_event_parent(test_event):
    """Test if parent class of :py:mod:`Event` is :py:mod:`Element`"""
    assert isinstance(test_event, Element)


def test_event_tag(test_element, test_event):
    """Test if tag of initialization element of event is properly processed"""
    assert test_event.tag == test_element.tag


def test_event_attrib(test_element, test_event):
    """Test if attributes of initialization element of event is properly processed"""
    assert test_event.attrib == test_element.attrib


def test_event_call_get_full_row(test_event, subtable_title):
    """get_full_row's return type should be of instance table"""
    assert isinstance(test_event.get_full_row(subtable_title), Table)


def test_event_init_reduced_call(test_event, subtable_title):
    """Reduced row should just be created when init is called on it"""
    with pytest.raises(AttributeError):
        assert test_event._reduced_row
    test_event._init_reduced_row(subtable_title)
    assert test_event._reduced_row


def test_event_get_reduced_row(test_event, subtable_title):
    """Reduced row should be created as just one table row with five columns"""
    test_event._init_reduced_row(subtable_title)
    assert test_event._reduced_row._nrows == 1
    assert test_event._reduced_row._ncols == 7


def test_event_reduced_rows_column_widths(test_event, subtable_title, table_style):
    """Reduced row should be created with column widths according to full row"""
    test_event._init_reduced_row(subtable_title)
    assert test_event._reduced_row._colWidths == table_style.column_widths


def test_event_reduced_creation(test_event, subtable_title):
    """Reduced row should be created after full row is requested"""
    with pytest.raises(AttributeError):
        assert test_event._reduced_row
    assert test_event.get_full_row(subtable_title)
    assert test_event._reduced_row


def test_event_compare_reduced_row(test_event, subtable_title):
    """Reduced row should contain the same as full"""
    full_row = test_event.get_full_row(subtable_title)
    reduced_row = test_event._reduced_row
    assert str(full_row._cellvalues[0]) == str(reduced_row._cellvalues[0])


def test_event_get_row(test_event, subtable_title):
    """Before call to table row no reduced table row should be available"""
    with pytest.raises(AttributeError):
        assert test_event._reduced_row
    assert test_event.get_table_row(subtable_title)
    assert test_event._reduced_row
