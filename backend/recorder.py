from threading import Lock

from backend.step import Step
from common.types import RecordedStatistic, RecordedStep


class Recorder:
    def __init__(self) -> None:
        """Recorder for tracking the state of the matchmaking queue, candidate games and created matches over time."""
        self.steps: list[Step] = []
        self.__current_step_index: int = 0
        self.__queue_size: RecordedStatistic = []
        self.__heap_size: RecordedStatistic = []
        self.__max_wait_time: RecordedStatistic = []
        self.__min_imbalance: RecordedStatistic = []
        self.__min_priority: RecordedStatistic = []
        self.__lock: Lock = Lock()

    def get_steps(self) -> list[RecordedStep]:
        """Get a list of all recorded steps as dictionaries."""
        with self.__lock:
            return [step.to_dict() for step in self.steps]

    def get_stats(self) -> dict[str, RecordedStatistic]:
        """Get statistics about the recorded steps for analysis."""
        with self.__lock:
            return {
                "queue_size": self.__queue_size.copy(),
                "heap_size": self.__heap_size.copy(),
                "max_wait_time": self.__max_wait_time.copy(),
                "min_priority": self.__min_priority.copy(),
                "min_imbalance": self.__min_imbalance.copy()
            }

    def record_step(self, **kwargs) -> None:
        """
        Asynchronously record a new step, passing keyword arguments directly to the Step constructor.
        :param kwargs: Keyword arguments passed to the Step constructor.
        """
        with self.__lock:
            step: Step = Step(**kwargs)
            self.steps.append(step)
            self.__queue_size.append(len(step.queue_snapshot.state))
            self.__heap_size.append(len(step.heap_snapshot.state))
            max_wait_time: float = max(player.pop("wait_time") for player in step.queue_snapshot.state) if step.queue_snapshot.state else None
            self.__max_wait_time.append(max_wait_time)
            heap_top = step.heap_snapshot.state[0] if step.heap_snapshot.state else {}
            self.__min_priority.append(heap_top.get("priority"))
            self.__min_imbalance.append(heap_top.get("imbalance"))
            self.__current_step_index += 1
