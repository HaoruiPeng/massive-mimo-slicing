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
    attempts_left : int
        Number of attempts (in frames) left before events expires (defaults to max_attempts)
    pilot_id : int
        Pilot id that is assigned during the simulation
    """

    def __init__(self, event_type, event_time, dead_time, node_id, counter):
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
        self.pilot_id = -1
        self.counter = 0
        self.trace = {'event_type': event_type, 'node_id': node_id, 'counter': counter,
                      'arrival_time': event_time, 'dead_time': dead_time, 'departure_time': 0,
                      'pilot': False}

    def get_entry(self, departure_time, pilot):
        self.trace['departure_time'] = departure_time
        self.trace['pilot'] = pilot

        return self.trace
