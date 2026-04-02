from __future__ import annotations

from typing import List

from .models import GameState, PlayerCard, TeamState, TurnContext


def lineup_for_side(ctx: TurnContext, side: str) -> List[PlayerCard]:
    return ctx.attack_selection.players if side == "attack" else ctx.defense_selection.players


def opposing_lineup(ctx: TurnContext, side: str) -> List[PlayerCard]:
    return ctx.defense_selection.players if side == "attack" else ctx.attack_selection.players


def team_for_side(game: GameState, ctx: TurnContext, side: str) -> TeamState:
    idx = ctx.attack_team_idx if side == "attack" else ctx.defense_team_idx
    return game.teams[idx]


def attack_mod(ctx: TurnContext, side: str, amount: int, reason: str) -> None:
    if side == "attack":
        ctx.attack_value += amount
        ctx.notes.append(reason)


def defense_mod(ctx: TurnContext, side: str, amount: int, reason: str) -> None:
    if side == "defense":
        ctx.defense_value += amount
        ctx.notes.append(reason)


def _set_auto_spectacular(ctx: TurnContext, side: str, value: bool) -> None:
    if side == "attack":
        ctx.attack_goal_is_automatic_spectacular = value
    else:
        ctx.defense_goal_is_automatic_spectacular = value
    ctx.notes.append(f"{side}: gol automatico spettacolare se segna")


# Player effects

def _apply_attaccante_combo(game: GameState, ctx: TurnContext, side: str) -> None:
    lineup = lineup_for_side(ctx, side)
    if sum(card.name == "Attaccante" for card in lineup) >= 2:
        attack_mod(ctx, side, 1, f"{side}: Attaccante combo +1")



def _apply_difensore_combo(game: GameState, ctx: TurnContext, side: str) -> None:
    lineup = lineup_for_side(ctx, side)
    if sum(card.name == "Difensore" for card in lineup) >= 2:
        defense_mod(ctx, side, 1, f"{side}: Difensore combo +1")



def _apply_regista_draw_tactic(game: GameState, ctx: TurnContext, side: str) -> None:
    team = team_for_side(game, ctx, side)
    team.draw_cards(game.rng, tactics=1)
    ctx.notes.append(f"{side}: Regista pesca 1 Tattica")


def _apply_portiere_save(game: GameState, ctx: TurnContext, side: str) -> None:
    if side != "defense":
        return
    ctx.defense_goal_roll_modifier -= 1
    ctx.notes.append(f"{side}: Portiere pronto a ridurre di 1 il dado per parare il gol")


def _apply_mediano_support(game: GameState, ctx: TurnContext, side: str) -> None:
    lineup = lineup_for_side(ctx, side)
    zero_def_teammates = [card for card in lineup if card.name != "Mediano" and card.defense == 0]
    if zero_def_teammates:
        defense_mod(ctx, side, len(zero_def_teammates), f"{side}: Mediano protegge compagno/i a 0 difesa")



def _apply_franz_motivatore(game: GameState, ctx: TurnContext, side: str) -> None:
    team = team_for_side(game, ctx, side)
    other = game.teams[ctx.defense_team_idx if side == "attack" else ctx.attack_team_idx]
    if team.score < other.score:
        swing = 0
        for card in lineup_for_side(ctx, side):
            if card.name == "Franz":
                continue
            if side == "attack":
                swing += card.defense - card.attack
            else:
                swing += card.attack - card.defense
        if side == "attack":
            attack_mod(ctx, side, swing, f"{side}: Franz scambia attacco/difesa dei compagni")
        else:
            defense_mod(ctx, side, swing, f"{side}: Franz scambia attacco/difesa dei compagni")



def _apply_franz_urlatore(game: GameState, ctx: TurnContext, side: str) -> None:
    lineup = lineup_for_side(ctx, side)
    if any(card.name == "Regista" for card in lineup):
        defense_mod(ctx, side, -2, f"{side}: Franz con Regista -2 difesa")



def _apply_lorenzo_assist(game: GameState, ctx: TurnContext, side: str) -> None:
    lineup = lineup_for_side(ctx, side)
    bonus = sum(1 for card in lineup if card.name != "Lorenzo R" and card.attack > card.defense)
    if bonus:
        attack_mod(ctx, side, 2 * bonus, f"{side}: Lorenzo R assist +{2 * bonus}")



def _apply_lorenzo_cocciuto(game: GameState, ctx: TurnContext, side: str) -> None:
    other = opposing_lineup(ctx, side)
    if other and all(card.defense > 2 for card in other):
        attack_mod(ctx, side, -2, f"{side}: Lorenzo R cocciuto -2")



def _apply_fabrizio_pressing_penalty(game: GameState, ctx: TurnContext, side: str) -> None:
    other_tactic = ctx.defense_selection.tactic if side == "attack" else ctx.attack_selection.tactic
    if other_tactic and other_tactic.name == "Pressing Alto":
        attack_mod(ctx, side, -2, f"{side}: Fabrizio penalizzato da Pressing Alto")



def _apply_sandrino_ignore_event(game: GameState, ctx: TurnContext, side: str) -> None:
    if side == "attack":
        ctx.attack_ignore_event = True
    else:
        ctx.defense_ignore_event = True
    ctx.notes.append(f"{side}: Sandrino ignora l'Evento")



def _opponent_tactic_gives_defense_bonus(ctx: TurnContext, side: str) -> bool:
    other_tactic = ctx.defense_selection.tactic if side == "attack" else ctx.attack_selection.tactic
    return other_tactic is not None and other_tactic.name in {"Possesso Palla", "Cerca Uomo", "Catenaccio"}



def _apply_sandrino_vs_defense_bonus(game: GameState, ctx: TurnContext, side: str) -> None:
    if _opponent_tactic_gives_defense_bonus(ctx, side):
        attack_mod(ctx, side, -2, f"{side}: Sandrino soffre bonus difensivo avversario")



def _apply_salvatore_colpo_genio(game: GameState, ctx: TurnContext, side: str) -> None:
    roll = game.rng.randint(1, 6)
    if roll > 3:
        attack_mod(ctx, side, 3, f"{side}: Salvatore colpo di genio +3 (dado {roll})")
    else:
        attack_mod(ctx, side, -2, f"{side}: Salvatore colpo di genio -2 (dado {roll})")



def _apply_ernesto_vetrallese(game: GameState, ctx: TurnContext, side: str) -> None:
    team = team_for_side(game, ctx, side)
    other = game.teams[ctx.defense_team_idx if side == "attack" else ctx.attack_team_idx]
    if team.score >= other.score:
        attack_mod(ctx, side, -1, f"{side}: Ernesto -1 se non in svantaggio")



def _apply_sebas_ahead_penalty(game: GameState, ctx: TurnContext, side: str) -> None:
    team = team_for_side(game, ctx, side)
    other = game.teams[ctx.defense_team_idx if side == "attack" else ctx.attack_team_idx]
    if team.score - other.score >= 2:
        attack_mod(ctx, side, -2, f"{side}: Sebas -2 se avanti di 2+")



def _apply_massi_marking(game: GameState, ctx: TurnContext, side: str) -> None:
    if side != "defense":
        return
    other = opposing_lineup(ctx, side)
    if not other:
        return
    max_attack = max(card.attack for card in other)
    ctx.attack_value -= 2
    target_names = [card.name for card in other if card.attack == max_attack]
    ctx.notes.append(f"{side}: Massi marca {'/'.join(target_names)} (-2 attacco avversario)")



def _apply_massi_event_penalty(game: GameState, ctx: TurnContext, side: str) -> None:
    if ctx.event_card is not None:
        defense_mod(ctx, side, -1, f"{side}: Massi -1 difesa se la squadra gioca un Evento")



def _apply_dave_wins_ties(game: GameState, ctx: TurnContext, side: str) -> None:
    if side == "attack":
        ctx.attack_wins_ties = True
        ctx.defense_wins_ties = False
    else:
        ctx.defense_wins_ties = True
        ctx.attack_wins_ties = False
    ctx.notes.append(f"{side}: Dave fa vincere i pareggi")



def _apply_dave_wear(game: GameState, ctx: TurnContext, side: str) -> None:
    team = team_for_side(game, ctx, side)
    plays = team.play_counts.get("Dave", 0)
    if plays >= 2:
        attack_mod(ctx, side, -1, f"{side}: Dave logorato -1 attacco")
        defense_mod(ctx, side, -1, f"{side}: Dave logorato -1 difesa")


PLAYER_EFFECTS = {
    "attaccante_combo": _apply_attaccante_combo,
    "difensore_combo": _apply_difensore_combo,
    "regista_draw_tactic": _apply_regista_draw_tactic,
    "portiere_save": _apply_portiere_save,
    "mediano_support": _apply_mediano_support,
    "franz_motivatore": _apply_franz_motivatore,
    "franz_urlatore": _apply_franz_urlatore,
    "lorenzo_assist": _apply_lorenzo_assist,
    "lorenzo_cocciuto": _apply_lorenzo_cocciuto,
    "fabrizio_miracolo": lambda game, ctx, side: ctx.notes.append(f"{side}: Fabrizio pronto a ridurre il dado avversario"),
    "fabrizio_pressing_penalty": _apply_fabrizio_pressing_penalty,
    "sandrino_ignore_event": _apply_sandrino_ignore_event,
    "sandrino_vs_defense_bonus": _apply_sandrino_vs_defense_bonus,
    "salvatore_colpo_genio": _apply_salvatore_colpo_genio,
    "ernesto_event_anytime": lambda game, ctx, side: ctx.notes.append(f"{side}: Ernesto permetterebbe Evento fuori svantaggio (hook pronto)"),
    "ernesto_vetrallese": _apply_ernesto_vetrallese,
    "sebas_goal_spectacular": lambda game, ctx, side: _set_auto_spectacular(ctx, side, True),
    "sebas_ahead_penalty": _apply_sebas_ahead_penalty,
    "massi_marking": _apply_massi_marking,
    "massi_event_penalty": _apply_massi_event_penalty,
    "dave_wins_ties": _apply_dave_wins_ties,
    "dave_wear": _apply_dave_wear,
}


# Tactics

def apply_tactic_effect(game: GameState, ctx: TurnContext, side: str) -> None:
    tactic = ctx.attack_selection.tactic if side == "attack" else ctx.defense_selection.tactic
    if tactic is None:
        return
    if side == "attack" and ctx.nullify_attack_tactic:
        ctx.notes.append("attack: Tattica annullata")
        return
    if side == "defense" and ctx.nullify_defense_tactic:
        ctx.notes.append("defense: Tattica annullata")
        return
    effect = TACTIC_EFFECTS.get(tactic.effect)
    if effect is not None:
        effect(game, ctx, side)



def _pressing_alto(game: GameState, ctx: TurnContext, side: str) -> None:
    attack_mod(ctx, side, 1, f"{side}: Pressing Alto +1 attacco")
    penalty = -3 if any(card.name == "Sebas" for card in opposing_lineup(ctx, side)) else -2
    defense_mod(ctx, side, penalty, f"{side}: Pressing Alto {penalty} difesa")
    if side == "defense":
        ctx.defense_extra_momentum_on_stop += 1
        ctx.notes.append("defense: Pressing Alto dà +1 impeto extra se la difesa regge")



def _contropiede(game: GameState, ctx: TurnContext, side: str) -> None:
    attack_mod(ctx, side, 3, f"{side}: Contropiede +3 attacco")
    defense_mod(ctx, side, -1, f"{side}: Contropiede -1 difesa")



def _possesso_palla(game: GameState, ctx: TurnContext, side: str) -> None:
    attack_mod(ctx, side, 1, f"{side}: Possesso +1 attacco")
    defense_mod(ctx, side, 1, f"{side}: Possesso +1 difesa")



def _cerca_uomo(game: GameState, ctx: TurnContext, side: str) -> None:
    bonus = 3 if any(card.name == "Jos" for card in lineup_for_side(ctx, side)) else 2
    defense_mod(ctx, side, bonus, f"{side}: Cerca Uomo +{bonus} difesa")



def _lancio_lungo(game: GameState, ctx: TurnContext, side: str) -> None:
    attack_mod(ctx, side, -1, f"{side}: Lancio Lungo -1 attacco")
    defense_mod(ctx, side, -1, f"{side}: Lancio Lungo -1 difesa")
    if side == "defense":
        ctx.defense_defense_stop_counterroll = True
        ctx.notes.append("defense: Lancio Lungo può creare occasione su 6 dopo una difesa riuscita")



def _catenaccio(game: GameState, ctx: TurnContext, side: str) -> None:
    other = opposing_lineup(ctx, side)
    if sum(1 for card in other if card.attack > card.defense) >= 2:
        defense_mod(ctx, side, 3, f"{side}: Catenaccio +3 difesa")



def _polemica_continua(game: GameState, ctx: TurnContext, side: str) -> None:
    if side == "attack":
        ctx.nullify_defense_tactic = True
    else:
        ctx.nullify_attack_tactic = True
    ctx.notes.append(f"{side}: Polemica continua annulla la tattica avversaria")


TACTIC_EFFECTS = {
    "pressing_alto": _pressing_alto,
    "contropiede": _contropiede,
    "possesso_palla": _possesso_palla,
    "cerca_uomo": _cerca_uomo,
    "lancio_lungo": _lancio_lungo,
    "catenaccio": _catenaccio,
    "polemica_continua": _polemica_continua,
}


# Events

def apply_event_effect(game: GameState, ctx: TurnContext) -> None:
    event = ctx.event_card
    if event is None:
        return
    effect = EVENT_EFFECTS.get(event.effect)
    if effect is not None:
        effect(game, ctx)



def _pioggia_intensa(game: GameState, ctx: TurnContext) -> None:
    ctx.meteorological_event = True
    if not ctx.attack_ignore_event:
        ctx.attack_value -= 1
        ctx.notes.append("Evento: Pioggia intensa -1 attacco")



def _distrazione_difensiva(game: GameState, ctx: TurnContext) -> None:
    if not ctx.defense_ignore_event:
        ctx.defense_value -= 2
        ctx.notes.append("Evento: Distrazione difensiva -2 difesa avversaria")



def _bestemmia_multipla(game: GameState, ctx: TurnContext) -> None:
    if not ctx.attack_ignore_event:
        ctx.attack_requires_exact_six = True
        ctx.notes.append("Evento: Bestemmia multipla, segna solo con 6")



def _aperitivo_pre_partita(game: GameState, ctx: TurnContext) -> None:
    if not ctx.attack_ignore_event:
        malus = sum(1 for card in ctx.attack_selection.players if card.name != "Franz")
        ctx.attack_value -= malus
        ctx.notes.append(f"Evento: Aperitivo -{malus} attacco")
    if not ctx.defense_ignore_event:
        malus = sum(1 for card in ctx.defense_selection.players if card.name != "Franz")
        ctx.defense_value -= malus
        ctx.notes.append(f"Evento: Aperitivo -{malus} difesa")


EVENT_EFFECTS = {
    "pioggia_intensa": _pioggia_intensa,
    "distrazione_difensiva": _distrazione_difensiva,
    "bestemmia_multipla": _bestemmia_multipla,
    "aperitivo_pre_partita": _aperitivo_pre_partita,
}


# Resolution helpers

def apply_player_effects(game: GameState, ctx: TurnContext) -> None:
    for side in ("attack", "defense"):
        for card in lineup_for_side(ctx, side):
            if card.positive_effect and card.positive_effect in PLAYER_EFFECTS:
                PLAYER_EFFECTS[card.positive_effect](game, ctx, side)
        for card in lineup_for_side(ctx, side):
            if card.negative_effect and card.negative_effect in PLAYER_EFFECTS:
                PLAYER_EFFECTS[card.negative_effect](game, ctx, side)



def reduce_goal_roll_with_fabrizio(ctx: TurnContext, side_that_is_shooting: str, roll: int) -> int:
    opposing = ctx.defense_selection.players if side_that_is_shooting == "attack" else ctx.attack_selection.players
    if any(card.name == "Fabrizio" for card in opposing):
        roll -= 1
        ctx.notes.append(f"{side_that_is_shooting}: Fabrizio riduce il dado avversario di 1")
    return max(1, roll)
