import networkx as nx

from MasterThesisProject.source.structures.TotalOrderForRun import TotalOrder4Run
from MasterThesisProject.source.structures.WorkflowNet import TransitionWorkflowNet


class Event4Run:
    def __init__(self, name: str, label: TransitionWorkflowNet):
        self.name = name
        self.label = label

    def __str__(self):
        return "Event name: %s, Label: %s, Activity %s" % (self.name, self.label, self.label.activity_description)


class Run:
    def __init__(self, partial_order: nx.DiGraph, name_foreign_source: str = "UNKNOWN"):
        self.partial_order: nx.DiGraph = partial_order
        self.labels: dict = {event:  event.label for event in list(partial_order)}
        self.total_order: TotalOrder4Run = None
        self.name_foreign_source = "UNKNOWN" if name_foreign_source is None else name_foreign_source

    def __str__(self):
        return "Run with " + str(len(self.labels)) + " Events (Foreign name: " + self.name_foreign_source + ")."

    def __repr__(self):
        return "Run with " + str(len(self.labels)) + " Events (repr-Method)"
