from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .models import EventCard, PlayerCard, PlayerType, TacticCard


PLAYERS: Dict[str, PlayerCard] = {
    "Attaccante": PlayerCard("Attaccante", 3, 0, PlayerType.ATTACKER, positive_effect="attaccante_combo", tags=("attacker",)),
    "Difensore": PlayerCard("Difensore", 0, 3, PlayerType.DEFENDER, positive_effect="difensore_combo", tags=("defender",)),
    "Regista": PlayerCard("Regista", 2, 1, PlayerType.MIDFIELDER, positive_effect="regista_draw_tactic", tags=("playmaker",)),
    "Mediano": PlayerCard("Mediano", 1, 2, PlayerType.MIDFIELDER, positive_effect="mediano_support", tags=("midfielder",)),
    "Portiere": PlayerCard("Portiere", 0, 3, PlayerType.GOALKEEPER, positive_effect="portiere_save", tags=("goalkeeper",)),
    "Il Presidente": PlayerCard("Il Presidente", 1, 3, PlayerType.DEFENDER, positive_effect="presidente_shot", negative_effect="presidente_finanza_creativa", implemented=False),
    "Franz": PlayerCard("Franz", 0, 4, PlayerType.GOALKEEPER, positive_effect="franz_motivatore", negative_effect="franz_urlatore"),
    "Lorenzo R": PlayerCard("Lorenzo R", 2, 2, PlayerType.MIDFIELDER, positive_effect="lorenzo_assist", negative_effect="lorenzo_cocciuto"),
    "Fabrizio": PlayerCard("Fabrizio", 0, 4, PlayerType.GOALKEEPER, positive_effect="fabrizio_miracolo", negative_effect="fabrizio_pressing_penalty"),
    "Sandrino": PlayerCard("Sandrino", 3, 1, PlayerType.ATTACKER, positive_effect="sandrino_ignore_event", negative_effect="sandrino_vs_defense_bonus"),
    "Salvatore": PlayerCard("Salvatore", 1, 3, PlayerType.DEFENDER, positive_effect="salvatore_colpo_genio", negative_effect="salvatore_colpo_genio"),
    "Peppe": PlayerCard("Peppe", 2, 2, PlayerType.MIDFIELDER, positive_effect="peppe_double_tactic", negative_effect="peppe_cacacazzi", implemented=False),
    "Bodo": PlayerCard("Bodo", 0, 4, PlayerType.DEFENDER, positive_effect="bodo_minaccioso", negative_effect="bodo_weather", implemented=False),
    "Jori": PlayerCard("Jori", 1, 3, PlayerType.DEFENDER, positive_effect="jori_extra_player", negative_effect="jori_generoso", implemented=False),
    "Ernesto": PlayerCard("Ernesto", 2, 2, PlayerType.MIDFIELDER, positive_effect="ernesto_event_anytime", negative_effect="ernesto_vetrallese"),
    "Sebas": PlayerCard("Sebas", 4, 0, PlayerType.ATTACKER, positive_effect="sebas_goal_spectacular", negative_effect="sebas_ahead_penalty"),
    "Massi": PlayerCard("Massi", 1, 3, PlayerType.DEFENDER, positive_effect="massi_marking", negative_effect="massi_event_penalty"),
    "Claudio M": PlayerCard("Claudio M", 2, 2, PlayerType.MIDFIELDER, positive_effect="claudio_persist", negative_effect="claudio_second_turn_tax", implemented=False),
    "Dave": PlayerCard("Dave", 2, 2, PlayerType.MIDFIELDER, positive_effect="dave_wins_ties", negative_effect="dave_wear"),
}

TACTICS: Dict[str, TacticCard] = {
    "Pressing Alto": TacticCard("Pressing Alto", effect="pressing_alto"),
    "Contropiede": TacticCard("Contropiede", effect="contropiede"),
    "Possesso Palla": TacticCard("Possesso Palla", effect="possesso_palla"),
    "Cerca Uomo": TacticCard("Cerca Uomo", effect="cerca_uomo"),
    "Lancio Lungo": TacticCard("Lancio Lungo", effect="lancio_lungo"),
    "Catenaccio": TacticCard("Catenaccio", effect="catenaccio"),
    "Polemica continua": TacticCard("Polemica continua", effect="polemica_continua"),
}

EVENTS: Dict[str, EventCard] = {
    "Pioggia intensa": EventCard("Pioggia intensa", effect="pioggia_intensa", meteorological=True),
    "Errore arbitrale": EventCard("Errore arbitrale", effect="errore_arbitrale", implemented=False),
    "Distrazione difensiva": EventCard("Distrazione difensiva", effect="distrazione_difensiva"),
    "Bestemmia multipla": EventCard("Bestemmia multipla", effect="bestemmia_multipla"),
    "Partita a 8": EventCard("Partita a 8", effect="partita_a_8", implemented=False),
    "Partita a 5": EventCard("Partita a 5", effect="partita_a_5", implemented=False),
    "Aperitivo pre-partita": EventCard("Aperitivo pre-partita", effect="aperitivo_pre_partita"),
    "Mirto Cup": EventCard("Mirto Cup", effect="mirto_cup", implemented=False),
}


IMPLEMENTED_STARTER_PLAYER_DECK = [
    "Attaccante",
    "Attaccante",
    "Difensore",
    "Difensore",
    "Portiere",
    "Regista",
    "Mediano",
    "Franz",
    "Lorenzo R",
    "Fabrizio",
    "Sandrino",
    "Salvatore",
    "Ernesto",
    "Sebas",
    "Massi",
    "Dave",
]

IMPLEMENTED_STARTER_TACTIC_DECK = [
    "Pressing Alto",
    "Contropiede",
    "Possesso Palla",
    "Cerca Uomo",
    "Lancio Lungo",
    "Catenaccio",
    "Polemica continua",
]

IMPLEMENTED_STARTER_EVENT_DECK = [
    "Pioggia intensa",
    "Distrazione difensiva",
    "Bestemmia multipla",
    "Aperitivo pre-partita",
]


def build_player_deck(names: List[str]) -> List[PlayerCard]:
    return [PLAYERS[name] for name in names]


def build_tactic_deck(names: List[str]) -> List[TacticCard]:
    return [TACTICS[name] for name in names]


def build_event_deck(names: List[str]) -> List[EventCard]:
    return [EVENTS[name] for name in names]


def make_starter_decks() -> tuple[List[PlayerCard], List[TacticCard], List[EventCard]]:
    return (
        build_player_deck(IMPLEMENTED_STARTER_PLAYER_DECK),
        build_tactic_deck(IMPLEMENTED_STARTER_TACTIC_DECK),
        build_event_deck(IMPLEMENTED_STARTER_EVENT_DECK),
    )
