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

    def __init__(self, event_type, event_time, dead_time=None, node_id=0, counter=0):
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
        self.dead_time = dead_time
        self.counter = counter
        self.trace = {'event_type': event_type, 'node_id': node_id, 'counter': counter,
                      'arrival_time': event_time, 'dead_time': dead_time, 'departure_time': 0,
                      'pilot': False}

    def get_entry(self, departure_time, pilot):
        self.trace['departure_time'] = departure_time
        self.trace['pilot'] = pilot

        return self.trace
