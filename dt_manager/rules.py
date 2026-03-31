from __future__ import annotations

from dataclasses import dataclass
import random
from typing import List, Optional

from .effects import apply_event_effect, apply_player_effects, apply_tactic_effect, reduce_goal_roll_with_fabrizio
from .models import BotAdapter, EventCard, GameState, MatchResult, Selection, TeamState, TurnContext, TurnRecord


@dataclass
class MatchEngine:
    state: GameState
    bots: List[BotAdapter]

    @classmethod
    def create(
        cls,
        team1_name: str,
        team2_name: str,
        team1_player_deck,
        team1_tactic_deck,
        team1_event_deck,
        team2_player_deck,
        team2_tactic_deck,
        team2_event_deck,
        bot1: BotAdapter,
        bot2: BotAdapter,
        seed: int | None = None,
        target_goals: int = 5,
    ) -> "MatchEngine":
        rng = random.Random(seed)
        cls._validate_implemented(team1_player_deck, team1_tactic_deck, team1_event_deck)
        cls._validate_implemented(team2_player_deck, team2_tactic_deck, team2_event_deck)
        team1 = TeamState(team1_name, list(team1_player_deck), list(team1_tactic_deck), list(team1_event_deck))
        team2 = TeamState(team2_name, list(team2_player_deck), list(team2_tactic_deck), list(team2_event_deck))
        rng.shuffle(team1.player_draw)
        rng.shuffle(team1.tactic_draw)
        rng.shuffle(team1.event_draw)
        rng.shuffle(team2.player_draw)
        rng.shuffle(team2.tactic_draw)
        rng.shuffle(team2.event_draw)
        team1.draw_cards(rng, players=5, tactics=3, events=1)
        team2.draw_cards(rng, players=5, tactics=3, events=1)
        state = GameState(teams=[team1, team2], rng=rng, target_goals=target_goals, current_attacker=0)
        return cls(state=state, bots=[bot1, bot2])

    @staticmethod
    def _validate_implemented(player_deck, tactic_deck, event_deck) -> None:
        not_implemented = [card.name for card in list(player_deck) + list(tactic_deck) + list(event_deck) if not card.implemented]
        if not_implemented:
            raise ValueError(f"Deck contains cards marked as not implemented yet: {', '.join(not_implemented)}")

    def run(self, max_turns: int = 50) -> MatchResult:
        while self.state.turn_number < max_turns:
            winner = self._check_victory()
            if winner is not None:
                return MatchResult(winner=winner, final_score=self._score_tuple(), turns_played=self.state.turn_number, history=self.state.history)
            self.play_turn()
        winner = 0 if self.state.teams[0].score >= self.state.teams[1].score else 1
        return MatchResult(winner=winner, final_score=self._score_tuple(), turns_played=self.state.turn_number, history=self.state.history)

    def play_turn(self) -> None:
        self.state.turn_number += 1
        attacker = self.state.current_attacker
        defender = 1 - attacker
        attack_team = self.state.teams[attacker]
        defense_team = self.state.teams[defender]

        for team in self.state.teams:
            team.reduce_cooldowns()

        attack_team.draw_cards(self.state.rng, players=1, tactics=1)
        defense_team.draw_cards(self.state.rng, players=1, tactics=1, events=1)

        attack_selection = self.bots[attacker].choose_selection(self.state, attacker)
        defense_selection = self.bots[defender].choose_selection(self.state, defender)

        event_card = self._choose_event(attacker, defender, attack_selection, defense_selection)

        score_before = self._score_tuple()
        momentum_before = self._momentum_tuple()

        ctx = TurnContext(
            turn_number=self.state.turn_number,
            attack_team_idx=attacker,
            defense_team_idx=defender,
            attack_selection=attack_selection,
            defense_selection=defense_selection,
            event_card=event_card,
            attack_value=sum(card.attack for card in attack_selection.players),
            defense_value=sum(card.defense for card in defense_selection.players),
        )

        apply_player_effects(self.state, ctx)
        self._preapply_nullify_tactics(ctx)
        apply_tactic_effect(self.state, ctx, "attack")
        apply_tactic_effect(self.state, ctx, "defense")
        apply_event_effect(self.state, ctx)

        self._resolve_action(ctx)
        self._resolve_momentum_bonus(attacker)
        self._resolve_momentum_bonus(defender)
        self._cleanup_turn(attacker, defender, attack_selection, defense_selection, event_card)

        record = TurnRecord(
            turn_number=self.state.turn_number,
            attacker=attack_team.name,
            defender=defense_team.name,
            attack_value=ctx.attack_value,
            defense_value=ctx.defense_value,
            score_before=score_before,
            score_after=self._score_tuple(),
            momentum_before=momentum_before,
            momentum_after=self._momentum_tuple(),
            event_name=event_card.name if event_card else None,
            note_summary=" | ".join(ctx.notes),
        )
        self.state.history.append(record)
        self.state.current_attacker = defender

    def _choose_event(self, attacker: int, defender: int, attack_selection: Selection, defense_selection: Selection) -> Optional[EventCard]:
        scores = self._score_tuple()
        team_behind = None
        if scores[0] < scores[1]:
            team_behind = 0
        elif scores[1] < scores[0]:
            team_behind = 1

        candidate_team = team_behind
        if candidate_team is None:
            if any(card.name == "Ernesto" for card in attack_selection.players):
                candidate_team = attacker
            elif any(card.name == "Ernesto" for card in defense_selection.players):
                candidate_team = defender

        if candidate_team is None:
            return None
        team = self.state.teams[candidate_team]
        if not team.event_hand:
            return None
        return self.bots[candidate_team].choose_event(self.state, candidate_team)

    def _preapply_nullify_tactics(self, ctx: TurnContext) -> None:
        if ctx.attack_selection.tactic and ctx.attack_selection.tactic.name == "Polemica continua":
            ctx.nullify_defense_tactic = True
            ctx.notes.append("attack: Polemica continua annulla la tattica difensiva")
        if ctx.defense_selection.tactic and ctx.defense_selection.tactic.name == "Polemica continua":
            ctx.nullify_attack_tactic = True
            ctx.notes.append("defense: Polemica continua annulla la tattica offensiva")

    def _resolve_action(self, ctx: TurnContext) -> None:
        attacker_team = self.state.teams[ctx.attack_team_idx]
        defender_team = self.state.teams[ctx.defense_team_idx]

        attack_wins = False
        if ctx.attack_value > ctx.defense_value:
            attack_wins = True
        elif ctx.attack_value == ctx.defense_value:
            attack_wins = ctx.attack_wins_ties and not ctx.defense_wins_ties

        if attack_wins:
            self._attempt_goal("attack", ctx)
        else:
            defender_team.momentum += 1 + ctx.defense_extra_momentum_on_stop
            ctx.notes.append(f"difesa riuscita: {defender_team.name} guadagna impeto")
            if ctx.defense_defense_stop_counterroll:
                roll = self.state.rng.randint(1, 6)
                ctx.notes.append(f"Lancio Lungo in difesa: dado {roll}")
                if roll == 6:
                    self._attempt_goal("defense", ctx)

    def _attempt_goal(self, shooting_side: str, ctx: TurnContext) -> None:
        roll = self.state.rng.randint(1, 6)
        roll = reduce_goal_roll_with_fabrizio(ctx, shooting_side, roll)
        attacker_team = self.state.teams[ctx.attack_team_idx]
        defender_team = self.state.teams[ctx.defense_team_idx]
        scoring_team = attacker_team if shooting_side == "attack" else defender_team

        ctx.notes.append(f"{shooting_side}: tiro con dado {roll}")

        requires_exact_six = ctx.attack_requires_exact_six if shooting_side == "attack" else False
        auto_spectacular = ctx.attack_goal_is_automatic_spectacular if shooting_side == "attack" else ctx.defense_goal_is_automatic_spectacular

        goal = False
        spectacular = False
        if requires_exact_six:
            goal = roll == 6
            spectacular = goal
        else:
            if roll >= 3:
                goal = True
            spectacular = roll == 6 or (goal and auto_spectacular)

        if goal:
            scoring_team.score += 1
            ctx.notes.append(f"{shooting_side}: GOL di {scoring_team.name}")
            if spectacular:
                scoring_team.momentum += 1
                ctx.notes.append(f"{shooting_side}: gol spettacolare, +1 impeto")
        else:
            ctx.notes.append(f"{shooting_side}: occasione fallita")

    def _resolve_momentum_bonus(self, team_idx: int) -> None:
        team = self.state.teams[team_idx]
        if team.momentum >= 3:
            roll = self.state.rng.randint(1, 6)
            if roll >= 4:
                team.score += 1
            team.momentum = 0

    def _cleanup_turn(
        self,
        attacker: int,
        defender: int,
        attack_selection: Selection,
        defense_selection: Selection,
        event_card: Optional[EventCard],
    ) -> None:
        self._cleanup_team(attacker, attack_selection, played_event=event_card if event_card in self.state.teams[attacker].event_hand else None)
        self._cleanup_team(defender, defense_selection, played_event=event_card if event_card in self.state.teams[defender].event_hand else None)

    def _cleanup_team(self, team_idx: int, selection: Selection, played_event: Optional[EventCard]) -> None:
        team = self.state.teams[team_idx]

        for card in selection.players:
            if card in team.player_hand:
                team.player_hand.remove(card)
                team.player_discard.append(card)
                team.cooldowns[card.name] = 2
                team.play_counts[card.name] = team.play_counts.get(card.name, 0) + 1

        selected_tactic = selection.tactic
        if selection.keep_active_tactic:
            pass
        elif selected_tactic is not None:
            if team.active_tactic is not None:
                team.tactic_discard.append(team.active_tactic)
            if selected_tactic in team.tactic_hand:
                team.tactic_hand.remove(selected_tactic)
            team.active_tactic = selected_tactic

        if played_event is not None and played_event in team.event_hand:
            team.event_hand.remove(played_event)
            team.event_discard.append(played_event)

    def _check_victory(self) -> Optional[int]:
        for idx, team in enumerate(self.state.teams):
            if team.score >= self.state.target_goals:
                return idx
        return None

    def _score_tuple(self) -> tuple[int, int]:
        return (self.state.teams[0].score, self.state.teams[1].score)

    def _momentum_tuple(self) -> tuple[int, int]:
        return (self.state.teams[0].momentum, self.state.teams[1].momentum)
