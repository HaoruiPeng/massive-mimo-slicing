import heapq
from utilities.event import Event

__author__ = "Jon Stålhammar, Christian Lejdström, Emma Fitzgerald"


class EventHeap:
    """
    Custom event heap that keeps track of events in chronological orders

    Attributes
    ----------
    __key : int
        Tiebreaker if two events have the same time, keeps algorithm sable
    __heap : list
        Heap implementation of a binary heap
    max_attempts : int
        Maximum number of attempts (in frames) before a event deadline should be considered missed

    """

    def __init__(self, max_attempts):
        """
        Initializes a new event heap sorted by event time

        Parameters
        ----------
        max_attempts : int
            Maximum number of attempts (in frames) before a event deadline should be considered missed
        """

        self.__key = 0
        self.__heap = []
        self.__max_attempts = max_attempts

    def push(self, event_type, event_time, node_id, max_attempts=None):
        """
        Inserts a new event at the correct time in the event heap

        Parameters
        ----------
        event_type : int
            Event type, e.g. arrival or departure
        event_time : float
            Positive float (presumably greater than the current time in the simulation)
        node_id : int
            What node (i.e. machine/device) this event belongs to
        max_attempts : int
            Custom max amount of attempts
        """

        if max_attempts is None:
            max_attempts = self.__max_attempts

        new_event = Event(event_type, event_time, node_id, max_attempts)
        heapq.heappush(self.__heap, (event_time, event_type, self.__key, new_event))
        self.__key += 1

    def pop(self):
        """
        Fetches the next event in time

        Returns
        -------
        Event
            The next event in time
        """

        return heapq.heappop(self.__heap)
