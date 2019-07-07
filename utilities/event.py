__author__ = "Jon Stålhammar, Christian Lejdström, Emma Fitzgerald"


class Event:
    """
    Describes an event (i.e. packet/signal)

    Attributes
    ----------
    event_type : int
        Event type, e.g. arrival or departure
    event_time : float
        Positive float (presumably greater than the current time in the simulation)
    node_id : int
        What node (think machine/device) this event belongs to
    pilot_id : int
        Pilot id that is assigned during the simulation
    """

    def __init__(self, event_type, event_time, node_id, max_attempts):
        """
        Initializes a new event

        Parameters
        ----------
        event_type : int
            Event type, e.g. arrival or departure
        event_time : float
            Positive float (presumably greater than the current time in the simulation)
        node_id : int
            What node (think machine/device) this event belongs to
        """

        self.type = event_type
        self.time = event_time
        self.node_id = node_id
        self.pilot_id = -1
