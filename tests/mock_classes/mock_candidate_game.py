from tests.mock_classes.mock_player import MockPlayer


class MockCandidateGame:
    def __init__(self, anchor_player: MockPlayer, team_x=None, team_y=None, priority: float = None,
                 imbalance: float = 5.0):
        self.anchor_player = anchor_player
        self.team_x = team_x if team_x is not None else frozenset()
        self.team_y = team_y if team_y is not None else frozenset()
        self.priority = priority
        self.imbalance = imbalance

    def __lt__(self, other):
        if self.priority is not None and other.priority is not None:
            return self.priority < other.priority
        return self.imbalance < other.imbalance

    def __le__(self, other):
        if self.priority is not None and other.priority is not None:
            return self.priority <= other.priority
        return self.imbalance <= other.imbalance

    def __gt__(self, other):
        if self.priority is not None and other.priority is not None:
            return self.priority > other.priority
        return self.imbalance > other.imbalance

    def __ge__(self, other):
        if self.priority is not None and other.priority is not None:
            return self.priority >= other.priority
        return self.imbalance >= other.imbalance

    def __eq__(self, other):
        if self.priority is not None and other.priority is not None:
            return self.priority == other.priority
        return self.imbalance == other.imbalance

    def __ne__(self, other):
        if self.priority is not None and other.priority is not None:
            return self.priority != other.priority
        return self.imbalance != other.imbalance

    def __repr__(self):
        return f"CandidateGame(anchor={self.anchor_player.id}, imbalance={self.imbalance})"
