from dt_manager.bots import make_greedy_bot, make_random_bot
from dt_manager.catalog import EVENTS, PLAYERS, TACTICS, make_starter_decks
from dt_manager.rules import MatchEngine
import random


def test_starter_match_runs_to_completion():
    p1, t1, e1 = make_starter_decks()
    p2, t2, e2 = make_starter_decks()
    engine = MatchEngine.create(
        team1_name="A",
        team2_name="B",
        team1_player_deck=p1,
        team1_tactic_deck=t1,
        team1_event_deck=e1,
        team2_player_deck=p2,
        team2_tactic_deck=t2,
        team2_event_deck=e2,
        bot1=make_greedy_bot(random.Random(10)),
        bot2=make_random_bot(random.Random(11)),
        seed=99,
        target_goals=3,
    )
    result = engine.run(max_turns=40)
    assert result.turns_played > 0
    assert result.final_score[0] >= 0
    assert result.final_score[1] >= 0
    assert len(result.history) == result.turns_played


def test_catalog_marks_some_cards_as_not_implemented_yet():
    assert not PLAYERS["Peppe"].implemented
    assert not EVENTS["Mirto Cup"].implemented
