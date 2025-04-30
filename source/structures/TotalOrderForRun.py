
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

    @staticmethod
    def make_total_order_from_list(event_list: list) -> "TotalOrder4Run":
        """
        Method returns a total order from the list, where we construct the natural successors and predecssors
        from the list.
        """
        if event_list is None or len(event_list) == 0:
            return TotalOrder4Run([], {}, {})
        if len(event_list) == 1:
            return TotalOrder4Run(event_list, {event_list[0]: None}, {event_list[0]: None})
        result: TotalOrder4Run = TotalOrder4Run(event_list)
        event_to_successor: dict = dict()
        event_to_predecesor: dict = dict()
        # Inner case
        for index in range(1, len(event_list)-1 ):
            event_to_successor[event_list[index]] = event_list[index+1]
            event_to_predecesor[event_list[index]] = event_list[index-1]
        # Start and end are special
        event_to_successor[event_list[0]] = event_list[1]
        event_to_predecesor[event_list[0]] = None
        event_to_successor[event_list[-1]] = None
        event_to_predecesor[event_list[-1]] = event_list[-2]
        result.event_to_predecessor_event = event_to_predecesor
        result.event_to_successor_event = event_to_successor
        return result


