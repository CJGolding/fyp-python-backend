from threading import Lock

from backend.step import Step
from common.types import RecordedStatistic, RecordedStep


class Recorder:
    def __init__(self) -> None:
        """Recorder for tracking the state of the matchmaking queue, candidate games and created matches over time."""
        self.steps: list[Step] = []
        self.queue_size: RecordedStatistic = []
        self.heap_size: RecordedStatistic = []
        self.max_wait_time: RecordedStatistic = []
        self.min_priority: RecordedStatistic = []
        self.min_imbalance: RecordedStatistic = []
        self.__lock: Lock = Lock()

    def get_steps(self) -> list[RecordedStep]:
        """Get a list of all recorded steps as dictionaries."""
        with self.__lock:
            return [step.to_dict() for step in self.steps]

    def get_stats(self) -> dict[str, RecordedStatistic]:
        """Get statistics about the recorded steps for analysis."""
        with self.__lock:
            return {
                "queue_size": self.queue_size.copy(),
                "heap_size": self.heap_size.copy(),
                "max_wait_time": self.max_wait_time.copy(),
                "min_priority": self.min_priority.copy(),
                "min_imbalance": self.min_imbalance.copy()
            }

    def __clear(self) -> None:
        """Internal method to clear all recorded steps ready for the next recording session."""
        self.steps = []

    def record_step(self, **kwargs) -> None:
        """
        Asynchronously record a new step with the optional parameter to control the clearing of previous steps.
        The remaining keyword arguments are passed directly to the Step constructor.
        :param kwargs: Keyword arguments passed to the Step constructor and control flags.
        """
        with self.__lock:
            step: Step = Step(**kwargs)
            self.steps.append(step)
            self.queue_size.append(len(step.queue_snapshot.state))
            self.heap_size.append(len(step.heap_snapshot.state))
            self.max_wait_time.append(
                max([player["wait_time"] for player in step.queue_snapshot.state]) if step.queue_snapshot.state else 0)
            heap_top = step.heap_snapshot.state[0] if step.heap_snapshot.state else {}
            self.min_priority.append(heap_top.get("priority", 0))
            self.min_imbalance.append(heap_top.get("imbalance", 0))
