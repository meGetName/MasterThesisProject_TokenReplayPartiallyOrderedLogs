class TotalOrder4Run:
    def __init__(self, order: list = None, event_to_successor_event: dict = None,
                 event_to_predecessor_event: dict = None):
        self.order = order
        self.event_to_successor_event = event_to_successor_event
        self.event_to_predecessor_event = event_to_predecessor_event

    def reverse_copy(self) -> "TotalOrder4Run":
        new_order = list(self.order)
        new_order.reverse()
        return TotalOrder4Run(new_order, self.event_to_predecessor_event, self.event_to_successor_event)
