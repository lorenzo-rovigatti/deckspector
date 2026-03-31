from __future__ import annotations

from dataclasses import dataclass
import itertools
import random
from typing import List, Optional

from .models import BotAdapter, EventCard, GameState, Selection, TeamState


@dataclass
class RandomBot:
    rng: random.Random

    def choose_selection(self, game: GameState, team_idx: int) -> Selection:
        team = game.teams[team_idx]
        available = team.available_players()
        if len(available) < 2:
            chosen_players = available[:]
        else:
            chosen_players = self.rng.sample(available, 2)

        candidate_tactics = []
        if team.active_tactic is not None:
            candidate_tactics.append((team.active_tactic, True))
        candidate_tactics.extend((t, False) for t in team.tactic_hand)

        chosen_tactic = None
        keep = False
        if candidate_tactics:
            chosen_tactic, keep = self.rng.choice(candidate_tactics)

        return Selection(players=chosen_players, tactic=chosen_tactic, keep_active_tactic=keep)

    def choose_event(self, game: GameState, team_idx: int) -> Optional[EventCard]:
        team = game.teams[team_idx]
        return self.rng.choice(team.event_hand) if team.event_hand else None


@dataclass
class GreedyBot:
    rng: random.Random

    def choose_selection(self, game: GameState, team_idx: int) -> Selection:
        team = game.teams[team_idx]
        role = "attack" if team_idx == game.current_attacker else "defense"
        available = team.available_players()
        combos = list(itertools.combinations(available, 2)) if len(available) >= 2 else [tuple(available)]
        if not combos:
            combos = [tuple()]

        def lineup_score(cards) -> int:
            if role == "attack":
                base = sum(card.attack for card in cards)
                base += 2 * sum(1 for card in cards if card.name in {"Sebas", "Salvatore", "Lorenzo R", "Attaccante"})
            else:
                base = sum(card.defense for card in cards)
                base += 2 * sum(1 for card in cards if card.name in {"Fabrizio", "Franz", "Massi", "Difensore"})
            return base

        chosen_players = list(max(combos, key=lineup_score))

        candidate_tactics = []
        if team.active_tactic is not None:
            candidate_tactics.append((team.active_tactic, True))
        candidate_tactics.extend((t, False) for t in team.tactic_hand)

        def tactic_score(item) -> int:
            tactic, keep = item
            if tactic is None:
                return 0
            scores = {
                "Pressing Alto": 5 if role == "attack" else 3,
                "Contropiede": 4 if role == "attack" else 0,
                "Possesso Palla": 3,
                "Cerca Uomo": 5 if role == "defense" else 1,
                "Lancio Lungo": 3 if role == "defense" else 1,
                "Catenaccio": 5 if role == "defense" else 0,
                "Polemica continua": 4,
            }
            return scores.get(tactic.name, 0) + (1 if keep else 0)

        chosen_tactic = None
        keep = False
        if candidate_tactics:
            chosen_tactic, keep = max(candidate_tactics, key=tactic_score)

        return Selection(players=chosen_players, tactic=chosen_tactic, keep_active_tactic=keep)

    def choose_event(self, game: GameState, team_idx: int) -> Optional[EventCard]:
        team = game.teams[team_idx]
        if not team.event_hand:
            return None
        priority = {
            "Distrazione difensiva": 5,
            "Bestemmia multipla": 4,
            "Pioggia intensa": 3,
            "Aperitivo pre-partita": 2,
        }
        return max(team.event_hand, key=lambda e: priority.get(e.name, 0))



def make_random_bot(rng: random.Random) -> BotAdapter:
    bot = RandomBot(rng)
    return BotAdapter(name="RandomBot", choose_selection=bot.choose_selection, choose_event=bot.choose_event)



def make_greedy_bot(rng: random.Random) -> BotAdapter:
    bot = GreedyBot(rng)
    return BotAdapter(name="GreedyBot", choose_selection=bot.choose_selection, choose_event=bot.choose_event)
