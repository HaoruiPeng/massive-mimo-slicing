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
    dead_time: float
        Positive float, at which the event is dropped when no pilot has been assigned yet
    counter: int
        Count how many packets have arrived
    trace: dictionary
        Trace the life time of a packet
    """

    def __init__(self, event_type, event_time, dead_time=None, node_id=0, mode= None):
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
        self.mode = mode
        self.dead_time = dead_time
        self.trace = {'event_type': event_type, 'node_id': node_id,
                      'arrival_time': event_time, 'dead_time': dead_time, 'departure_time': None,
                      'mode': mode, 'pilot': False}

    def get_entry(self, departure_time=None, pilot=None):
        self.trace['departure_time'] = departure_time
        self.trace['pilot'] = pilot

        return self.trace

    def get_node(self):
        return self.node_id
