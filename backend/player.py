from dataclasses import dataclass, field
from typing import Optional

from backend._clock import now
from common.types import Number


@dataclass
class Player:
    """
    Represents a player in the matchmaking queue. Data class for easy storage and access to player attributes.
    :param id: Unique identifier for the player.
    :param skill: Skill level of the player.
    :param enqueue_time: Timestamp when the player entered the queue.
    :param dequeue_time: Timestamp when the player exited the queue (None if still in queue
    """
    id: int
    skill: int
    enqueue_time: float = field(default_factory=now)
    dequeue_time: Optional[float] = None

    def to_dict(self) -> dict[str, Number]:
        """Convert the Player instance to a dictionary for recording."""
        return {
            "id": self.id,
            "skill": self.skill,
            "enqueue_time": self.enqueue_time,
            "wait_time": self.wait_time
        }

    @property
    def wait_time(self) -> float:
        """
        Calculate the wait time of the player in the queue. If the player has not exited the queue,
        the wait time is calculated up to the current time.
        :return: The wait time in seconds.
        """
        if self.dequeue_time is None:
            return now() - self.enqueue_time
        return self.dequeue_time - self.enqueue_time

    def mark_as_exited(self) -> None:
        """Mark the player as having exited the queue by setting the dequeue time to the current time."""
        self.dequeue_time = now()

    def __lt__(self, other: "Player") -> bool:
        """Less-than comparison based on skill level, then by ID for consistent tie-breaking."""
        return (self.skill, self.id) < (other.skill, other.id)

    def __hash__(self) -> int:
        """Hash based on player ID for use in sets and dictionaries."""
        return hash(self.id)

    def __eq__(self, other: "Player") -> bool:
        """Equality comparison based on player ID."""
        return self.id == other.id
