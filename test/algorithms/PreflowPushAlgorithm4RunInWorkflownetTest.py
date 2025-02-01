import unittest

from networkx import DiGraph

from MasterThesisProject.source.algorithms.FindTotalOrderForPartialOrder import find_total_order_for_run
from MasterThesisProject.source.algorithms.PreflowPushAlgorithm4RunInWorkflownet import find_optimal_tokenflow_for_place
from MasterThesisProject.source.structures.Run import Event4Run, Run
from MasterThesisProject.source.structures.SinglePlaceTokenResult import SinglePlaceTokenResult
from MasterThesisProject.source.structures.WorkflowNet import PlaceWorkflowNet, TransitionWorkflowNet


class PreflowPushAlgorithmTestcases(unittest.TestCase):

    def setUp(self):
        """
        We effectively need only one place and four events (one for each possible combination 'doesProduce'/'doesConsume')
        to build any potential run. Note that the universal place has not set the following and proceeding transitions
        correctly, but we do not reference them in the preflow push algorithm.
        :return:
        """
        self.place = PlaceWorkflowNet("UniversalTestPlace", set(), set())
        self.transition_nothing = TransitionWorkflowNet("Test transition, not consuming or producing", set(), set())
        self.transition_only_consuming = TransitionWorkflowNet("Test transition, only consuming", {self.place}, set())
        self.transition_only_producing = TransitionWorkflowNet("Test transition, only producing", set(), {self.place})
        self.transition_producing_and_consuming = TransitionWorkflowNet("Test transition, consuming and producing",
                                                                        {self.place}, {self.place})

    def test_first_example(self):
        """
        The structure of the run is the following:
            E1 -- E3       E6
                     --  --
                       E5
                     --  --
            E2 -- E4       E7
        E3 is producing, E4, E6, E7 are consuming.
        :return:
        """
        event_1: Event4Run = Event4Run("Event 1", self.transition_nothing)
        event_2: Event4Run = Event4Run("Event 2", self.transition_nothing)
        event_3: Event4Run = Event4Run("Event 3", self.transition_only_producing)
        event_4: Event4Run = Event4Run("Event 4", self.transition_only_consuming)
        event_5: Event4Run = Event4Run("Event 5", self.transition_nothing)
        event_6: Event4Run = Event4Run("Event 6", self.transition_only_consuming)
        event_7: Event4Run = Event4Run("Event 7", self.transition_only_consuming)
        partial_order: DiGraph = DiGraph()
        partial_order.add_edges_from([(event_1, event_3), (event_3, event_5), (event_2, event_4), (event_4, event_5),
                                      (event_5, event_6), (event_5, event_7)])
        run: Run = Run(partial_order)
        run.total_order = find_total_order_for_run(run)
        heuristic: SinglePlaceTokenResult = SinglePlaceTokenResult(1, 3, 0,
                                                                   0, 0, 0)
        result: SinglePlaceTokenResult = find_optimal_tokenflow_for_place(self.place, run, heuristic)
        self.assertEqual(result.consumed_token, 3)  # add assertion here
        self.assertEqual(result.produced_token, 1)
        self.assertEqual(result.missing_token_min, 2)
        self.assertEqual(result.missing_token_max, 2)
        self.assertEqual(result.remaining_token_min, 0)
        self.assertEqual(result.remaining_token_max, 0)

    def test_second_example(self):
        event_1: Event4Run = Event4Run("Event 1", self.transition_producing_and_consuming)
        event_2: Event4Run = Event4Run("Event 2", self.transition_nothing)
        event_3: Event4Run = Event4Run("Event 3", self.transition_only_producing)
        event_4: Event4Run = Event4Run("Event 4", self.transition_nothing)
        event_5: Event4Run = Event4Run("Event 5", self.transition_nothing)
        event_6: Event4Run = Event4Run("Event 6", self.transition_only_producing)
        event_7: Event4Run = Event4Run("Event 7", self.transition_only_producing)
        event_8: Event4Run = Event4Run("Event 8", self.transition_only_consuming)
        event_9: Event4Run = Event4Run("Event 9", self.transition_only_consuming)
        partial_order: DiGraph = DiGraph()
        partial_order.add_edges_from(
            [(event_1, event_2), (event_3, event_4), (event_2, event_4), (event_4, event_5),
             (event_5, event_7), (event_5, event_8), (event_4, event_6), (event_6, event_9)])
        run: Run = Run(partial_order)
        run.total_order = find_total_order_for_run(run)
        heuristic: SinglePlaceTokenResult = SinglePlaceTokenResult(4, 3, 0,
                                                                   0, 0, 0)
        result: SinglePlaceTokenResult = find_optimal_tokenflow_for_place(self.place, run, heuristic)
        self.assertEqual(result.produced_token, 4)
        self.assertEqual(result.consumed_token, 3)
        self.assertEqual(result.missing_token_max, 1)
        self.assertEqual(result.missing_token_min, 1)
        self.assertEqual(result.remaining_token_max, 2)
        self.assertEqual(result.remaining_token_min, 2)

    def test_third_example(self):
        """
        example where it is impossible to consume any token.
        :return:
        """
        event_1: Event4Run = Event4Run("Event 1", self.transition_nothing)
        event_2: Event4Run = Event4Run("Event 2", self.transition_nothing)
        event_3: Event4Run = Event4Run("Event 3", self.transition_only_consuming)
        event_4: Event4Run = Event4Run("Event 4", self.transition_only_producing)
        event_5: Event4Run = Event4Run("Event 5", self.transition_nothing)
        event_6: Event4Run = Event4Run("Event 6", self.transition_nothing)
        event_7: Event4Run = Event4Run("Event 7", self.transition_only_producing)
        event_8: Event4Run = Event4Run("Event 8", self.transition_nothing)
        event_9: Event4Run = Event4Run("Event 9", self.transition_nothing)
        partial_order: DiGraph = DiGraph()
        partial_order.add_edges_from(
            [(event_1, event_3), (event_2, event_3), (event_3, event_4), (event_3, event_5),
             (event_4, event_6), (event_5, event_6), (event_6, event_7), (event_7, event_8), (event_8, event_9)])
        run: Run = Run(partial_order)
        run.total_order = find_total_order_for_run(run)
        heuristic: SinglePlaceTokenResult = SinglePlaceTokenResult(2, 1, 0,
                                                                   0, 0, 0)
        result: SinglePlaceTokenResult = find_optimal_tokenflow_for_place(self.place, run, heuristic)
        self.assertEqual(result.produced_token, 2)
        self.assertEqual(result.consumed_token, 1)
        self.assertEqual(result.missing_token_max, 1)
        self.assertEqual(result.missing_token_min, 1)
        self.assertEqual(result.remaining_token_max, 2)
        self.assertEqual(result.remaining_token_min, 2)

    def test_fourth_example(self):
        """
        modification of third example but here it is possible; relation is made a bit more complicated, and
        we give only one producing and one consuming
        :return:
        """
        event_1: Event4Run = Event4Run("Event 1", self.transition_nothing)
        event_2: Event4Run = Event4Run("Event 2", self.transition_nothing)
        event_3: Event4Run = Event4Run("Event 3", self.transition_only_producing)
        event_4: Event4Run = Event4Run("Event 4", self.transition_nothing)
        event_5: Event4Run = Event4Run("Event 5", self.transition_nothing)
        event_6: Event4Run = Event4Run("Event 6", self.transition_nothing)
        event_7: Event4Run = Event4Run("Event 7", self.transition_nothing)
        event_8: Event4Run = Event4Run("Event 8", self.transition_nothing)
        event_9: Event4Run = Event4Run("Event 9", self.transition_nothing)
        event_10: Event4Run = Event4Run("Event 10", self.transition_nothing)
        event_11: Event4Run = Event4Run("Event 11", self.transition_only_consuming)
        event_12: Event4Run = Event4Run("Event 12", self.transition_nothing)
        partial_order: DiGraph = DiGraph()
        partial_order.add_edges_from(
            [(event_1, event_3), (event_2, event_3), (event_3, event_4), (event_3, event_5),
             (event_4, event_6), (event_5, event_6), (event_6, event_7), (event_7, event_8), (event_8, event_9),
             (event_8, event_10), (event_10, event_11), (event_10, event_12)])
        run: Run = Run(partial_order)
        run.total_order = find_total_order_for_run(run)
        heuristic: SinglePlaceTokenResult = SinglePlaceTokenResult(1, 1, 0,
                                                                   0, 0, 0)
        result: SinglePlaceTokenResult = find_optimal_tokenflow_for_place(self.place, run, heuristic)
        self.assertEqual(result.produced_token, 1)
        self.assertEqual(result.consumed_token, 1)
        self.assertEqual(result.missing_token_max, 0)
        self.assertEqual(result.missing_token_min, 0)
        self.assertEqual(result.remaining_token_max, 0)
        self.assertEqual(result.remaining_token_min, 0)


if __name__ == '__main__':
    unittest.main()
