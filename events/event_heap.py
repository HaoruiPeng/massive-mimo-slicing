import heapq
from events.event import Event

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

    def __init__(self):
        """
        Initializes a new event heap sorted by event time

        Parameters
        ----------
        max_attempts : int
            Maximum number of attempts (in frames) before a event deadline should be considered missed
        """

        self.__key = 0
        self.__heap = []

    def push(self, event_type, event_time, dead_time=None, node_id=0, counter=0):
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
        """

        new_event = Event(event_type, event_time, dead_time, node_id, counter)
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

    def get_heap(self):
        return self.__heap

    def get_size(self):
        return len(self.__heap)
