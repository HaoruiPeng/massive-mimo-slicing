class EventList:
    def __init__(self, max_attempts):
        self.first = None
        self.max_attempts = max_attempts

    # Inserts an event at the correct time
    def insert(self, event_type, event_time, node_id):
        event = self.Event(event_type, event_time, node_id, self.max_attempts)

        if self.first is None:
            self.first = event
        elif self.first.next is None:
            self.first.next = event
        else:
            prev = self.first
            curr = self.first.next

            while curr.time < event_time:
                prev = curr
                curr = curr.next

                if curr is None:
                    break

            prev.next = event
            event.next = curr

    # Fetch the next event in time
    def fetch(self):
        if self.first is not None:
            tmp = self.first
            self.first = self.first.next
            return tmp

        return self.first

    class Event:
        def __init__(self, event_type, event_time, node_id, max_attempts):
            self.type = event_type
            self.time = event_time
            self.node_id = node_id
            self.attempts_left = max_attempts
            self.pilot_id = -1
            self.next = None
