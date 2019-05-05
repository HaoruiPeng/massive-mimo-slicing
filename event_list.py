from event import Event


class EventList:
    """
    Custom linked list that keeps track of events in chronological orders

    Attributes
    ----------
    first : Node
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

        self.first = None
        self.max_attempts = max_attempts

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
            What node (think machine/device) this event belongs to
        """

        new_event = Event(event_type, event_time, node_id, self.max_attempts)
        new_node = self.__Node(new_event)

        if self.first is None:
            self.first = new_node
        elif self.first.next is None:
            self.first.next = new_node
        else:
            prev_node = self.first
            curr_node = self.first.next

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

        if self.first is not None:
            tmp = self.first
            self.first = self.first.next
            return tmp.val

        return self.first

    class __Node:
        # Inner class describing a node in the linked list

        def __init__(self, val):
            self.val = val
            self.next = None
