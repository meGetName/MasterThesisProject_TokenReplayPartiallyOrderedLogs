import math
import time
from datetime import datetime

import pandas as pd
from pandas import DataFrame

from MasterThesisProject.source.algorithms.ConformanceMeasureAlgorithm import calculate_token_replay_conformance_norm_for_partial_order
from MasterThesisProject.source.algorithms.FindTotalOrderForPartialOrder import find_total_order_for_run
from MasterThesisProject.source.structures.PartiallyOrderedLogConformanceResult import PartiallyOrderedLogConformanceResult, PlaceStatistics
from MasterThesisProject.source.structures.RunConformanceResult import RunConformanceResult
from MasterThesisProject.source.utils.ImportCCOxesFileToEventLog import import_cco_xes_file_to_event_log, import_xes_file_totally_ordered_log
from MasterThesisProject.source.utils.ImporterPnmlFileToInternalWorkflowNet import import_pnml_file_to_workflow_net

# Definition of experiment parameters
# TO combination
net_log_pairs_to = [
    {"log": "BPI2012_alog.xes", "net": "bpi2012_alog_5.pnml"},
    {"log": "BPI2012_alog.xes", "net": "bpi2012_alog_10.pnml"},
    {"log": "BPI2012_olog.xes", "net": "bpi2012_olog_5.pnml"},
    {"log": "BPI2012_olog.xes", "net": "bpi2012_olog_10.pnml"},
    {"log": "BPI2019_C.xes", "net": "bpi2019c_5.pnml"},
    {"log": "BPI2019_C.xes", "net": "bpi2019c_10.pnml"},
    {"log": "reviewing_complete_only.xes", "net": "reviewing_5.pnml"},
    {"log": "reviewing_complete_only.xes", "net": "reviewing_10.pnml"},
    {"log": "Road_Traffic_Fine.xes", "net": "roadtraffic_5.pnml"},
    {"log": "Road_Traffic_Fine.xes", "net": "roadtraffic_10.pnml"},
    {"log": "teleclaims_complete_only.xes", "net": "teleclaims_5.pnml"},
    {"log": "teleclaims_complete_only.xes", "net": "teleclaims_10.pnml"},
    {"log": "repairExampleNice.xes", "net": "repair_net.pnml"}
    ]
# PO combinations
net_log_pairs_po = [
    {"log": "BPI12_alog_alpha_logwise_oneRperPoVar.xes", "net": "bpi2012_alog_5.pnml"},
    {"log": "BPI12_alog_alpha_logwise_oneRperPoVar.xes", "net": "bpi2012_alog_10.pnml"},
    {"log": "BPI12_olog_alpha_logwise_oneRperPoVar.xes", "net": "bpi2012_olog_5.pnml"},
    {"log": "BPI12_olog_alpha_logwise_oneRperPoVar.xes", "net": "bpi2012_olog_10.pnml"},
    {"log": "bpi2019_C_alpha_logwise_oneRperPoVar.xes", "net": "bpi2019c_5.pnml"},
    {"log": "bpi2019_C_alpha_logwise_oneRperPoVar.xes", "net": "bpi2019c_10.pnml"},
    {"log": "reviewing_alpha_logwise_oneRperPoVar.xes", "net": "reviewing_5.pnml"},
    {"log": "reviewing_alpha_logwise_oneRperPoVar.xes", "net": "reviewing_10.pnml"},
    {"log": "roadtrafficfine_alpha_logwise_oneRperPoVar.xes", "net": "roadtraffic_5.pnml"},
    {"log": "roadtrafficfine_alpha_logwise_oneRperPoVar.xes", "net": "roadtraffic_10.pnml"},
    {"log": "teleclaims_alpha_logwise_oneRperPoVar.xes", "net": "teleclaims_5.pnml"},
    {"log": "teleclaims_alpha_logwise_oneRperPoVar.xes", "net": "teleclaims_10.pnml"},
    {"log": "Repair_alpha_logwise_oneRperPoVar.xes", "net": "repair_net.pnml"}
]
# Parameter to control experiment
number_tests_per_pair: int = 100
is_experiment_with_po: bool = True
do_persist_results: bool = False

# The following parameter should normally not be changed but if you want to experiment feel free.
include_invalid_data: bool = True
include_data_with_invalid_transitions: bool = True
# in some situations (in particular our data) the start and final event are set to be fulfilled; thus
# they generate a lot of correct tokens
count_initial_and_final_places: bool = True

# Following information is directly filled from above choices
path_for_logs: str = "data/partially_ordered_logs/" if is_experiment_with_po else "data/totally_ordered_logs/"
path_for_results: str = "results/po/" if is_experiment_with_po else "results/to/"
calculation_methods = ["Heuristic and flow network", "Only heuristic", "Only flow network"] if is_experiment_with_po else ["Classic token replay"]
do_calculate_precise_result_flags = [True, False, True] if is_experiment_with_po else [True]
never_use_heuristic_flags = [False, False, True] if is_experiment_with_po else [False]

# Column names for the involved csv files
colum_names_general_results = ["Start time",
                               "Net name",
                               "Log name",
                               "Invalid included",
                               "Include initial/final place",
                               "Calculation method",
                               "Run time",
                               "Conformance level (maximum)",
                               "Conformance level (minimum)",
                               "Places with forward heuristic",
                               "Places with backward heuristic",
                               "Other places",
                               "Missing tokens (max)",
                               "Missing tokens (min)",
                               "Consumed tokens",
                               "Remaining tokens (max)",
                               "Remaining tokens (min)",
                               "Produced tokens"]
colum_names_run_statistics = ["Start time",
                              "Net name",
                              "Log Name",
                              "Invalid included",
                              "Include initial/final place",
                              "Run represent (PO/TO name)",
                              "Run frequency",
                              "Conformance level (maximum)",
                              "Conformance level (minimum)",
                              "Invalid event label",
                              "Missing Tokens (maximum)",
                              "Missing Tokens (minimum)",
                              "Consumed Tokens",
                              "Remaining Tokens (maximum)",
                              "Remaining Tokens (minimum)",
                              "Produced Tokens"
                              ]
column_names_place_statistics = ["Start time",
                                 "Net name",
                                 "Log Name",
                                 "Invalid included",
                                 "Include initial/final place",
                                 "Place Name",
                                 "Forward heuristic",
                                 "Backward heuristic",
                                 "Maximal Flow",
                                 "Missing Tokens (maximum)",
                                 "Missing Tokens (minimum)",
                                 "Consumed Tokens",
                                 "Remaining Tokens (maximum)",
                                 "Remaining Tokens (minimum)",
                                 "Produced Tokens"
                                 ]
# Definition(End)

results_this_experiment: DataFrame = pd.DataFrame(columns=colum_names_general_results)


def do_experiment_for_data(net_log_pair: dict[str, str]):
    # After each iteration we save the subresults to avoid data loss. In the end we will produce a master file
    iteration_sub_results: list[DataFrame] = []
    net_name = net_log_pair["net"].replace(".pnml", "")
    net_file_name = "data/nets/" + net_log_pair["net"]
    log_name = net_log_pair["log"].replace(".xes", "")
    log_file_name = path_for_logs + net_log_pair["log"]
    print("Beginning experiment for log-net-pair ({},{}).".format(log_name, net_name))
    net_internal_format, name_to_transition = import_pnml_file_to_workflow_net(net_file_name)
    log_internal_format, invalid_run_to_false_labels = import_cco_xes_file_to_event_log(log_file_name, name_to_transition,
                                                                                        include_data_with_invalid_transitions) \
        if is_experiment_with_po else import_xes_file_totally_ordered_log(log_file_name, name_to_transition, include_data_with_invalid_transitions)
    # set the total orders in advance to avoid non-deterministic behavior
    for run in log_internal_format.run_to_frequency:
        run.total_order = find_total_order_for_run(run)
    # now do the iterations
    for number_iteration in range(number_tests_per_pair):
        iteration_sub_result: DataFrame = DataFrame(columns=colum_names_general_results)
        print("Iteration {} of {}.".format(number_iteration + 1, number_tests_per_pair))
        # Also iterate over different calculation methods
        for index_calc_method in range(len(calculation_methods)):
            do_calculate_precise_result: bool = do_calculate_precise_result_flags[index_calc_method]
            never_use_heuristic: bool = never_use_heuristic_flags[index_calc_method]
            time_stamp: datetime = datetime.now()
            start_experiment = time.perf_counter()
            result: PartiallyOrderedLogConformanceResult = calculate_token_replay_conformance_norm_for_partial_order(log_internal_format,
                                                                                                                     net_internal_format,
                                                                                                                     do_calculate_precise_result,
                                                                                                                     never_use_heuristic,
                                                                                                                     not is_experiment_with_po,
                                                                                                                     count_initial_and_final_places)
            end_experiment = time.perf_counter()
            time_experiment = end_experiment - start_experiment
            # The other places are either ones calculated in flow network or only by better heuristic
            number_other_places: int = result.number_places_decided_flow_network if do_calculate_precise_result else result.number_places_only_estimated
            iteration_sub_result.loc[len(iteration_sub_result)] = [time_stamp,
                                                                   net_name,
                                                                   log_name,
                                                                   include_invalid_data,
                                                                   count_initial_and_final_places,
                                                                   calculation_methods[index_calc_method],
                                                                   time_experiment,
                                                                   result.upper_bound_conformance,
                                                                   result.lower_bound_conformance,
                                                                   result.number_places_decided_forward_heuristic,
                                                                   result.number_places_decided_backward_heuristic,
                                                                   number_other_places,
                                                                   result.missing_tokens_max,
                                                                   result.missing_tokens_min,
                                                                   result.consumed_tokens,
                                                                   result.remaining_tokens_max,
                                                                   result.remaining_tokens_min,
                                                                   result.produced_tokens]

            # We only need to save once the statistics for every place and every run
            if number_iteration == 0 and index_calc_method == 0:
                # Place statistics
                place_statistic_result: DataFrame = DataFrame(columns=column_names_place_statistics)
                for place in net_internal_format.inner_places:
                    place_count: PlaceStatistics = result.place_to_decision_statistic[place.name]
                    place_statistic_result.loc[len(place_statistic_result)] = [time_stamp,
                                                                               net_name,
                                                                               log_name,
                                                                               include_invalid_data,
                                                                               count_initial_and_final_places,
                                                                               place.name,
                                                                               place_count.forward_heuristic,
                                                                               place_count.backward_heuristic,
                                                                               place_count.maximal_flow,
                                                                               place_count.missing_token_max,
                                                                               place_count.missing_token_min,
                                                                               place_count.consumed_token,
                                                                               place_count.remaining_token_max,
                                                                               place_count.remaining_token_min,
                                                                               place_count.produced_token
                                                                               ]
                if do_persist_results:
                    place_statistic_result.to_csv(
                        path_for_results + "place_details/Result_POL_PlaceStats_{}_{}_{}.csv".format(net_name, log_name,
                                                                                                     time_stamp.strftime("%Y-%m-%d_%H-%M-%S")),
                        index=False)
                # Run statistics
                run_statistic_result: DataFrame = DataFrame(columns=colum_names_run_statistics)
                for run in result.run_to_conformance_result:
                    run_conformance_result: RunConformanceResult = result.run_to_conformance_result[run]
                    run_statistic_result.loc[len(run_statistic_result)] = [time_stamp,
                                                                           net_name,
                                                                           log_name,
                                                                           include_invalid_data,
                                                                           count_initial_and_final_places,
                                                                           run.name_foreign_source,
                                                                           log_internal_format.run_to_frequency[run],
                                                                           run_conformance_result.conformance_level_max,
                                                                           run_conformance_result.conformance_level_min,
                                                                           None,
                                                                           run_conformance_result.missing_token_max,
                                                                           run_conformance_result.missing_token_min,
                                                                           run_conformance_result.consumed_token,
                                                                           run_conformance_result.remaining_token_max,
                                                                           run_conformance_result.remaining_token_min,
                                                                           run_conformance_result.produced_token
                                                                           ]
                # Additionally, we add all invalid runs to the run statistics if they are not present; otherwise we se the first false
                # label on the already added transitions.
                for run_name in invalid_run_to_false_labels:
                    invalid_label: str = invalid_run_to_false_labels[run_name]
                    if not include_data_with_invalid_transitions:
                        run_statistic_result.loc[len(run_statistic_result)] = [time_stamp,
                                                                               net_name,
                                                                               log_name,
                                                                               include_invalid_data,
                                                                               count_initial_and_final_places,
                                                                               run_name,
                                                                               1,
                                                                               math.nan,
                                                                               math.nan,
                                                                               invalid_label,
                                                                               math.nan,
                                                                               math.nan,
                                                                               math.nan,
                                                                               math.nan,
                                                                               math.nan,
                                                                               math.nan]
                    else:
                        run_statistic_result.loc[run_statistic_result["Run represent (PO/TO name)"] == run_name, "Invalid event label"] = invalid_label
                if do_persist_results:
                    run_statistic_result.to_csv(
                        path_for_results + "run_details/Result_POL_RunStats_{}_{}_{}.csv".format(net_name, log_name, time_stamp.strftime("%Y-%m-%d_%H-%M-%S")),
                        index=False)
        iteration_sub_results.append(iteration_sub_result)
        # Writing of subresults is not really needed, thus we skip it.
        # # Write subresults
        # file_name_subresult = path_for_results + "parts/Result_ConformanceAndTime_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_Iteration_" + str(
        #     number_iteration)
        # iteration_sub_result.to_csv(file_name_subresult, index=False)
    # At the end concat results and write into file
    file_name_total_result: str = path_for_results + "general/Result_ConformanceANdTime_{}_{}_{}".format(net_name, log_name,
                                                                                                         datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    combined_results: DataFrame = pd.concat(iteration_sub_results)
    if do_persist_results:
        combined_results.to_csv(file_name_total_result, index=False)


timestamp_total_experiment: str = str(datetime.now())
with open("WrongPOXesReadingLog.txt", "a") as log_file:
    log_file.write("Observed problems for experiments at time: " + timestamp_total_experiment + ".\n")
net_log_pairs = net_log_pairs_po if is_experiment_with_po else net_log_pairs_to
for net_log_pair in net_log_pairs:
    do_experiment_for_data(net_log_pair)
with open("WrongPOXesReadingLog.txt", "a") as log_file:
    log_file.write("END LOG FOR EXPERIMENT AT TIME " + timestamp_total_experiment + ".\n")
