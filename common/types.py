"""Common type definitions used across the project."""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from backend.player import Player as _Player
    from backend.candidate_game import CandidateGame as _CandidateGame
    from backend.step import Step as _Step
    from backend.snapshots import (
        BaseSnapshot as _BaseSnapshot,
        HeapSnapshot as _HeapSnapshot,
        QueueSnapshot as _QueueSnapshot
    )
    from backend.min_heap import MinHeap as _MinHeap
    from backend.sorted_set import SortedSet as _SortedSet
    from backend.unrestricted_game_manager import UnrestrictedGameManager as _UnrestrictedGameManager
    from backend.time_sensitive_game_manager import TimeSensitiveGameManager as _TimeSensitiveGameManager

# Primitive types
type Number = int | float

# Class type aliases
type Player = _Player
type CandidateGame = _CandidateGame
type CreatedMatch = _CandidateGame
type MinHeap = _MinHeap
type SortedSet = _SortedSet
type GameManager = _UnrestrictedGameManager | _TimeSensitiveGameManager
type Step = _Step
type HeapSnapshot = _HeapSnapshot
type QueueSnapshot = _QueueSnapshot
type CreatedMatchesSnapshot = _BaseSnapshot

# Recorder types
type RecordedWindow = list[int]
type RecordedPlayerIndex = int
type RecordedOrder = list[int]
type RecordedPlayer = dict[str, Number]
type RecordedTeam = list[int]
type RecordedGame = int
type RecordedState = list[dict[str, Number]]
type RecordedSnapshot = dict[
    str, RecordedState | RecordedWindow | RecordedPlayerIndex | RecordedTeam | RecordedGame | str]
type RecordedStep = dict[str, RecordedSnapshot]
type RecordedStatistic = list[Optional[Number]]
type RecordedParameters = dict[str, str | Number]

# Backend logic types
type GameTeam = set[Player]
type GamePlayers = set[Player]
type AffectedPlayers = set[Player]
type LambdaFunction = Callable[[Number], bool]
type BestCandidateResult = tuple[CandidateGame, float, int]
type PartitionFunction = Callable[[Player, GamePlayers], BestCandidateResult]
type AsynchronousFunction = Callable
