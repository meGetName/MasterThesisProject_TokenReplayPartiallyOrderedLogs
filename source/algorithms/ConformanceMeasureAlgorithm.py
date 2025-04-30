from MasterThesisProject.source.algorithms.PreflowPushAlgorithm4RunInWorkflownet import find_optimal_tokenflow_for_place
from MasterThesisProject.source.structures.PartiallyOrderedLogConformanceResult import PartiallyOrderedLogConformanceResult, TokenResultsWeightedSum, \
    PlaceStatistics
from MasterThesisProject.source.structures.PartiallyOrderedEventLog import PartiallyOrderedEventLog
from MasterThesisProject.source.structures.TotalOrderForRun import TotalOrder4Run
from MasterThesisProject.source.structures.WorkflowNet import WorkflowNet
from MasterThesisProject.source.structures.SinglePlaceTokenResult import SinglePlaceTokenResult
from MasterThesisProject.source.algorithms.ConformanceAnalysisInitialAndFinalPlace import calculate_token_analysis_for_initial_and_final_place
from MasterThesisProject.source.algorithms.FindTotalOrderForPartialOrder import find_total_order_for_run
from MasterThesisProject.source.structures.RunConformanceResult import RunConformanceResult
from MasterThesisProject.source.algorithms.BruteForceHeuristic import do_brute_force_heuristic_for_token_analysis


def calculate_token_replay_conformance_norm_for_partial_order(event_log: PartiallyOrderedEventLog,
                                                              model: WorkflowNet,
                                                              do_calculate_precise_result: bool,
                                                              never_use_heuristics=False,
                                                              is_total_order=False,
                                                              include_initial_and_final_place=True) \
        -> PartiallyOrderedLogConformanceResult:
    """

    :param is_total_order: In this case, we can realize classic token replay by only doing forward heuristic
    :param event_log:
    :param model:
    :param do_calculate_precise_result:
    :param never_use_heuristics: only for experiments: when this is set true the algorithm only uses the flow network
    :param include_initial_and_final_place: if the log is created by enforcing the correct start and final event,
                                            it makes sense to not take thes corresponding places into account
    :return:
    """
    if not do_calculate_precise_result and never_use_heuristics:
        raise Exception("The input flags contradict each other: you have to use the heuristics for the quick result!")
    weighted_tokens_sums: TokenResultsWeightedSum = TokenResultsWeightedSum()
    total_result: PartiallyOrderedLogConformanceResult = PartiallyOrderedLogConformanceResult()
    place_to_decision_statistic: dict[str, PlaceStatistics] = dict()
    # Only inner places are interesting as initial and start places are always clear to analyze
    for place in model.inner_places:
        place_to_decision_statistic[place.name] = PlaceStatistics()
    total_result.place_to_decision_statistic = place_to_decision_statistic
    run_to_conformance_result: dict = dict()
    for run in event_log.run_to_frequency.keys():
        result_run: RunConformanceResult = RunConformanceResult()
        # take care of initial and final place in workflow net
        initial_place_result: SinglePlaceTokenResult
        final_place_result: SinglePlaceTokenResult
        initial_place_result, final_place_result = calculate_token_analysis_for_initial_and_final_place(run, model)
        if include_initial_and_final_place:
            result_run.add_single_place_result(initial_place_result)
            result_run.add_single_place_result(final_place_result)
        if run.total_order is None:
            total_order: TotalOrder4Run = find_total_order_for_run(run)
            run.total_order = total_order
        for place in model.inner_places:
            forward_heuristic: SinglePlaceTokenResult = None
            backward_heuristic: SinglePlaceTokenResult = None
            missing_token_theoretic_optimum: int = -1
            if not never_use_heuristics:
                # Try forward heuristic and see if it already fits
                forward_heuristic = do_brute_force_heuristic_for_token_analysis(run, model, place, False)
                missing_token_theoretic_optimum = max(0, forward_heuristic.consumed_token - forward_heuristic.produced_token)
                if missing_token_theoretic_optimum == forward_heuristic.missing_token_max or is_total_order:
                    forward_heuristic.mark_self_as_precise()
                    result_run.add_single_place_result(forward_heuristic)
                    result_run.number_places_decided_forward_heuristic += 1
                    place_to_decision_statistic[place.name].forward_heuristic += 1
                    place_to_decision_statistic[place.name].add_single_place_result(forward_heuristic)
                    continue
                # Forward heuristic failed, now try backward heuristic.
                backward_heuristic: SinglePlaceTokenResult = do_brute_force_heuristic_for_token_analysis(run, model, place, True)
                if missing_token_theoretic_optimum == backward_heuristic.missing_token_max:
                    backward_heuristic.mark_self_as_precise()
                    result_run.add_single_place_result(backward_heuristic)
                    result_run.number_places_decided_backward_heuristic += 1
                    place_to_decision_statistic[place.name].backward_heuristic += 1
                    place_to_decision_statistic[place.name].add_single_place_result(backward_heuristic)
                    continue
            # Both heuristics failed or were now allowed; now depending on input flag we either do the precise calculation or only estimate
            place_to_decision_statistic[place.name].maximal_flow += 1
            result_to_use: SinglePlaceTokenResult
            if do_calculate_precise_result:
                result_to_use = find_optimal_tokenflow_for_place(place, run, forward_heuristic)
                result_run.number_places_decided_flow_network += 1
            else:
                better_heuristic = forward_heuristic if forward_heuristic.missing_token_max <= backward_heuristic.missing_token_max else backward_heuristic
                better_heuristic.missing_token_min = missing_token_theoretic_optimum
                better_heuristic.remaining_token_min = (better_heuristic.produced_token - better_heuristic.consumed_token
                                                        + better_heuristic.missing_token_min)
                result_to_use = better_heuristic
                result_run.number_places_only_estimated += 1
            result_run.add_single_place_result(result_to_use)
            place_to_decision_statistic[place.name].add_single_place_result(result_to_use)
        result_run.calculate_and_set_conformance_level()
        run_to_conformance_result[run] = result_run
        weighted_tokens_sums.add_result_for_run(event_log.run_to_frequency[run], result_run)
    total_result.fill_from_calculation_result(weighted_tokens_sums, run_to_conformance_result)
    return total_result
