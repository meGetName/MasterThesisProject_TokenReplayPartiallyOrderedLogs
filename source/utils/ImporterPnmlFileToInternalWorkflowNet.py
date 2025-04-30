from pm4py import PetriNet, Marking
from pm4py.objects.petri_net.importer import importer as pnml_importer

from MasterThesisProject.source.structures.WorkflowNet import TransitionWorkflowNet, WorkflowNet, PlaceWorkflowNet


def import_pnml_file_to_workflow_net(file_path: str) -> (WorkflowNet, dict[str, TransitionWorkflowNet]):
    net: PetriNet
    initial_marking: Marking
    final_marking: Marking
    net, initial_marking, final_marking = pnml_importer.apply(file_path)
    # find names of initial and final place
    initial_place_name: str = list(initial_marking.keys())[0].name
    final_place_name: str = list(final_marking.keys())[0].name
    # prepare my format for transitions and places
    name_to_place: dict[str, PlaceWorkflowNet] = dict()
    name_to_transition: dict[str, TransitionWorkflowNet] = dict()
    # The label is the human readable description of the transition
    label_to_transition: dict[str, TransitionWorkflowNet] = dict()
    for place in net.places:
        name_to_place[place.name] = PlaceWorkflowNet(place.name)
    for transition in net.transitions:
        transition_name = transition.name
        label: str = transition.label
        name_to_transition[transition_name] = TransitionWorkflowNet(transition_name, label)
        if label is None:
            # The transition has to be the START or END Transition
            if transition.properties["trans_name_tag"] == "ArtificialStart":
                label_to_transition["START"] = name_to_transition[transition_name]
                label_to_transition["START"].activity_description = "START"
            elif transition.properties["trans_name_tag"] == "ArtificialEnd":
                label_to_transition["END"] = name_to_transition[transition_name]
                label_to_transition["END"].activity_description = "END"
            else:
                raise Exception("Transition without label was found that is not start or end!")
        else:
            label_to_transition[label] = name_to_transition[transition_name]
    # prepare info in transitions, so we can build WorkflowNet from that
    for arc in net.arcs:
        if isinstance(arc.source, PetriNet.Transition):
            name_transition: str = arc.source.name
            name_place: str = arc.target.name
            transition: TransitionWorkflowNet = name_to_transition[name_transition]
            transition.add_place_to_postset(name_to_place[name_place])
        elif isinstance(arc.target, PetriNet.Transition):
            name_transition: str = arc.target.name
            name_place: str = arc.source.name
            transition: TransitionWorkflowNet = name_to_transition[name_transition]
            transition.add_place_to_preset(name_to_place[name_place])
        else:
            raise Exception("The format of the arc does not fit to a Petri net.")
    # We add an invalid transitions which can be used for logs with invalid transitions name
    invalid_transition: TransitionWorkflowNet = TransitionWorkflowNet("INVALID TRANSITION")
    label_to_transition["INVALID"] = invalid_transition
    name_to_transition["INVALID TRANSITION"] = invalid_transition
    # It remains to use the static constructor of our Workflow net format
    result_net: WorkflowNet = WorkflowNet.make_class_instance_from_transitions(set(name_to_transition.values()), name_to_place[initial_place_name],
                                                                               name_to_place[final_place_name])

    return result_net, label_to_transition
