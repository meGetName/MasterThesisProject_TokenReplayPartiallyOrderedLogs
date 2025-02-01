import networkx as nx

from MasterThesisProject.source.structures.TotalOrderForRun import TotalOrder4Run
from MasterThesisProject.source.structures.WorkflowNet import TransitionWorkflowNet


class Event4Run:
    def __init__(self, name: str, label: TransitionWorkflowNet):
        self.name = name
        self.label = label

    def __str__(self):
        return "Event %s with Label %s" % (self.name, self.label)


class Run:
    def __init__(self, partial_order: nx.DiGraph):
        self.partial_order: nx.DiGraph = partial_order
        self.labels: dict = {event:  event.label for event in list(partial_order)}
        self.total_order: TotalOrder4Run = None

    def __str__(self):
        return "Run with " + str(len(self.labels)) + " Events (stringMethod)"

    def __repr__(self):
        return "Run with " + str(len(self.labels)) + " Events (repr-Method)"
