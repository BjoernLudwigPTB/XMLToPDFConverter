class EventTable():

    def __init__(self, name, locations, activities):
        """
        Contains all events which cover the mentioned activities at the
        mentioned locations. Every event listed covers at least one of the
        listed activities at one of the listed locations.

        :param str name: name of the table describing where and what is done in
            the included events
        :param list(str) locations: list of locations at one of which all
            listed activities take place
        :param list(str) activities: list of activities covered by the listed
            events
        :return str: the table itself
        course
        """
        self._elements = []
        self._styles = []
        self._name = name
        self._locations = locations
        self._activities = activities

    def add_event(self, event):
        """
        Adds a single event to the table later to be displayed as part of the
        table.

        :param List[reportlab.platypus.Table] event:
        """
        self._elements.append(event)

    def get_elements(self):
        """
        Return the collected event table.

        :return list[reportlab.platypus.Table]: a list of all table rows
            containing the relevant event data
        """
        return self._elements

    def get_activities(self):
        """
        Return the activities associated with the event table.

        :return list[str]: a list of all activities
        """
        return self._activities