"""Module to provide a wrapper :py:class:`Core.events.Event` for xml extracted data"""
from pyxml2pdf.model.tables.TableBuilder import TableBuilder

__all__ = ["Event"]


import warnings
from typing import List
from xml.etree.ElementTree import Element

from reportlab.platypus import Paragraph
from reportlab.platypus import Table

from pyxml2pdf.PdfVisualisation.TableStyle import TableStyle


class Event(Element):
    """A wrapper class for :py:class:`xml.etree.ElementTree.Element`

    :py:class:`xml.etree.ElementTree.Element` is augmented with the table row
    representation and the attributes and methods to manipulate everything
    according to the final tables needs. A :py:class:`Core.events.Event` can only
    be initialized with an object of type :py:class:`xml.etree.ElementTree.Element`.

    :param xml.etree.ElementTree.Element element: the element to build the instance from
    """

    _table_builder = TableBuilder()
    _table_style = TableStyle()

    _categories: List[str]
    _full_row: Table
    _reduced_row: Table
    _subtable_title: str
    _type: str
    _date: str
    _regular_time: str
    _region: str
    _responsible: str
    _description: str

    def __init__(self, element):
        # Call Element constructor and extend ourselves by extending all children
        # tags to create an underlying copy of element.
        super().__init__(element.tag, element.attrib)
        self.extend(list(element))
        # Initialize needed objects especially for table creation.
        self._style = self._table_style.custom_styles["Normal"]
        # Initialize definitely needed instance variables.
        self._init_categories()
        self._type = self._concatenate_tags_content(["Kursart"])
        self._region = self._concatenate_tags_content(["Ort"])
        self._responsible = self._concatenate_tags_content(["Leiter"])
        # Initialize time string for regular event and store it as well in _date.
        self._init_regular_time()
        self._date = self._regular_time
        # Build the table row which contains all information about the regular event.
        self._init_full_row()

    def _init_categories(self):
        """Initialize the list of categories from the according xml tag's content"""
        categories: str = self._concatenate_tags_content(["Kategorie"])
        self._categories = categories.split(", ")

    def _init_reduced_row(self, subtable_title):
        """Initializes the reduced version of the event

        Create a table row in proper format but just containing a brief description
        of the event and a reference to the fully described event at another place,
        namely the subtable with the given title.

        :param str subtable_title: title of the subtable which contains the full event

        .. warning:: Do not call this function directly since it is automatically
        called right after :meth:`get_full_row` is invoked.
        """
        self._reduced_row = self._full_row

    def create_reduced_after_full(func):
        """Decorator to execute :meth:`_init_reduced_row` with :meth:`get_full_row`

        :returns: the return value of :meth:`get_full_row`
        :rtype: Table
        """

        def execute_get_full_and_init_reduced_row(self, *args, **kwargs):
            """Exchange a table row with all the event's information against a
            subtable's title

            This ensures, that after handing over the full information, the reduced
            version with a reference to the subtable containing the  full version is
            created.

            .. note:: This is ensured by a decorator, which is why the function
                signature on `ReadTheDocs.org
                <https://pyxml2pdf.readthedocs.io/en/latest/pyxml2pdf.html#Core.events
                .Event.get_full_row>`_ is displayed incorrectly. The parameter and
                return value are as follows...

            :param str subtable_title: the title of the subtable in which the row will
                be integrated
            :returns: a table row with all the event's information
            :rtype: Table
            """
            return_table = func(self, *args, **kwargs)
            self._init_reduced_row(args[0])
            return return_table

        return execute_get_full_and_init_reduced_row

    def _concatenate_tags_content(self, event_subelements, separator=" - "):
        """Form one string from the texts of a subset of an event's children tags

        Form a string of the content for all desired event children tags by
        concatenating them together with a separator. This is especially necessary,
        since :py:mod:`reportlab.platypus.Paragraph` cannot handle `None`s as texts but
        handles as well the concatenation of XML tags' content, if `event_tags` has more
        than one element.

        :param List[str] event_subelements: list of all tags for which the
            descriptive texts is wanted, even if it is just one
        :param str separator: the separator in between the concatenated texts
        :returns: concatenated, separated texts of all tags for the current event
        :rtype: str
        """
        children_text = ""
        for tag in event_subelements:
            child_text: str = self.findtext(tag)
            if child_text:
                if children_text:
                    children_text += separator + child_text
                else:
                    children_text = child_text
        return children_text

    def _init_full_row(self):
        """Initialize the single table row containing all information of the event

        Extract interesting information from events children tags and connect them
        into a nicely formatted row of a table.
        """
        # columns_to_print = [
        #     Paragraph(PDFBuilder._get_event_data(
        #         event_data, ['Bezeichnung']), styles["Normal"]),
        #     Paragraph(self._parse_regular_time(PDFBuilder._get_event_data(
        #         event_data, ['Wochentag']), PDFBuilder._get_event_data(
        #         event_data, ['Uhrzeit']), PDFBuilder._get_event_data(
        #         event_data, ['Saison']), PDFBuilder._get_event_data(
        #         event_data, ['Ausnahmen'])), styles["Normal"]),
        #     Paragraph(PDFBuilder._get_event_data(
        #         event_data, ['Ort']), styles["Normal"]),
        #     Paragraph(PDFBuilder._get_event_data(
        #         event_data, ['Terminbeschreibung']),
        #         styles["Normal"]),
        #     Paragraph(PDFBuilder._get_event_data(
        #         event_data, ['Zielgruppe']), styles["Normal"]),
        #     Paragraph(PDFBuilder._get_event_data(
        #         event_data, ['Voraussetzungen']), styles["Normal"]),
        #     Paragraph(PDFBuilder._get_event_data(
        #         event_data, ['Leiter']), styles["Normal"])]
        table_columns = [
            Paragraph(self._concatenate_tags_content(["Bezeichnung"]), self._style),
            Paragraph(self._regular_time, self._style),
            Paragraph(self._region, self._style),
            Paragraph(
                self._concatenate_tags_content(["Terminbeschreibung"]), self._style
            ),
            Paragraph(self._concatenate_tags_content(["Zielgruppe"]), self._style),
            Paragraph(self._concatenate_tags_content(["Voraussetzungen"]), self._style),
            Paragraph(self._responsible, self._style),
        ]
        self._full_row = self._table_builder.create_fixedwidth_table([table_columns])

    def _init_date(self):
        """Create a properly formatted string containing the date of the event"""
        # Extract data from xml children tags' texts. Since the date can consist of
        # three date ranges, we concatenate them separated with a line containing
        # only an "und".
        extracted_date = self._concatenate_tags_content(
            ["TerminDatumVon1", "TerminDatumBis1"]
        )
        additional_dates = [
            self._concatenate_tags_content(["TerminDatumVon2", "TerminDatumBis2"]),
            self._concatenate_tags_content(["TerminDatumVon3", "TerminDatumBis3"]),
        ]
        for additional_date in additional_dates:
            if additional_date:
                extracted_date += "<br/>und<br/>" + additional_date

        # Replace any extracted_date of a form similar to 31.12.2099 with "on request".
        if "2099" in extracted_date:
            new_date = "auf Anfrage"
        elif extracted_date:
            # Remove placeholders for missing time specifications and the first two
            # digits of the year specification.
            new_date = (
                extracted_date.replace("00:00", "")
                .replace("2020", "20")
                .replace("2019", "19")
                .replace("2018", "18")
            )
        else:
            # All other dates stay uninterpreted and will be dropped.
            new_date = ""
        self._date = new_date

    def _init_regular_time(self):
        """Determine all time relevant infos and assemble a string accordingly

        This results in a string containing when the group meets and when it does not.
        """
        # Fetch the related information from the xml data.
        weekday = self._concatenate_tags_content(["Wochentag"])
        time = self._concatenate_tags_content(["Uhrzeit"])
        season = self._concatenate_tags_content(["Saison"])
        exceptions = self._concatenate_tags_content(["Ausnahmen"])
        if weekday:
            new_time = weekday + "<br/>"
        else:
            new_time = ""

        if time:
            new_time += time + "<br/>"
        if season:
            new_time += season + "<br/>"
        if exceptions:
            new_time += exceptions
        self._regular_time = new_time

    @staticmethod
    def _parse_prerequisites(personal, material, financial, offers):
        """
        Determine all prerequisites and assemble a string accordingly.

        :param str material: material prerequisite xml text
        :param str personal: personal prerequisite xml text
        :param str financial: financial prerequisite xml text
        :param str offers: xml text of what is included in the price
        :returns: the text to insert in prerequisite column
            the current event
        :rtype: str
        """
        if personal:
            personal_string = "a) " + personal + "<br/>"
        else:
            personal_string = "a) keine <br/>"

        if material:
            material_string = "b) " + material + "<br/>"
        else:
            material_string = "b) keine <br/>"

        if financial:
            financial_string = "c) " + financial + " €"
            if offers:
                financial_string += " (" + offers + ")"
        else:
            financial_string = "c) keine"
        return personal_string + material_string + financial_string

    def _build_description(self, name2="", description="", link=""):
        """Build the description for the event

        This covers all cases with empty texts in some of the according children tags
        and the full as well as the reduced version with just the reference to the
        subtable where the full version can be found. Since the title of the event is
        mandatory, it is not received as parameter but directly retrieved from the
        xml data.

        :param str name2: the short name number two for the event
        :param str description: the descriptive text
        :param str link: a link to more details like the trainer url or the subtable
        :returns: the full description including url if provided
        :rtype: str
        """
        full_description = (
            "<b>" + self._concatenate_tags_content(["Bezeichnung"]) + "</b>"
        )
        if name2:
            full_description += " - " + name2
        if description:
            full_description += " - " + description
        if link:
            if full_description[-1] != ".":
                full_description += "."
            full_description += " Mehr Infos unter <b><i>" + link + "</i></b>."

        return full_description

    @create_reduced_after_full
    def get_full_row(self, subtable_title=None):
        """Exchange a table row with all the event's information against a
        subtable's title

        This ensures, that after handing over the full information, the reduced
        version with a reference to the subtable containing the  full version is
        created.

        .. note:: This is ensured by a decorator, which is why the function
            signature on `ReadTheDocs.org
            <https://pyxml2pdf.readthedocs.io/en/latest/pyxml2pdf.html#Core.events
            .Event.get_full_row>`_ is displayed incorrectly. The parameter and
            return value are as follows...

        :param str subtable_title: the title of the subtable in which the row will
            be integrated
        :returns: a table row with all the event's information
        :rtype: Table
        """
        # If subtable_title is provided, we assume the event has been written to this
        # according subtable, so we store, that the event can be found there.
        if subtable_title:
            self._subtable_title = subtable_title
        else:
            try:
                self._subtable_title
            except AttributeError:
                warnings.warn(
                    "No title for a reference to the full event was given by any "
                    "previous call. Thus it needs to be given this time."
                )
        return self._full_row

    @property
    def categories(self):
        """Return the event's categories

        :returns: a list of the event's categories
        :rtype: List[str]
        """
        return self._categories

    @property
    def responsible(self):
        """Return the name of the person being responsible for the event

        :returns: first and last name
        :rtype: str
        """
        return self._responsible

    @property
    def date(self):
        """Return the date of the event

        :returns: date
        :rtype: str
        """
        return self._date

    def get_table_row(self, subtable_title):
        """Return the table row representation of the event

        This is the API of :py:class:`Core.events.Event` for getting the table row
        representation of the event. It makes sure, that on the first call
        :meth:`get_full_row` is invoked and otherwise :attr:`_reduced_row` is returned.

        :param str subtable_title: the title of the subtable in which the row will
            be integrated
        :returns: a table row representation of the event
        :rtype: Table
        """
        # We check if the reduced row was produced before, which means in turn,
        # that :meth:`get_table_row` was called at least once before. Otherwise we call
        # :meth:`get_full_row` which automatically triggers the creation of the
        # reduced row for later uses.
        try:
            self._reduced_row
        except AttributeError:
            return self.get_full_row(subtable_title)
        return self._reduced_row
