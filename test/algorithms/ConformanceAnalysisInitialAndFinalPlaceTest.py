import unittest

from networkx import DiGraph

from MasterThesisProject.source.algorithms.ConformanceAnalysisInitialAndFinalPlace import calculate_token_analysis_for_initial_and_final_place
from MasterThesisProject.source.structures.Run import Event4Run, Run
from MasterThesisProject.source.structures.SinglePlaceTokenResult import SinglePlaceTokenResult
from MasterThesisProject.source.structures.WorkflowNet import PlaceWorkflowNet, TransitionWorkflowNet, WorkflowNet


class MyTestCase(unittest.TestCase):

    def setUp(self):
        """
        We construct one workflow net for all tests; the precise structure of the net is irrelevant as only start and end
        are important.
        :return:
        """
        initial_place: PlaceWorkflowNet = PlaceWorkflowNet("Start place")
        final_place: PlaceWorkflowNet = PlaceWorkflowNet("Final place")
        internal_place: PlaceWorkflowNet = PlaceWorkflowNet("Internal place")

        transition_1: TransitionWorkflowNet = TransitionWorkflowNet("Transition 1")
        transition_1.add_place_to_preset(initial_place)
        transition_1.add_place_to_postset(internal_place)
        self.transition_1 = transition_1
        transition_2: TransitionWorkflowNet = TransitionWorkflowNet("Transition 2")
        transition_2.add_place_to_preset(initial_place)
        transition_2.add_place_to_postset(final_place)
        self.transition_2 = transition_2
        transition_3: TransitionWorkflowNet = TransitionWorkflowNet("Transition 3")
        transition_3.add_place_to_preset(internal_place)
        transition_3.add_place_to_postset(final_place)
        self.transition_3 = transition_3
        transition_4: TransitionWorkflowNet = TransitionWorkflowNet("Transition 4")
        transition_4.add_place_to_preset(internal_place)
        transition_4.add_place_to_postset(final_place)
        self.transition_4 = transition_4
        transitions: set[TransitionWorkflowNet] = {transition_1, transition_2, transition_3, transition_4}
        self.test_workflownet = WorkflowNet.make_class_instance_from_transitions(transitions, initial_place, final_place)

    def check_token_result_against_expected(self, expected: SinglePlaceTokenResult, observed: SinglePlaceTokenResult):
        self.assertEqual(expected.produced_token, observed.produced_token)
        self.assertEqual(expected.consumed_token, observed.consumed_token)
        self.assertEqual(expected.missing_token_min, observed.missing_token_min)
        self.assertEqual(expected.missing_token_max, observed.missing_token_max)
        self.assertEqual(expected.remaining_token_min, observed.remaining_token_min)
        self.assertEqual(expected.remaining_token_max, expected.remaining_token_max)

    def test_first_run_example(self):
        # Prepare run for test
        event_1: Event4Run = Event4Run("Event 1", self.transition_3)
        event_2: Event4Run = Event4Run("Event 2", self.transition_2)
        event_3: Event4Run = Event4Run("Event 3", self.transition_1)
        event_4: Event4Run = Event4Run("Event 4", self.transition_1)
        event_5: Event4Run = Event4Run("Event 5", self.transition_4)
        event_6: Event4Run = Event4Run("Event 6", self.transition_1)
        event_7: Event4Run = Event4Run("Event 7", self.transition_2)
        event_8: Event4Run = Event4Run("Event 8", self.transition_3)
        partial_order: DiGraph = DiGraph()
        partial_order.add_edges_from([(event_1, event_3), (event_2, event_4), (event_3, event_5), (event_4, event_5),
                                      (event_5, event_6), (event_5, event_7), (event_5, event_8)])
        run: Run = Run(partial_order)
        #act
        result_start_place, result_final_place = calculate_token_analysis_for_initial_and_final_place(run, self.test_workflownet)
        # assert
        expected_result_start_place: SinglePlaceTokenResult = SinglePlaceTokenResult(1, 5, 4, 4,
                                                                                     0, 0)
        self.check_token_result_against_expected(expected_result_start_place, result_start_place)
        expected_result_final_place: SinglePlaceTokenResult = SinglePlaceTokenResult(5, 1, 0,0,
                                                                                     4,4)
        self.check_token_result_against_expected(expected_result_final_place, result_final_place)

    def test_second_example_run(self):
        """
        In this example we study a situation where the initial token is not consumed. Thus in the initial result we have zero missing
        but one remaining token (special case).
        :return:
        """
        # Prepare run for test
        event_1: Event4Run = Event4Run("Event 1", self.transition_3)
        event_2: Event4Run = Event4Run("Event 2", self.transition_4)
        event_3: Event4Run = Event4Run("Event 3", self.transition_3)
        event_4: Event4Run = Event4Run("Event 4", self.transition_4)
        event_5: Event4Run = Event4Run("Event 5", self.transition_3)
        event_6: Event4Run = Event4Run("Event 6", self.transition_4)
        event_7: Event4Run = Event4Run("Event 7", self.transition_4)
        event_8: Event4Run = Event4Run("Event 8", self.transition_3)
        partial_order: DiGraph = DiGraph()
        partial_order.add_edges_from([(event_1, event_2), (event_2, event_4), (event_2, event_4), (event_2, event_5),
                                      (event_5, event_6), (event_4, event_6), (event_3, event_6), (event_6, event_7),
                                      (event_6, event_8)])
        run: Run = Run(partial_order)
        # act
        result_start_place, result_final_place = calculate_token_analysis_for_initial_and_final_place(run, self.test_workflownet)
        # assert
        expected_result_start_place: SinglePlaceTokenResult = SinglePlaceTokenResult(1, 0 ,0,
                                                                                     0, 1,1)
        self.check_token_result_against_expected(expected_result_start_place, result_start_place)
        expected_result_final_place: SinglePlaceTokenResult = SinglePlaceTokenResult(8, 1, 0,0,
                                                                                     7,7)
        self.check_token_result_against_expected(expected_result_final_place, result_final_place)

    def test_third_example_run(self):
        """
        In this example we study a situation where no token for the final place is produced. Thus in the result for the final place
        we have one missing and no remaining token (special case).
        :return:
        """
        # Prepare run for test
        event_1: Event4Run = Event4Run("Event 1", self.transition_1)
        event_2: Event4Run = Event4Run("Event 2", self.transition_1)
        event_3: Event4Run = Event4Run("Event 3", self.transition_1)
        event_4: Event4Run = Event4Run("Event 4", self.transition_1)
        event_5: Event4Run = Event4Run("Event 5", self.transition_1)
        event_6: Event4Run = Event4Run("Event 6", self.transition_1)
        event_7: Event4Run = Event4Run("Event 7", self.transition_1)
        event_8: Event4Run = Event4Run("Event 8", self.transition_1)
        partial_order: DiGraph = DiGraph()
        partial_order.add_edges_from([(event_1, event_2), (event_2, event_4), (event_2, event_4), (event_2, event_5),
                                      (event_5, event_6), (event_4, event_6), (event_3, event_6), (event_6, event_7),
                                      (event_6, event_8)])
        run: Run = Run(partial_order)
        # act
        result_start_place, result_final_place = calculate_token_analysis_for_initial_and_final_place(run, self.test_workflownet)
        # assert
        expected_result_start_place: SinglePlaceTokenResult = SinglePlaceTokenResult(1, 8 ,7,
                                                                                     7, 0,0)
        self.check_token_result_against_expected(expected_result_start_place, result_start_place)
        expected_result_final_place: SinglePlaceTokenResult = SinglePlaceTokenResult(0, 1, 1,1,
                                                                                     0,0)
        self.check_token_result_against_expected(expected_result_final_place, result_final_place)



if __name__ == '__main__':
    unittest.main()
