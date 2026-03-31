from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from .bots import make_greedy_bot, make_random_bot
from .catalog import make_starter_decks
from .rules import MatchEngine


@dataclass
class SimulationSummary:
    games: int
    team1_wins: int
    team2_wins: int
    avg_turns: float
    avg_score_team1: float
    avg_score_team2: float



def run_series(n_games: int = 100, seed: int = 1234) -> SimulationSummary:
    team1_wins = 0
    team2_wins = 0
    turns = []
    scores1 = []
    scores2 = []

    for game_idx in range(n_games):
        p1, t1, e1 = make_starter_decks()
        p2, t2, e2 = make_starter_decks()
        engine = MatchEngine.create(
            team1_name="Team A",
            team2_name="Team B",
            team1_player_deck=p1,
            team1_tactic_deck=t1,
            team1_event_deck=e1,
            team2_player_deck=p2,
            team2_tactic_deck=t2,
            team2_event_deck=e2,
            bot1=make_greedy_bot(__import__("random").Random(seed + game_idx)),
            bot2=make_random_bot(__import__("random").Random(seed + 10000 + game_idx)),
            seed=seed + game_idx,
        )
        result = engine.run(max_turns=40)
        if result.winner == 0:
            team1_wins += 1
        else:
            team2_wins += 1
        turns.append(result.turns_played)
        scores1.append(result.final_score[0])
        scores2.append(result.final_score[1])

    return SimulationSummary(
        games=n_games,
        team1_wins=team1_wins,
        team2_wins=team2_wins,
        avg_turns=mean(turns) if turns else 0.0,
        avg_score_team1=mean(scores1) if scores1 else 0.0,
        avg_score_team2=mean(scores2) if scores2 else 0.0,
    )


if __name__ == "__main__":
    summary = run_series(n_games=50)
    print("DT Manager starter simulation")
    print(f"Games: {summary.games}")
    print(f"Team A wins: {summary.team1_wins}")
    print(f"Team B wins: {summary.team2_wins}")
    print(f"Average turns: {summary.avg_turns:.2f}")
    print(f"Average score Team A: {summary.avg_score_team1:.2f}")
    print(f"Average score Team B: {summary.avg_score_team2:.2f}")
