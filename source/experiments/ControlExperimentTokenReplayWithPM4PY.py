import pm4py
import pandas as pd
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.algo.conformance.tokenreplay.algorithm import apply


path_nets: str = "data/nets/"
path_results: str = "results/to/Control_TokenReplay_PM4PY/"
path_logs: str = "data/totally_ordered_logs/"
do_persist_general_results: bool = True

log_net_pairs = [
                 # {"log": "BPI2012_alog.xes", "net": "bpi2012_alog_5.pnml"},
                 # {"log": "BPI2012_alog.xes", "net": "bpi2012_alog_10.pnml"},
                 # {"log": "BPI2012_olog.xes", "net": "bpi2012_olog_5.pnml"},
                 # {"log": "BPI2012_olog.xes", "net": "bpi2012_olog_10.pnml"},
                 # {"log": "BPI2019_C.xes", "net": "bpi2019c_5.pnml"},
                 # {"log": "BPI2019_C.xes", "net": "bpi2019c_10.pnml"},
                 # {"log": "reviewing_complete_only.xes", "net": "reviewing_5.pnml"},
                 # {"log": "reviewing_complete_only.xes", "net": "reviewing_10.pnml"},
                 {"log": "Road_Traffic_Fine.xes", "net": "roadtraffic_5.pnml"}
                 # {"log": "Road_Traffic_Fine.xes", "net": "roadtraffic_10.pnml"},
                 # {"log": "teleclaims_complete_only.xes", "net": "teleclaims_5.pnml"},
                 # {"log": "teleclaims_complete_only.xes", "net": "teleclaims_10.pnml"}
                ]

colum_names = [
                "Net name",
                "Log name",
                "Conformance level",
                "Missing Tokens",
                "Consumed Tokens",
                "Remaining Tokens",
                "Produced Tokens"
                ]

nets_with_trace_documentation = ["roadtraffic_5.pnml"]
column_names_trace_details = ["Net name",
                              "Log name",
                              "Missing Tokens",
                              "Consumed Tokens",
                              "Remaining Tokens",
                              "Produced Tokens"
                              ]

results_df: pd.DataFrame = pd.DataFrame(columns=colum_names)
trace_details_df: pd.DataFrame = pd.DataFrame(columns=column_names_trace_details)
token_replay_results = []
average_fitness: dict[str, float] = dict()
for pair in log_net_pairs:
    net_file_name = path_nets + pair["net"]
    log_file_name = path_logs + pair["log"]
    net, initial_marking, final_marking = pnml_importer.apply(net_file_name)
    log = pm4py.read_xes(log_file_name)
    result = apply(log, net, initial_marking, final_marking)
    token_replay_results.append(result)
    consumed_tokens: int = sum([trace_result["consumed_tokens"] for trace_result in result])
    produced_tokens: int = sum([trace_result["produced_tokens"] for trace_result in result])
    missing_tokens: int = sum([trace_result["missing_tokens"] for trace_result in result])
    remaining_tokens: int = sum([trace_result["remaining_tokens"] for trace_result in result])
    token_replay_norm: float = 0.5 * (1 - remaining_tokens/produced_tokens) + 0.5*(1-missing_tokens/consumed_tokens)
    trace_fitness_list = [trace_result["trace_fitness"] for trace_result in result]
    average_fitnes_result = sum(trace_fitness_list) / len(trace_fitness_list)
    average_fitness[pair["net"]] = average_fitnes_result
    results_df.loc[len(results_df)] = [pair["net"], pair["log"], token_replay_norm, missing_tokens, consumed_tokens, remaining_tokens, produced_tokens]
    if pair["net"] == nets_with_trace_documentation[0]:
        for trace_result in result:
            trace_details_df.loc[len(trace_details_df)] = [pair["net"],
                                                           pair["log"],
                                                           trace_result["missing_tokens"],
                                                           trace_result["consumed_tokens"],
                                                           trace_result["remaining_tokens"],
                                                           trace_result["produced_tokens"]
                                                           ]

trace_details_df.to_csv("results/to/Control_TokenReplay_PM4PY/trace_details_review5")
if do_persist_general_results:
    results_df.to_csv("results/to/Control_TokenReplay_PM4PY/control_results")

