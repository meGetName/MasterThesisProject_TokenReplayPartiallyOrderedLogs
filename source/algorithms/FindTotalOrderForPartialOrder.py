from MasterThesisProject.source.structures.Run import Run, Event4Run
from collections import deque

from MasterThesisProject.source.structures.TotalOrderForRun import TotalOrder4Run


def find_total_order_for_run(run: Run) -> TotalOrder4Run:
    events: list = list(run.partial_order.nodes)
    event_to_number_remaining_predecessors: dict = {event: 0 for event in events}
    for event in events:
        for successor_event in run.partial_order.neighbors(event):
            event_to_number_remaining_predecessors[successor_event] += 1
    initial_events: list = list(filter(lambda key: int(event_to_number_remaining_predecessors[key]) == 0,
                                       event_to_number_remaining_predecessors))
    total_order: list = []
    event_to_predecessor: dict = {initial_event: None for initial_event in initial_events}
    event_to_successor: dict = {}
    event_queue: deque = deque(initial_events)
    while len(event_queue) > 0:
        next_event = event_queue.popleft()
        total_order.append(next_event)
        new_events_for_queue: list[Event4Run] = list()
        following_events: list[Event4Run] = list(run.partial_order.neighbors(next_event))
        for following_event in following_events:
            event_to_number_remaining_predecessors[following_event] -= 1
            # if event fell to zero this turn, it can now be added t the queue
            if event_to_number_remaining_predecessors[following_event] == 0:
                new_events_for_queue.append(following_event)
        if len(following_events) > 0:
            event_to_successor[next_event] = following_events[0]
        else:
            event_to_successor[next_event] = None
        for new_event in new_events_for_queue:
            event_queue.append(new_event)
            event_to_predecessor[new_event] = next_event
            event_to_number_remaining_predecessors[new_event] = - 1

    return TotalOrder4Run(total_order, event_to_successor, event_to_predecessor)
