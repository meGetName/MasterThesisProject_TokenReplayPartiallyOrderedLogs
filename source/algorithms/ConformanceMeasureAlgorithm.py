from MasterThesisProject.source.algorithms.PreflowPushAlgorithm4RunInWorkflownet import find_optimal_tokenflow_for_place
from MasterThesisProject.source.structures.PartiallyOrderedLogConformanceResult import PartiallyOrderedLogConformanceResult, TokenResultsWeightedSum
from MasterThesisProject.source.structures.PartiallyOrderedEventLog import PartiallyOrderedEventLog
from MasterThesisProject.source.structures.TotalOrderForRun import TotalOrder4Run
from MasterThesisProject.source.structures.WorkflowNet import WorkflowNet
from MasterThesisProject.source.structures.SinglePlaceTokenResult import SinglePlaceTokenResult
from MasterThesisProject.source.algorithms.ConformanceAnalysisInitialAndFinalPlace import calculate_token_analysis_for_initial_and_final_place
from MasterThesisProject.source.algorithms.FindTotalOrderForPartialOrder import find_total_order_for_run
from MasterThesisProject.source.structures.RunConformanceResult import RunConformanceResult
from MasterThesisProject.source.algorithms.BruteForceHeuristic import do_brute_force_heuristic_for_token_analysis


def calculate_token_replay_conformance_norm_for_partial_order(event_log: PartiallyOrderedEventLog, model: WorkflowNet,
                                                              do_calculate_precise_result: bool) \
        -> PartiallyOrderedLogConformanceResult:
    weighted_tokens_sums: TokenResultsWeightedSum = TokenResultsWeightedSum()
    # we will need the inverted workflow net for the backward heuristic, only need to calculate it once
    run_to_conformance_result: dict = dict()
    for run in event_log.run_to_frequency.keys():
        result_run: RunConformanceResult = RunConformanceResult()
        # take care of initial and final place in workflow net
        initial_place_result: SinglePlaceTokenResult
        final_place_result: SinglePlaceTokenResult
        initial_place_result, final_place_result = calculate_token_analysis_for_initial_and_final_place(run, model)
        result_run.add_single_place_result(initial_place_result)
        result_run.add_single_place_result(final_place_result)
        total_order: TotalOrder4Run = find_total_order_for_run(run)
        run.total_order = total_order
        for place in model.inner_places:
            # Try forward heuristic and see if it already fits
            forward_heuristic: SinglePlaceTokenResult = do_brute_force_heuristic_for_token_analysis(run, model, place, False)
            missing_token_theoretic_optimum = max(0, forward_heuristic.consumed_token - forward_heuristic.produced_token)
            if missing_token_theoretic_optimum == forward_heuristic.missing_token_max:
                forward_heuristic.mark_self_as_precise()
                result_run.add_single_place_result(forward_heuristic)
                result_run.number_places_decided_forward_heuristic += 1
                continue
            # Forward heuristic failed, now try backward heuristic.
            backward_heuristic: SinglePlaceTokenResult = do_brute_force_heuristic_for_token_analysis(run, model, place, True)
            if missing_token_theoretic_optimum == backward_heuristic.missing_token_max:
                backward_heuristic.mark_self_as_precise()
                result_run.add_single_place_result(backward_heuristic)
                result_run.number_places_decided_backward_heuristic += 1
                continue
            # Both heuristics failed; now depending on input flag we either do the precise calculation or only estimate
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
        result_run.calculate_and_set_conformance_level()
        run_to_conformance_result[run] = result_run
        weighted_tokens_sums.add_result_for_run(event_log.run_to_frequency[run], result_run)
    total_result: PartiallyOrderedLogConformanceResult = PartiallyOrderedLogConformanceResult()
    total_result.fill_from_calculation_result(weighted_tokens_sums, run_to_conformance_result)
    return total_result
