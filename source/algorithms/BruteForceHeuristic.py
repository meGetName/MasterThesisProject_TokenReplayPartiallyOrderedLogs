from MasterThesisProject.source.structures.Run import Run
from MasterThesisProject.source.structures.SinglePlaceTokenResult import SinglePlaceTokenResult
from MasterThesisProject.source.structures.TotalOrderForRun import TotalOrder4Run
from MasterThesisProject.source.structures.WorkflowNet import WorkflowNet


def do_brute_force_heuristic_for_token_analysis(run: Run, model: WorkflowNet, place, do_backward_heuristic: bool) \
        -> SinglePlaceTokenResult:
    """
    This functions performs the brute force heuristic for estimating the number of missing tokens of the optimal compact
    tokenflow by always pushing all tokens to the next following event (when doing a forward heuristic) or to the
    predecessing event (when doing a backward heuristic).
    :param run:
    :param model:
    :param place:
    :param do_backward_heuristic:
    :return: The result does not fill the fields for minimal missing and remaining tokens as the pure heuristic can not
             tell this. One has to fill this information manually afterward. Therefore, the result always assume itself
             to be not precise.
    """
    order_iteration: TotalOrder4Run = run.total_order
    if do_backward_heuristic:
        order_iteration = run.total_order.reverse_copy()
    event_to_marking: dict = {event: 0 for event in order_iteration.order}
    flow_relation = model.graph
    result: SinglePlaceTokenResult = SinglePlaceTokenResult()
    result.is_precise = False

    for event in order_iteration.order:
        transition = run.labels[event]
        # check for consumption
        has_event_consumption: bool = flow_relation.has_edge(transition, place) if do_backward_heuristic \
            else flow_relation.has_edge(place, transition)
        if has_event_consumption:
            result.consumed_token += 1
            if event_to_marking[event] == 0:
                result.missing_token_max += 1
            else:
                event_to_marking[event] -= 1
        # check for production
        has_event_production: bool = flow_relation.has_edge(place, transition) if do_backward_heuristic\
            else flow_relation.has_edge(transition, place)
        if has_event_production:
            result.produced_token += 1
            event_to_marking[event] += 1
        # push token to next event
        next_event = order_iteration.event_to_successor_event[event]
        if next_event is None:
            result.remaining_token_max += event_to_marking[event]
        else:
            event_to_marking[next_event] += event_to_marking[event]
        event_to_marking[event] = 0

    # for backward heuristic we have to switch roles and correct remaining tokens
    if do_backward_heuristic:
        result.produced_token, result.consumed_token = result.consumed_token, result.produced_token
        corrected_value_remaining_token = result.produced_token - result.consumed_token + result.remaining_token_max
        result.missing_token_max, result.remaining_token_max = result.remaining_token_max, corrected_value_remaining_token

    return result
