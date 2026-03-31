from dt_manager.bots import make_greedy_bot, make_random_bot
from dt_manager.catalog import make_starter_decks
from dt_manager.rules import MatchEngine
import random


p1, t1, e1 = make_starter_decks()
p2, t2, e2 = make_starter_decks()

engine = MatchEngine.create(
    team1_name="Reds",
    team2_name="Blues",
    team1_player_deck=p1,
    team1_tactic_deck=t1,
    team1_event_deck=e1,
    team2_player_deck=p2,
    team2_tactic_deck=t2,
    team2_event_deck=e2,
    bot1=make_greedy_bot(random.Random(1)),
    bot2=make_random_bot(random.Random(2)),
    seed=42,
)

result = engine.run(max_turns=30)

print("Winner:", engine.state.teams[result.winner].name)
print("Final score:", result.final_score)
print("Turns:", result.turns_played)
print("Last 5 turns:")
for turn in result.history[-5:]:
    print(
        f"Turn {turn.turn_number}: {turn.attacker} vs {turn.defender} | "
        f"A {turn.attack_value} - D {turn.defense_value} | "
        f"score {turn.score_before} -> {turn.score_after} | "
        f"event={turn.event_name}"
    )
