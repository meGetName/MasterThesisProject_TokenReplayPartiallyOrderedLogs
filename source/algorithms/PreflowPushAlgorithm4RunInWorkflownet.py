import math
from collections import deque
from enum import Enum

from networkx import DiGraph

from MasterThesisProject.source.structures.Run import Run, Event4Run
from MasterThesisProject.source.structures.SinglePlaceTokenResult import SinglePlaceTokenResult
from MasterThesisProject.source.structures.WorkflowNet import PlaceWorkflowNet


class NodeType(Enum):
    SOURCE = 1
    SINK = 2
    # Robins Notation for consuming part of event
    TOP = 3
    # Robins Notation for producing part of event
    BOTTOM = 4

    def __str__(self):
        return self.name


class Node4FlowNetwork:
    def __init__(self, node_type: NodeType, event: Event4Run, label: int = -1):
        self.type = node_type
        self.event = event
        self.excess: int = 0
        self.label = label

    def __str__(self):
        return '%s-node of event %s with excess %d and label %d.' % (self.type, self.event, self.excess, self.label)


class MaxFlowNetwork:
    """
    Class keeps the relevant information for the maximum flow network implied by the run.
    ...
    Attributes:
    ----------
        number_sink_neighbors : int
            we need this information for an early stop of the preflow push algorithm
        realized_flow : int
            this allows us to early exit the algorithm when all possible flow has reached the sink; we update this
            during the algorithm
        maximal_possible_flow : int
            correct initilization is done in the construction of the flow network
    """
    def __init__(self, sink: Node4FlowNetwork, source: Node4FlowNetwork, network: DiGraph, number_sink_neighbor: int,
                 sink_neighbors: set[Node4FlowNetwork]):
        self.sink = sink
        self.source = source
        self.network = network
        self.number_sink_neighbors = number_sink_neighbor
        self.sink_neighbors = sink_neighbors
        self.unreachable_sink_neighbors: int = 0
        self.realized_flow: int = 0
        self.maximal_possible_flow: int = 0


def find_optimal_tokenflow_for_place(place: PlaceWorkflowNet, run: Run, heuristic: SinglePlaceTokenResult) \
                                     -> SinglePlaceTokenResult:
    """
    Function calculates the minimal possible number of missing tokens in the optimal tokenflow.
    :param place:
    :param run:
    :param heuristic: Previous calculated heuristic has already information on produced and consumed tokens.
    :return:
    """

    def build_maximal_flow_problem(consumed_token: int) -> MaxFlowNetwork:
        """
        Build network and also prepare initial labeling.
        :param consumed_token:
        :return:
        """
        # source and sink have special labeling, and we know the number of nodes in the flow network in advance
        sink: Node4FlowNetwork = Node4FlowNetwork(NodeType.SINK, None, 0)
        size_flow_network = 2 * len(run.total_order.order) + 2
        default_label: int = size_flow_network - 1
        source: Node4FlowNetwork = Node4FlowNetwork(NodeType.SOURCE, None, size_flow_network)
        graph: DiGraph = DiGraph()
        result_network: MaxFlowNetwork = MaxFlowNetwork(sink, source, graph, 0, set())
        partial_order_run: DiGraph = run.partial_order
        list_events: list[Event4Run] = list(partial_order_run)
        # we will calculate precise initial labels for the nodes; nodes that are not reached cannot flow to the sink,
        # thus we choose a default label that disqualifies them but is still compatible with source
        # , i.e., the size of the flow network - 1
        top_nodes: dict = {event: Node4FlowNetwork(NodeType.TOP, event, default_label) for event in list_events}
        bottom_nodes: dict = {event: Node4FlowNetwork(NodeType.BOTTOM, event, default_label) for event in list_events}
        queue_for_labeling: deque[Node4FlowNetwork] = deque()
        for event in list_events:
            # Connect top to bottom node
            graph.add_edge(top_nodes[event], bottom_nodes[event], capacity=consumed_token, flow=0,
                           residual=consumed_token)
            graph.add_edge(bottom_nodes[event], top_nodes[event], capacity=0, flow=0, residual=0)
            # connect source if a token on place p is produced in the event
            if place in event.label.postset:
                graph.add_edge(source, bottom_nodes[event], capacity=1, flow=0, residual=1)
                graph.add_edge(bottom_nodes[event], source, capacity=0, flow=0, residual=0)
            # connect sink if a token on place p is consumed in the event and set label in top node
            if place in event.label.preset:
                top_node_for_event: Node4FlowNetwork = top_nodes[event]
                top_node_for_event.label = 1
                queue_for_labeling.append(top_node_for_event)
                graph.add_edge(top_node_for_event, sink, capacity=1, flow=0, residual=1)
                graph.add_edge(sink, top_node_for_event, capacity=0, flow=0, residual=0)
                result_network.number_sink_neighbors += 1
                result_network.sink_neighbors.add(top_node_for_event)
            # connect bottom node to top node of following events
            for next_event in partial_order_run.neighbors(event):
                graph.add_edge(bottom_nodes[event], top_nodes[next_event], capacity=consumed_token, flow=0,
                               residual=consumed_token)
                graph.add_edge(top_nodes[next_event], bottom_nodes[event], capacity=0, flow=0, residual=0)
        # now fill labels beginning from the top nodes connected to the sink
        while queue_for_labeling:
            next_node: Node4FlowNetwork = queue_for_labeling.popleft()
            neighbor_without_label: set[Node4FlowNetwork] = {node for node in graph.predecessors(next_node)
                            if (node.label == default_label and graph.edges[node, next_node]['capacity'] != 0)}
            for neighbor_node in neighbor_without_label:
                neighbor_node.label = next_node.label + 1
            queue_for_labeling.extend(neighbor_without_label)
        return result_network

    flow_network: MaxFlowNetwork = build_maximal_flow_problem(heuristic.consumed_token)
    active_nodes: set[Node4FlowNetwork] = set()

    def do_initial_push():
        """
        NOTE: due to the network structure we never directly push from sink to source!
        :return:
        """
        for source_neighbor in flow_network.network.neighbors(flow_network.source):
            flow_network.network.edges[flow_network.source, source_neighbor]["flow"] = 1
            flow_network.network.edges[flow_network.source, source_neighbor]["residual"] = 0
            flow_network.network.edges[source_neighbor, flow_network.source]["flow"] = -1
            flow_network.network.edges[source_neighbor, flow_network.source]["residual"] = 1
            source_neighbor.excess = 1
            flow_network.source.excess -= 1
            flow_network.maximal_possible_flow += 1
            active_nodes.add(source_neighbor)

    def push(from_node: Node4FlowNetwork, to_node: Node4FlowNetwork):
        amount: int = min(from_node.excess, flow_network.network.edges[from_node, to_node]["residual"])
        flow_network.network.edges[from_node, to_node]["flow"] += amount
        flow_network.network.edges[to_node, from_node]["flow"] -= amount
        flow_network.network.edges[from_node, to_node]["residual"] -= amount
        flow_network.network.edges[to_node, from_node]["residual"] += amount
        from_node.excess -= amount
        to_node.excess += amount
        # if flow reached the sink, we can higher the already realized flow
        if to_node == flow_network.sink:
            flow_network.realized_flow += amount

    def relabel(node: Node4FlowNetwork):
        new_label: int = math.inf
        for neighbor in flow_network.network.neighbors(node):
            if flow_network.network.edges[node, neighbor]["residual"] > 0:
                new_label = min(new_label, neighbor.label)
        node.label = new_label + 1
        # the sink neighbor has now increased its label and can no longer push to the is sink
        if node in flow_network.sink_neighbors:
            flow_network.unreachable_sink_neighbors += 1

    def discharge(node: Node4FlowNetwork):
        while node.excess > 0:
            for neighbor_node in flow_network.network.neighbors(node):
                if flow_network.network.edges[node, neighbor_node]["residual"] > 0:
                    if node.label == neighbor_node.label + 1:
                        push(node, neighbor_node)
                        is_neighbor_sink_or_source: bool = (neighbor_node == flow_network.source or neighbor_node == flow_network.sink)
                        if neighbor_node not in active_nodes and not is_neighbor_sink_or_source:
                            active_nodes.add(neighbor_node)
                        if node.excess == 0:
                            break
            else:
                relabel(node)


    do_initial_push()
    while (len(active_nodes) != 0 and flow_network.unreachable_sink_neighbors < flow_network.number_sink_neighbors and
           flow_network.realized_flow < flow_network.maximal_possible_flow):
        current_node: Node4FlowNetwork = max(active_nodes, key=lambda node: node.label)
        active_nodes.remove(current_node)
        discharge(current_node)


    maximal_flow: int = sum(flow_network.network.edges[sink_neighbor, flow_network.sink ]["flow"]
                            for sink_neighbor in flow_network.sink_neighbors)
    missing_token: int = heuristic.consumed_token - maximal_flow
    remaining_token: int = heuristic.produced_token - heuristic.consumed_token + missing_token
    result: SinglePlaceTokenResult = SinglePlaceTokenResult(heuristic.produced_token, heuristic.consumed_token,
                                                            missing_token, missing_token, remaining_token,
                                                            remaining_token, True)
    return result
