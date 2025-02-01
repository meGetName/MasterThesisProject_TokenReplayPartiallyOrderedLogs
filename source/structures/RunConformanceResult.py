from MasterThesisProject.source.structures.SinglePlaceTokenResult import SinglePlaceTokenResult


class RunConformanceResult:
    def __init__(self, produced_token: int = 0, consumed_token = 0, missing_token_min: int = 0, missing_token_max: int = 0,
                 remaining_token_min: int = 0, remaining_token_max: int = 0):
        self.produced_token = produced_token
        self.consumed_token = consumed_token
        self.missing_token_min = missing_token_min
        self.missing_token_max = missing_token_max
        self.remaining_token_min = remaining_token_min
        self.remaining_token_max = remaining_token_max

        self.conformance_level_min = 0
        self.conformance_level_max = 0

        self.number_places_decided_forward_heuristic = 0
        self.number_places_decided_backward_heuristic = 0
        self.number_places_decided_flow_network = 0
        # When we only use the heuristics we may not have the complete information for some places
        self.number_places_only_estimated = 0

    def add_single_place_result(self, result: SinglePlaceTokenResult):
        self.produced_token += result.produced_token
        self.consumed_token += result.consumed_token
        self.missing_token_max += result.missing_token_max
        self.missing_token_min += result.missing_token_min
        self.remaining_token_max += result.remaining_token_max
        self.remaining_token_min += result.remaining_token_min

    def calculate_and_set_conformance_level(self):
        def calculate_conformance_level_for_tokens(produced: int, consumed: int, missing: int, remaining: int) -> float:
            first_term: float = 1 - (missing/consumed)
            second_term: float = 1- (remaining/produced)
            return (first_term + second_term)/2

        self.conformance_level_min = calculate_conformance_level_for_tokens(
            self.produced_token, self.consumed_token, self.missing_token_max, self.remaining_token_max)
        self.conformance_level_max = calculate_conformance_level_for_tokens(
            self.produced_token, self.consumed_token, self.missing_token_min, self.remaining_token_min
        )
