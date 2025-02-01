from MasterThesisProject.source.structures.Run import Run


class PartiallyOrderedEventLog:
    def __init__(self, run_to_frequency: dict[Run]):
        self.run_to_frequency = run_to_frequency
