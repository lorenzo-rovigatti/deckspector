# DT Manager - starter simulator

This is an initial Python project skeleton for simulating and balancing **DT Manager**.

It is intentionally designed as a **custom rules engine** rather than a generic card-game framework.

## What is included

- a phase-based match engine
- card definitions as data objects
- a central effect registry
- two simple bots (`GreedyBot` and `RandomBot`)
- deck / hand / discard / reshuffle management
- player cooldown handling
- momentum (`impeto`) handling
- a small simulation harness
- smoke tests

## Important scope note

This is a **first working version**, not a complete implementation of every card and corner case.

In particular:
- the core turn loop is implemented
- many player / tactic / event effects are implemented
- several more complex cards are included in the catalog as **not yet implemented** so they are visible in the codebase
- the default demo decks only use implemented cards, so simulations run out of the box

## Project structure

```text
.
├── README.md
├── pyproject.toml
├── dt_manager/
│   ├── __init__.py
│   ├── bots.py
│   ├── catalog.py
│   ├── effects.py
│   ├── models.py
│   ├── rules.py
│   └── simulate.py
├── examples/
│   └── run_quickstart.py
└── tests/
    └── test_smoke.py
```

## Quick start

```bash
cd dt_manager_starter
python -m dt_manager.simulate
python examples/run_quickstart.py
```

## Recommended next steps

1. complete the remaining unimplemented card effects
2. add deterministic rules tests for each card
3. improve the bot heuristics (mulligan / lineup / event timing)
4. add CSV or pandas export for balance analysis
5. build matchup suites for deck-vs-deck balancing
