from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional
import random


class CardType(str, Enum):
    PLAYER = "player"
    TACTIC = "tactic"
    EVENT = "event"


class PlayerType(str, Enum):
    ATTACKER = "A"  # Attaccante
    DEFENDER = "D"  # Difensore
    MIDFIELDER = "C"  # Centrocampista
    GOALKEEPER = "P"  # Portiere


@dataclass(frozen=True)
class PlayerCard:
    name: str
    attack: int
    defense: int
    type: PlayerType
    positive_effect: Optional[str] = None
    negative_effect: Optional[str] = None
    tags: tuple[str, ...] = ()
    implemented: bool = True


@dataclass(frozen=True)
class TacticCard:
    name: str
    effect: Optional[str] = None
    implemented: bool = True


@dataclass(frozen=True)
class EventCard:
    name: str
    effect: Optional[str] = None
    implemented: bool = True
    meteorological: bool = False


@dataclass
class TeamState:
    name: str
    player_draw: List[PlayerCard]
    tactic_draw: List[TacticCard]
    event_draw: List[EventCard]
    player_hand: List[PlayerCard] = field(default_factory=list)
    tactic_hand: List[TacticCard] = field(default_factory=list)
    event_hand: List[EventCard] = field(default_factory=list)
    player_discard: List[PlayerCard] = field(default_factory=list)
    tactic_discard: List[TacticCard] = field(default_factory=list)
    event_discard: List[EventCard] = field(default_factory=list)
    active_tactic: Optional[TacticCard] = None
    score: int = 0
    momentum: int = 0
    cooldowns: Dict[str, int] = field(default_factory=dict)
    play_counts: Dict[str, int] = field(default_factory=dict)

    def reduce_cooldowns(self) -> None:
        expired = []
        for name in list(self.cooldowns):
            self.cooldowns[name] -= 1
            if self.cooldowns[name] <= 0:
                expired.append(name)
        for name in expired:
            del self.cooldowns[name]

    def available_players(self) -> List[PlayerCard]:
        return [card for card in self.player_hand if card.name not in self.cooldowns]

    def reshuffle_if_needed(self, rng: random.Random) -> None:
        if not self.player_draw and self.player_discard:
            self.player_draw = self.player_discard[:]
            self.player_discard.clear()
            rng.shuffle(self.player_draw)
        if not self.tactic_draw and self.tactic_discard:
            self.tactic_draw = self.tactic_discard[:]
            self.tactic_discard.clear()
            rng.shuffle(self.tactic_draw)
        if not self.event_draw and self.event_discard:
            self.event_draw = self.event_discard[:]
            self.event_discard.clear()
            rng.shuffle(self.event_draw)

    def draw_cards(self, rng: random.Random, players: int = 0, tactics: int = 0, events: int = 0) -> None:
        self.reshuffle_if_needed(rng)
        for _ in range(players):
            if self.player_draw:
                self.player_hand.append(self.player_draw.pop())
            else:
                break
        for _ in range(tactics):
            if self.tactic_draw:
                self.tactic_hand.append(self.tactic_draw.pop())
            else:
                break
        for _ in range(events):
            if self.event_draw:
                self.event_hand.append(self.event_draw.pop())
            else:
                break


@dataclass
class Selection:
    players: List[PlayerCard]
    tactic: Optional[TacticCard]
    keep_active_tactic: bool = False


@dataclass
class TurnContext:
    turn_number: int
    attack_team_idx: int
    defense_team_idx: int
    attack_selection: Selection
    defense_selection: Selection
    event_card: Optional[EventCard]
    attack_value: int = 0
    defense_value: int = 0
    attack_goal_roll_modifier: int = 0
    defense_goal_roll_modifier: int = 0
    attack_requires_exact_six: bool = False
    attack_goal_is_automatic_spectacular: bool = False
    defense_goal_is_automatic_spectacular: bool = False
    defense_wins_ties: bool = True
    attack_wins_ties: bool = False
    attack_ignore_event: bool = False
    defense_ignore_event: bool = False
    attack_extra_momentum_on_stop: int = 0
    defense_extra_momentum_on_stop: int = 0
    attack_defense_stop_counterroll: bool = False
    defense_defense_stop_counterroll: bool = False
    nullify_attack_tactic: bool = False
    nullify_defense_tactic: bool = False
    meteorological_event: bool = False
    notes: List[str] = field(default_factory=list)


@dataclass
class TurnRecord:
    turn_number: int
    attacker: str
    defender: str
    attack_value: int
    defense_value: int
    score_before: tuple[int, int]
    score_after: tuple[int, int]
    momentum_before: tuple[int, int]
    momentum_after: tuple[int, int]
    event_name: Optional[str]
    note_summary: str


@dataclass
class MatchResult:
    winner: int
    final_score: tuple[int, int]
    turns_played: int
    history: List[TurnRecord]


BotFunc = Callable[["GameState", int], Selection]
EventChoiceFunc = Callable[["GameState", int], Optional[EventCard]]


@dataclass
class BotAdapter:
    name: str
    choose_selection: BotFunc
    choose_event: EventChoiceFunc


@dataclass
class GameState:
    teams: List[TeamState]
    rng: random.Random
    target_goals: int = 5
    current_attacker: int = 0
    turn_number: int = 0
    history: List[TurnRecord] = field(default_factory=list)
