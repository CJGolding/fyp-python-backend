class MockPlayer:
    def __init__(self, player_id: int, skill: int = 1000, enqueue_time: float = 0.0):
        self.id = player_id
        self.skill = skill
        self.enqueue_time = enqueue_time
        self.dequeue_time = None
        self.wait_time = 0.0

    def __repr__(self):
        return f"Player({self.id}, skill={self.skill})"

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __lt__(self, other):
        return (self.skill, self.id) < (other.skill, other.id)

    def __gt__(self, other):
        return (self.skill, self.id) > (other.skill, other.id)

    def mark_as_exited(self):
        self.dequeue_time = 0.0
