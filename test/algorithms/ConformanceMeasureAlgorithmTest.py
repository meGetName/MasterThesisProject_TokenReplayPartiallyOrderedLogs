import time
import unittest

from networkx import DiGraph

from MasterThesisProject.source.algorithms.ConformanceMeasureAlgorithm import calculate_token_replay_conformance_norm_for_partial_order
from MasterThesisProject.source.structures.PartiallyOrderedEventLog import PartiallyOrderedEventLog
from MasterThesisProject.source.structures.PartiallyOrderedLogConformanceResult import PartiallyOrderedLogConformanceResult
from MasterThesisProject.source.structures.Run import Event4Run, Run
from MasterThesisProject.source.structures.WorkflowNet import PlaceWorkflowNet, TransitionWorkflowNet, WorkflowNet


class MyTestCase(unittest.TestCase):

    def setUp(self):
        # First workflow net: inspired by the textbook example from the process mining handbook
        self.net_1_place_initial: PlaceWorkflowNet = PlaceWorkflowNet("Start")
        self.net_1_place_1: PlaceWorkflowNet = PlaceWorkflowNet("P1")
        self.net_1_place_2a: PlaceWorkflowNet = PlaceWorkflowNet("P2A")
        self.net_1_place_2b: PlaceWorkflowNet = PlaceWorkflowNet("P2B")
        self.net_1_place_3a: PlaceWorkflowNet = PlaceWorkflowNet("P3A")
        self.net_1_place_3b: PlaceWorkflowNet = PlaceWorkflowNet("P3B")
        self.net_1_place_final: PlaceWorkflowNet = PlaceWorkflowNet("End")

        self.net_1_transition_start: TransitionWorkflowNet = TransitionWorkflowNet("T0")
        self.net_1_transition_start.add_place_to_preset(self.net_1_place_initial)
        self.net_1_transition_start.add_place_to_postset(self.net_1_place_1)
        self.net_1_transition_1: TransitionWorkflowNet = TransitionWorkflowNet("T1")
        self.net_1_transition_1.add_place_to_preset(self.net_1_place_1)
        self.net_1_transition_1.add_place_to_postset(self.net_1_place_2a)
        self.net_1_transition_1.add_place_to_postset(self.net_1_place_2b)
        self.net_1_transition_2a: TransitionWorkflowNet = TransitionWorkflowNet("T2A")
        self.net_1_transition_2a.add_place_to_preset(self.net_1_place_2a)
        self.net_1_transition_2a.add_place_to_postset(self.net_1_place_3a)
        self.net_1_transition_2b: TransitionWorkflowNet = TransitionWorkflowNet("T2B")
        self.net_1_transition_2b.add_place_to_preset(self.net_1_place_2b)
        self.net_1_transition_2b.add_place_to_postset(self.net_1_place_3b)
        self.net_1_transition_return: TransitionWorkflowNet = TransitionWorkflowNet("TR")
        self.net_1_transition_return.add_place_to_preset(self.net_1_place_3a)
        self.net_1_transition_return.add_place_to_preset(self.net_1_place_3b)
        self.net_1_transition_return.add_place_to_postset(self.net_1_place_1)
        self.net_1_transition_3: TransitionWorkflowNet = TransitionWorkflowNet("T3")
        self.net_1_transition_3.add_place_to_preset(self.net_1_place_3a)
        self.net_1_transition_3.add_place_to_preset(self.net_1_place_3b)
        self.net_1_transition_3.add_place_to_postset(self.net_1_place_final)
        self.net_1_transition_set: set[TransitionWorkflowNet] = {self.net_1_transition_start, self.net_1_transition_1, self.net_1_transition_2a,
                                                                 self.net_1_transition_2b, self.net_1_transition_3, self.net_1_transition_return}
        self.net_1: WorkflowNet = WorkflowNet.make_class_instance_from_transitions(self.net_1_transition_set, self.net_1_place_initial, self.net_1_place_final)

        # Second example net: in the net we first prepare three tokens on one place and then have three parallel activities
        # This will lead to natural runs that are impossible to solve purely by the heuristics.

        self.net_2_place_initial: PlaceWorkflowNet = PlaceWorkflowNet("Start")
        self.net_2_place_prep1: PlaceWorkflowNet = PlaceWorkflowNet("PP1")
        self.net_2_place_prep2: PlaceWorkflowNet = PlaceWorkflowNet("PP2")
        self.net_2_place_prep3: PlaceWorkflowNet = PlaceWorkflowNet("PP3")
        self.net_2_place_a1: PlaceWorkflowNet = PlaceWorkflowNet("PA1")
        self.net_2_place_a2: PlaceWorkflowNet = PlaceWorkflowNet("PA2")
        self.net_2_place_a3: PlaceWorkflowNet = PlaceWorkflowNet("PA3")
        self.net_2_place_end: PlaceWorkflowNet = PlaceWorkflowNet("End")

        self.net_2_transition_prep1: TransitionWorkflowNet = TransitionWorkflowNet("TP1")
        self.net_2_transition_prep1.add_place_to_preset(self.net_2_place_initial)
        self.net_2_transition_prep1.add_place_iteration_to_postset([self.net_2_place_prep1, self.net_2_place_prep3])
        self.net_2_transition_prep2: TransitionWorkflowNet = TransitionWorkflowNet("TP2")
        self.net_2_transition_prep2.add_place_to_preset(self.net_2_place_prep1)
        self.net_2_transition_prep2.add_place_iteration_to_postset([self.net_2_place_prep2, self.net_2_place_prep3])
        self.net_2_transition_prep3: TransitionWorkflowNet = TransitionWorkflowNet("TP3")
        self.net_2_transition_prep3.add_place_to_preset(self.net_2_place_prep2)
        self.net_2_transition_prep3.add_place_to_postset(self.net_2_place_prep3)
        self.net_2_transition_a1: TransitionWorkflowNet = TransitionWorkflowNet("TA1")
        self.net_2_transition_a1.add_place_to_preset(self.net_2_place_prep3)
        self.net_2_transition_a1.add_place_to_postset(self.net_2_place_a1)
        self.net_2_transition_a2: TransitionWorkflowNet = TransitionWorkflowNet("TA2")
        self.net_2_transition_a2.add_place_to_preset(self.net_2_place_prep3)
        self.net_2_transition_a2.add_place_to_postset(self.net_2_place_a2)
        self.net_2_transition_a3: TransitionWorkflowNet = TransitionWorkflowNet("TA3")
        self.net_2_transition_a3.add_place_to_preset(self.net_2_place_prep3)
        self.net_2_transition_a3.add_place_to_postset(self.net_2_place_a3)
        self.net_2_transition_final: TransitionWorkflowNet = TransitionWorkflowNet("TF")
        self.net_2_transition_final.add_place_iteration_to_preset([self.net_2_place_a1, self.net_2_place_a2, self.net_2_place_a3])
        self.net_2_transition_final.add_place_to_postset(self.net_2_place_end)
        self.net_2_transition_set: set[TransitionWorkflowNet] = {self.net_2_transition_prep1, self.net_2_transition_prep2, self.net_2_transition_prep3,
                                                                 self.net_2_transition_a1, self.net_2_transition_a2, self.net_2_transition_a3,
                                                                 self.net_2_transition_final}
        self.net_2: WorkflowNet = WorkflowNet.make_class_instance_from_transitions(self.net_2_transition_set, self.net_2_place_initial,
                                                                                   self.net_2_place_end)

    def test_first_net_first_log_example(self):
        # Prepare two runs, one correct one with one switched action
        run_1_event_1: Event4Run = Event4Run("Run1Event1", self.net_1_transition_start)
        run_1_event_2: Event4Run = Event4Run("Run1Event2", self.net_1_transition_1)
        run_1_event_3: Event4Run = Event4Run("Run1Event3", self.net_1_transition_2a)
        run_1_event_4: Event4Run = Event4Run("Run1Event4", self.net_1_transition_2b)
        run_1_event_5: Event4Run = Event4Run("Run1Event5", self.net_1_transition_3)
        run_1_order: DiGraph = DiGraph([(run_1_event_1, run_1_event_2), (run_1_event_2, run_1_event_3), (run_1_event_2, run_1_event_4),
                                        (run_1_event_3, run_1_event_5), (run_1_event_4, run_1_event_5)])
        run_1: Run = Run(run_1_order)

        run_2_event_1: Event4Run = Event4Run("Run2Event1", self.net_1_transition_start)
        run_2_event_2: Event4Run = Event4Run("Run2Event2", self.net_1_transition_return)
        run_2_event_3: Event4Run = Event4Run("Run2Event3", self.net_1_transition_1)
        run_2_event_4: Event4Run = Event4Run("Run2Event4", self.net_1_transition_2b)
        run_2_event_5: Event4Run = Event4Run("Run2Event5", self.net_1_transition_2a)
        run_2_event_6: Event4Run = Event4Run("Run2Event6", self.net_1_transition_3)
        run_2_order: DiGraph = DiGraph([(run_2_event_1, run_2_event_2), (run_2_event_2, run_2_event_3), (run_2_event_3, run_2_event_4),
                                        (run_2_event_3, run_2_event_5), (run_2_event_4, run_2_event_6), (run_2_event_5, run_2_event_6)])
        run_2: Run = Run(run_2_order)

        run_to_frequency: dict[Run, int] = {run_1: 3, run_2: 5}
        event_log: PartiallyOrderedEventLog = PartiallyOrderedEventLog(run_to_frequency)
        result: PartiallyOrderedLogConformanceResult = calculate_token_replay_conformance_norm_for_partial_order(event_log, self.net_1, True)

        self.assertEqual(1, result.run_to_conformance_result[run_1].conformance_level_min)  # first run should be completely fine
        self.assertEqual(0.8035714285714286, result.run_to_conformance_result[run_2].conformance_level_min)
        self.assertEqual(0.8666232921275212, result.conformance_level)

    def test_second_net_second_log(self):
        """
        In this example we construct a run where the theoretical number of missing tokens is zero (which would indeed happen if the
        first three event would be in sequence). Thus, we are forced to use the flow network algorithm.
        In the optimal tokenflow the transitions TA1, TA2, TA3 can get their token, and it is removed, so no missing tokens on PP3.
        But PP1 and PP2 have one missing token each and therefore also one remaining token. Thus, the conformance result should be
        0.5(1 - 2/10) + 0.5(1 - 2/10)  = 0.8
        :return:
        """
        run_1_event_1: Event4Run = Event4Run("Run1Event1", self.net_2_transition_prep1)
        run_1_event_2: Event4Run = Event4Run("Run1Even2", self.net_2_transition_prep2)
        run_1_event_3: Event4Run = Event4Run("Run1Event3", self.net_2_transition_prep3)
        run_1_event_4: Event4Run = Event4Run("Run1Event4", self.net_2_transition_a1)
        run_1_event_5: Event4Run = Event4Run("Run1Event5", self.net_2_transition_a2)
        run_1_event_6: Event4Run = Event4Run("Run1Event6", self.net_2_transition_a3)
        run_1_event_7: Event4Run = Event4Run("Run1Event7", self.net_2_transition_final)
        run_1_order: DiGraph = DiGraph([(run_1_event_1, run_1_event_4), (run_1_event_1, run_1_event_5), (run_1_event_1, run_1_event_6),
                                        (run_1_event_2, run_1_event_4), (run_1_event_2, run_1_event_5), (run_1_event_2, run_1_event_6),
                                        (run_1_event_3, run_1_event_4), (run_1_event_3, run_1_event_5), (run_1_event_3, run_1_event_6),
                                        (run_1_event_4, run_1_event_7), (run_1_event_5, run_1_event_7), (run_1_event_6, run_1_event_7)])
        run_1: Run = Run(run_1_order)

        run_to_frequency: dict[Run, int] = {run_1: 3}
        event_log: PartiallyOrderedEventLog = PartiallyOrderedEventLog(run_to_frequency)
        start_full_algorithm = time.time()
        result: PartiallyOrderedLogConformanceResult = calculate_token_replay_conformance_norm_for_partial_order(event_log, self.net_2, True)
        end_full_algorithm = time.time()
        time_full_algorithm = end_full_algorithm - start_full_algorithm
        self.assertEqual(0.8, result.conformance_level)
        # following is just a sanity check: the quick procedure should yield an upper bound bigger than the conformance result and
        # a lower bound; indeed in this case the upper bound should be 1, as theoretically there are no missing tokens (in the correct order)
        start_quick_algorithm = time.time()
        result_quick_algorithm: PartiallyOrderedLogConformanceResult = calculate_token_replay_conformance_norm_for_partial_order(event_log, self.net_2, False)
        end_quick_algorithm = time.time()
        time_quick_algorithm = end_quick_algorithm - start_quick_algorithm
        self.assertGreaterEqual(result_quick_algorithm.upper_bound_conformance, result.conformance_level)
        self.assertLessEqual(result_quick_algorithm.lower_bound_conformance, result.conformance_level)
        self.assertAlmostEqual(1.0, result_quick_algorithm.upper_bound_conformance, places=8)


if __name__ == '__main__':
    unittest.main()
