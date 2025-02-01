from typing import Tuple

from networkx import DiGraph

from MasterThesisProject.source.structures.Run import Run
from MasterThesisProject.source.structures.SinglePlaceTokenResult import SinglePlaceTokenResult
from MasterThesisProject.source.structures.WorkflowNet import WorkflowNet


def calculate_token_analysis_for_initial_and_final_place(run: Run, net: WorkflowNet) \
        -> Tuple[SinglePlaceTokenResult, SinglePlaceTokenResult]:
    initial_place = net.start_place
    final_place = net.end_place
    graph: DiGraph = net.graph
    consumed_initial_tokens: int = 0
    produced_final_tokens: int = 0
    for event in run.labels.keys():
        transition = run.labels[event]
        if graph.has_edge(initial_place,transition):
            consumed_initial_tokens += 1
        if graph.has_edge(transition, final_place):
            produced_final_tokens += 1
    result_initial_place: SinglePlaceTokenResult
    result_final_place: SinglePlaceTokenResult
    if consumed_initial_tokens >= 1:
        result_initial_place = SinglePlaceTokenResult(1, consumed_initial_tokens, consumed_initial_tokens - 1,
                                                      consumed_initial_tokens - 1, 0, 0)
    else:
        result_initial_place = SinglePlaceTokenResult(1, 0, 0, 0, 1, 1)
    if produced_final_tokens >= 1:
        result_final_place = SinglePlaceTokenResult(produced_final_tokens, 1, 0, 0, produced_final_tokens - 1,
                                                    produced_final_tokens - 1)
    else:
        result_final_place = SinglePlaceTokenResult(0, 1, 1, 1, 0, 0)
    return result_initial_place, result_final_place
