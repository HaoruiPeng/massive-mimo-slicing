from event import Event


class EventList:
    """
    Custom linked list that keeps track of events in chronological orders

    Attributes
    ----------
    __first : Node
        First node in the linked list, i.e. the wrapper for the next event in time
    max_attempts : int
        Maximum number of attempts (in frames) before a event deadline should be considered missed

    """

    def __init__(self, max_attempts):
        """
        Initializes a new event linked list

        Parameters
        ----------
        max_attempts : int
            Maximum number of attempts (in frames) before a event deadline should be considered missed
        """

        self.__first = None
        self.__max_attempts = max_attempts

    def insert(self, event_type, event_time, node_id):
        """
        Inserts a new event at the correct time in the event list

        Parameters
        ----------
        event_type : int
            Event type, e.g. arrival or departure
        event_time : float
            Positive float (presumably greater than the current time in the simulation)
        node_id : int
            What node (i.e. machine/device) this event belongs to
        """

        new_event = Event(event_type, event_time, node_id, self.__max_attempts)
        new_node = self.__Node(new_event)

        if self.__first is None:
            self.__first = new_node
        elif self.__first.next is None:
            if self.__first.val.time < event_time:
                self.__first.next = new_node
            else:
                tmp = self.__first
                self.__first = new_node
                self.__first.next = tmp
        else:
            if event_time < self.__first.val.time:
                tmp = self.__first
                self.__first = new_node
                self.__first.next = tmp
            else:
                prev_node = self.__first
                curr_node = self.__first.next

                while curr_node.val.time < event_time:
                    prev_node = curr_node
                    curr_node = curr_node.next

                    if curr_node is None:
                        break

                prev_node.next = new_node
                new_node.next = curr_node

    def fetch(self):
        """
        Fetches the next event in time

        Returns
        -------
        Event
            The next event in time
        """

        if self.__first is not None:
            tmp = self.__first
            self.__first = self.__first.next
            return tmp.val

        return self.__first

    class __Node:
        # Inner class describing a node in the linked list

        def __init__(self, val):
            self.val = val
            self.next = None
