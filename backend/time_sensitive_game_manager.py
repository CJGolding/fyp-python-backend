import logging

from backend.candidate_game import CandidateGame
from backend.player import Player
from backend.unrestricted_game_manager import UnrestrictedGameManager
from common.types import RecordedParameters, GameTeam

LOG: logging.Logger = logging.getLogger(__name__)


class TimeSensitiveGameManager(UnrestrictedGameManager):
    def __init__(self, team_size: int = 2, p_norm: float = 1.0, q_norm: float = 1.0, fairness_weight: float = 0.1,
                 queue_weight: float = 0.1, is_recording: bool = False, approximate=False) -> None:
        """
        Time-Sensitive Game Manager that extends UnrestrictedGameManager by incorporating queue time into matchmaking.
        :param team_size: Number of players per team.
        :param p_norm: The p-norm used for fairness calculation.
        :param q_norm: The q-norm used for uniformity calculation.
        :param fairness_weight: Weighting factor for fairness in imbalance calculation.
        :param queue_weight: Weighting factor for queue time in priority calculation.
        :param is_recording: Flag to enable or disable recording of matchmaking steps.
        :param approximate: Flag to enable or disable greedy approximation in matchmaking.
        """
        self.queue_weight: float = self.validate_config(queue_weight, lambda x: x > 0, "queue_weight", "greater than 0")
        super().__init__(team_size, p_norm, q_norm, fairness_weight, is_recording, approximate)
        self._match_quality_metric: str = "priority"

    def __repr__(self) -> str:
        return f"Team Size: {self.team_size}, P: {self.p_norm}, Q: {self.q_norm}, α: {self.fairness_weight}, β: {self.queue_weight}, Window: {self.skill_window}"

    def get_parameters(self) -> RecordedParameters:
        """Get the configuration parameters of the UnrestrictedGameManager for frontend state management."""
        return {
            "team_size": self.team_size,
            "p_norm": self.p_norm,
            "q_norm": self.q_norm,
            "fairness_weight": self.fairness_weight,
            "queue_weight": self.queue_weight,
            "skill_window": self.skill_window
        }

    def _create_candidate_game(self, player: Player, team_x: GameTeam, team_y: GameTeam) -> CandidateGame:
        return CandidateGame(player, team_x, team_y, self.p_norm, self.q_norm, self.fairness_weight, self.queue_weight)
