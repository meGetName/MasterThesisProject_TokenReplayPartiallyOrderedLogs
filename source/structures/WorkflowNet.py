from typing import Iterable

from networkx import DiGraph


class PlaceWorkflowNet:
    def __init__(self, name: str, transitions_requiring: set = None, transitions_producing: set = None):
        self.name = name
        self.transitions_requiring = transitions_requiring if transitions_requiring is not None else set()
        self.transitions_producing = transitions_producing if transitions_producing is not None else set()

    def __str__(self):
        return self.name

    def make_inverted_copy(self):
        return PlaceWorkflowNet(self.name, self.transitions_producing, self.transitions_requiring)


class TransitionWorkflowNet:
    def __init__(self, name: str, activity_desription=None, preset: set = None, postset: set = None):
        self.name = name
        self.activity_description = activity_desription if activity_desription is not None else "MISSING"
        self.preset = preset if preset is not None else set()
        self.postset = postset if postset is not None else set()

    def __str__(self):
        return self.name

    def make_inverted_copy(self):
        return TransitionWorkflowNet(self.name, preset=self.postset, postset=self.preset)

    def add_place_to_postset(self, place: PlaceWorkflowNet):
        if place is None or not isinstance(place, PlaceWorkflowNet):
            return
        self.postset.add(place)
        place.transitions_producing.add(self)

    def add_place_iteration_to_postset(self, places: Iterable[PlaceWorkflowNet]):
        for place in places:
            self.add_place_to_postset(place)

    def add_place_to_preset(self, place: PlaceWorkflowNet):
        if place is None or not isinstance(place, PlaceWorkflowNet):
            return
        self.preset.add(place)
        place.transitions_requiring.add(self)

    def add_place_iteration_to_preset(self, places: Iterable[PlaceWorkflowNet]):
        for place in places:
            self.add_place_to_preset(place)


class WorkflowNet:

    def __init__(self, graph: DiGraph, start_place: PlaceWorkflowNet, end_place: PlaceWorkflowNet, places: set[PlaceWorkflowNet],
                 transitions: set[TransitionWorkflowNet]):
        self.graph = graph
        self.start_place = start_place
        self.end_place = end_place
        self.places = places
        inner_places_aux = set(places)
        inner_places_aux.remove(start_place)
        inner_places_aux.remove(end_place)
        self.inner_places: set = inner_places_aux
        self.transitions = transitions

    @staticmethod
    def make_class_instance_from_transitions(transitions: set[TransitionWorkflowNet], start_place: PlaceWorkflowNet,
                                             end_place: PlaceWorkflowNet) -> "WorkflowNet":
        places: set[PlaceWorkflowNet] = set()
        graph: DiGraph = DiGraph()
        graph.add_nodes_from(transitions)
        graph.add_nodes_from([start_place, end_place])
        for transition in transitions:
            for place in transition.preset:
                graph.add_edge(place, transition)
                places.add(place)
            for place in transition.postset:
                graph.add_edge(transition, place)
                places.add(place)
        return WorkflowNet(graph, start_place, end_place, places, transitions)

    def make_inverted_copy(self) -> "WorkflowNet":
        """
        Note: Method produces new transitions and is thus not compatible with old run structures.
        :return:
        """
        place_to_new_place: dict[PlaceWorkflowNet, PlaceWorkflowNet] = {place: PlaceWorkflowNet(place.name + "(Reverted)") for place in self.places}
        new_transitions: set[TransitionWorkflowNet] = set()
        for transition in self.transitions:
            new_transition: TransitionWorkflowNet = TransitionWorkflowNet(transition.name + "(Reverted)")
            new_transition.preset = {place_to_new_place[place] for place in transition.postset}
            new_transition.postset = {place_to_new_place[place] for place in transition.preset}
            new_transitions.add(new_transition)
        result: WorkflowNet = WorkflowNet.make_class_instance_from_transitions(new_transitions, place_to_new_place[self.end_place],
                                                                               place_to_new_place[self.start_place])
        return result
