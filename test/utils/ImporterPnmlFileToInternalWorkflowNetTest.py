import unittest

from MasterThesisProject.source.utils.ImportCCOxesFileToEventLog import import_cco_xes_file_to_event_log, import_xes_file_totally_ordered_log
from MasterThesisProject.source.utils.ImporterPnmlFileToInternalWorkflowNet import import_pnml_file_to_workflow_net
from pm4py.objects.petri_net.importer import importer as pnml_importer


class ImportTester(unittest.TestCase):
    def test_basic_imports(self):
        """
        Try to import the net from the file in the sibling folder
        :return:
        """
        # first check po example
        net, name_to_transition = import_pnml_file_to_workflow_net("8.pnml")
        log_po, invalid_labels = import_cco_xes_file_to_event_log("Repair_alpha_logwise_oneRperPoVar.xes", name_to_transition)
        # now to example
        net_review, name_to_transition_review = import_pnml_file_to_workflow_net("reviewing_5.pnml")
        log_to_with_invalid, invalid_traces_with = import_xes_file_totally_ordered_log("reviewing_complete_only.xes", name_to_transition_review, True)
        log_to_without_invalid, invaid_traces_without = import_xes_file_totally_ordered_log("reviewing_complete_only.xes", name_to_transition_review, False)

        # also compared with classic import
        net, initial_marking, final_marking = pnml_importer.apply("reviewing_5.pnml")
        # TODO so far I only had a look to verify it; looks good but should write proper unit test
        self.assertEqual(True, True)  # add assertion here

    def test_import_roadtraffic(self):
        net, name_to_transition = import_pnml_file_to_workflow_net("roadtraffic_5.pnml")




if __name__ == '__main__':
    unittest.main()
