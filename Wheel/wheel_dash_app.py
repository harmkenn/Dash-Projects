"""Dash page for the Scripture Wheel game."""

import importlib.util
import random
import time
from pathlib import Path

from dash import ALL, Input, Output, State, ctx, dcc, html, no_update


def _load_puzzle_bank():
    try:
        from .puzzle_bank import PUZZLE_BANK
    except ImportError:
        try:
            from puzzle_bank import PUZZLE_BANK
        except ImportError:
            path = Path(__file__).with_name("puzzle_bank.py")
            spec = importlib.util.spec_from_file_location("_wheel_puzzle_bank", path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Unable to load puzzle bank from {path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            PUZZLE_BANK = module.PUZZLE_BANK
    return PUZZLE_BANK


PUZZLE_BANK = _load_puzzle_bank()
TEAM_NAMES = ["Team 1", "Team 2", "Team 3", "Team 4"]
TEAM_COLORS = ["#3b82f6", "#ef4444", "#22c55e", "#a855f7"]
VOWEL_COST = 200
RANDOM_VALUES = [100, 200, 300, 400, 500, "Lose Turn"]
TIMER_DURATION = 20
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

PREFIX = "wheel"
STORE_ID = f"{PREFIX}-state"
INTERVAL_ID = f"{PREFIX}-timer-tick"


def _start_turn(state):
    """Spin automatically when a playable turn has no value, as in the original."""
    if state["puzzle"] and not state["revealed"] and state["random_value"] is None:
        state["random_value"] = random.choice(RANDOM_VALUES)
        state["paused_time"] = None
        if state["timer_enabled"] and state["random_value"] != "Lose Turn":
            state["timer_start"] = time.time()
            state["timer_running"] = True
        else:
            state["timer_start"] = None
            state["timer_running"] = False


def _new_game_state():
    state = {
        "team_scores": [0, 0, 0, 0],
        "current_team": 0,
        "puzzle": random.choice(PUZZLE_BANK),
        "guessed_letters": [],
        "revealed": False,
        "random_value": None,
        "day_totals": [0, 0, 0, 0],
        "timer_start": None,
        "timer_running": False,
        "paused_time": None,
        "timer_enabled": True,
        "message": "",
        "message_kind": "info",
    }
    _start_turn(state)
    return state


def _time_left(state, now=None):
    now = time.time() if now is None else now
    if state["paused_time"] is not None:
        return int(state["paused_time"])
    if not state["timer_running"] or state["timer_start"] is None:
        return TIMER_DURATION
    return max(0, TIMER_DURATION - int(now - state["timer_start"]))


def _stop_timer(state):
    state["timer_running"] = False
    state["timer_start"] = None
    state["paused_time"] = None


def _message(state, text="", kind="info"):
    state["message"] = text
    state["message_kind"] = kind


def _card_style(revealed):
    style = {
        "minHeight": "68px",
        "padding": "14px 20px",
        "margin": "5px 0",
        "border": "2px solid white",
        "borderRadius": "8px",
        "boxShadow": "3px 3px 5px rgba(0,0,0,.3)",
        "fontSize": "24px",
        "fontWeight": "bold",
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "space-between" if revealed else "center",
        "textAlign": "center",
    }
    if revealed:
        style.update({"backgroundColor": "#FEF3C7", "color": "#1E3A8A", "borderColor": "#1E3A8A"})
    else:
        style.update({"backgroundColor": "#1E40AF", "color": "white"})
    return style


def _render_view(state):
    puzzle = state["puzzle"]
    now = time.time()
    seconds_left = _time_left(state, now)
    if seconds_left > TIMER_DURATION * 0.6:
        timer_color = "#22c55e"
    elif seconds_left > TIMER_DURATION * 0.3:
        timer_color = "#eab308"
    else:
        timer_color = "#ef4444"

    scores = []
    for index, name in enumerate(TEAM_NAMES):
        active = index == state["current_team"]
        scores.append(
            html.Div(
                [
                    html.Div(name),
                    html.Div(f"${state['team_scores'][index]}", style={"fontSize": "1.5rem"}),
                    html.Div(f"Day Total: ${state['day_totals'][index]}", style={"fontSize": ".95rem"}),
                ],
                style={
                    "border": f"{4 if active else 2}px solid {'white' if active else TEAM_COLORS[index]}",
                    "backgroundColor": TEAM_COLORS[index] if active else "transparent",
                    "color": "white" if active else TEAM_COLORS[index],
                    "borderRadius": "10px",
                    "padding": "10px",
                    "textAlign": "center",
                    "fontWeight": "bold",
                    "fontSize": "1.2rem",
                    "marginBottom": "10px",
                },
            )
        )

    words = []
    for word in " ".join(puzzle["text"].upper().split()).split(" "):
        tiles = []
        for char in word:
            if not char.isalpha():
                tiles.append(html.Div(char, style={"width": "38px", "fontSize": "2rem", "fontWeight": "bold", "textAlign": "center"}))
            else:
                visible = char in state["guessed_letters"] or state["revealed"]
                tiles.append(
                    html.Div(
                        char if visible else "",
                        style={
                            "width": "50px",
                            "height": "60px",
                            "backgroundColor": "#3b82f6" if visible else "#334155",
                            "borderRadius": "5px",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "fontSize": "2.2rem",
                            "fontWeight": "bold",
                            "color": "white",
                            "boxShadow": "2px 2px 5px rgba(0,0,0,.3)",
                        },
                    )
                )
        words.append(html.Div(tiles, style={"display": "flex", "gap": "5px"}))

    keyboard = []
    for row in ("ABCDEFGHI", "JKLMNOPQR", "STUVWXYZ"):
        keyboard.append(
            html.Div(
                [
                    html.Button(
                        f"{letter} ($200)" if letter in "AEIOU" else letter,
                        id={"type": f"{PREFIX}-letter", "letter": letter},
                        n_clicks=0,
                        disabled=(
                            letter in state["guessed_letters"]
                            or state["revealed"]
                            or state["random_value"] == "Lose Turn"
                        ),
                        style={"minWidth": "58px", "minHeight": "42px", "margin": "3px"},
                    )
                    for letter in row
                ],
                style={"display": "flex", "flexWrap": "wrap"},
            )
        )

    message = (
        html.Div(
            state["message"],
            role="status",
            style={
                "padding": "8px 12px",
                "margin": "8px 0",
                "borderRadius": "6px",
                "backgroundColor": "#fee2e2" if state["message_kind"] == "error" else "#dbeafe",
                "color": "#991b1b" if state["message_kind"] == "error" else "#1e3a8a",
            },
        )
        if state["message"]
        else html.Div()
    )

    if state["random_value"] == "Lose Turn":
        spin_result = html.Div(
            [
                html.Div(
                    "You landed on 'Lose Turn'! Click below to continue.",
                    style={"color": "#b91c1c", "fontWeight": "bold"},
                ),
                html.Button(
                    "➡️ Next Team",
                    id={"type": f"{PREFIX}-action", "action": "next-team"},
                    n_clicks=0,
                ),
            ]
        )
    else:
        spin_result = html.Div(
            f"Current Spin Value: {state['random_value']}" if state["random_value"] is not None else "Spinning…",
            style={"fontSize": "1.3rem", "fontWeight": "bold"},
        )

    timer_display = (
        html.Div(
            str(seconds_left),
            id=f"{PREFIX}-timer-display",
            style={
                "fontSize": "3rem",
                "fontWeight": "800",
                "textAlign": "center",
                "padding": ".5rem 1rem",
                "borderRadius": "1rem",
                "margin": "1rem auto",
                "backgroundColor": timer_color,
                "color": "white",
            },
        )
        if state["timer_enabled"] and state["timer_running"]
        else html.Div(
            "--",
            id=f"{PREFIX}-timer-display",
            style={
                "fontSize": "3rem",
                "fontWeight": "800",
                "textAlign": "center",
                "padding": ".5rem 1rem",
                "borderRadius": "1rem",
                "margin": "1rem auto",
                "backgroundColor": "#334155",
                "color": "white",
            },
        )
    )

    return html.Div(
        [
            html.Div(
                [
                    html.Aside(
                        [
                            html.H3("Team Scores"),
                            *[
                                html.Div(
                                    [
                                        score,
                                        html.Button(
                                            f"Select {TEAM_NAMES[index]}",
                                            id={"type": f"{PREFIX}-team", "team": index},
                                            n_clicks=0,
                                            style={"width": "100%"},
                                        ),
                                    ]
                                )
                                for index, score in enumerate(scores)
                            ],
                            html.H3("⏱️ Timer"),
                            dcc.Checklist(
                                id=f"{PREFIX}-timer-enabled",
                                options=[{"label": "Timer Enabled", "value": "enabled"}],
                                value=["enabled"] if state["timer_enabled"] else [],
                                inputStyle={"marginRight": "8px"},
                            ),
                            timer_display,
                            html.Div(
                                [
                                    html.Button("⏸️ Pause", id={"type": f"{PREFIX}-action", "action": "pause"}, n_clicks=0, disabled=not state["timer_running"] or not state["timer_enabled"]),
                                    html.Button("▶️ Resume", id={"type": f"{PREFIX}-action", "action": "resume"}, n_clicks=0, disabled=not state["timer_enabled"] or state["timer_running"] or state["paused_time"] is None),
                                ],
                                style={"display": "flex", "gap": "8px"},
                            ),
                        ],
                        style={"flex": "0 0 220px"},
                    ),
                    html.Main(
                        [
                            html.Div(
                                [
                                    html.H1("🎡 Scripture Wheel"),
                                    html.Button("🔄 New Puzzle", id={"type": f"{PREFIX}-action", "action": "new-puzzle"}, n_clicks=0),
                                    html.Div(
                                        [
                                            html.H3("Spin Result"),
                                            spin_result,
                                        ],
                                        style={"textAlign": "center", "margin": "12px"},
                                    ),
                                    html.H3(f"Category: {puzzle['category']}", style={"textAlign": "center"}),
                                    html.Div(words, style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "justifyContent": "center", "margin": "20px 0"}),
                                    html.Hr(),
                                    html.Div(
                                        [
                                            html.Section(
                                                [html.H3("Guess a Letter"), *keyboard],
                                                style={"flex": "2"},
                                            ),
                                            html.Section(
                                                [
                                                    html.H3("Solve the Puzzle"),
                                                    html.Button("✅ Correct", id={"type": f"{PREFIX}-action", "action": "correct"}, n_clicks=0, style={"margin": "4px"}),
                                                    html.Button("❌ Incorrect", id={"type": f"{PREFIX}-action", "action": "incorrect"}, n_clicks=0, style={"margin": "4px"}),
                                                ],
                                                style={"flex": "1"},
                                            ),
                                        ],
                                        style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
                                    ),
                                    html.Div(
                                        [
                                            html.H3(f"Puzzle Solved! The phrase was: {puzzle['text']} ({puzzle.get('reference', 'No reference')})"),
                                            html.Button("Next Puzzle ➡️", id={"type": f"{PREFIX}-action", "action": "next-puzzle"}, n_clicks=0),
                                        ]
                                        if state["revealed"]
                                        else html.Div()
                                    ),
                                ],
                                style={"flex": "1", "minWidth": "0"},
                            )
                        ]
                    ),
                ],
                style={"display": "flex", "gap": "24px", "flexWrap": "wrap"},
            ),
            message,
        ],
        style={"fontFamily": "Arial, sans-serif"},
    )


def layout():
    state = _new_game_state()
    return html.Div(
        [
            dcc.Store(id=STORE_ID, data=state, storage_type="session"),
            dcc.Interval(id=INTERVAL_ID, interval=500, n_intervals=0),
            html.Div(_render_view(state), id=f"{PREFIX}-view"),
        ]
    )


def register_callbacks(app):
    @app.callback(
        Output(STORE_ID, "data"),
        Input(INTERVAL_ID, "n_intervals"),
        Input(f"{PREFIX}-timer-enabled", "value"),
        Input({"type": f"{PREFIX}-action", "action": ALL}, "n_clicks"),
        Input({"type": f"{PREFIX}-letter", "letter": ALL}, "n_clicks"),
        Input({"type": f"{PREFIX}-team", "team": ALL}, "n_clicks"),
        State(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def update_game(_tick, timer_value, _action_clicks, _letter_clicks, _team_clicks, current):
        if not current:
            return _new_game_state()
        state = dict(current)
        triggered = ctx.triggered_id
        if triggered is None:
            return no_update

        if triggered == INTERVAL_ID:
            if state["timer_enabled"] and state["timer_running"] and _time_left(state) <= 0:
                _stop_timer(state)
                state["current_team"] = (state["current_team"] + 1) % len(TEAM_NAMES)
                state["random_value"] = None
                _message(state, "Time’s up! Next team’s turn.", "error")
                _start_turn(state)
                return state
            return no_update

        if triggered == f"{PREFIX}-timer-enabled":
            enabled = "enabled" in (timer_value or [])
            if state["timer_enabled"] == enabled:
                return no_update
            state["timer_enabled"] = enabled
            return state

        if isinstance(triggered, dict) and (
            not ctx.triggered or not ctx.triggered[0].get("value")
        ):
            return no_update

        if isinstance(triggered, dict) and triggered.get("type") == f"{PREFIX}-team":
            team = int(triggered["team"])
            if 0 <= team < len(TEAM_NAMES):
                state["current_team"] = team
                state["random_value"] = None
                state["timer_start"] = None
                state["timer_running"] = False
                state["paused_time"] = None
                _message(state)
                _start_turn(state)
            return state

        if isinstance(triggered, dict) and triggered.get("type") == f"{PREFIX}-action":
            action = triggered.get("action")
            if action in {"new-puzzle", "next-puzzle"}:
                fresh = _new_game_state()
                fresh["team_scores"] = state["team_scores"]
                fresh["day_totals"] = state["day_totals"]
                fresh["current_team"] = state["current_team"]
                fresh["timer_enabled"] = state["timer_enabled"]
                if not fresh["timer_enabled"] and fresh["timer_running"]:
                    fresh["timer_start"] = None
                    fresh["timer_running"] = False
                return fresh
            if action == "pause" and state["timer_running"]:
                state["paused_time"] = _time_left(state)
                state["timer_running"] = False
                state["timer_start"] = None
            elif action == "resume" and state["paused_time"] is not None:
                state["timer_start"] = time.time() - (TIMER_DURATION - state["paused_time"])
                state["timer_running"] = True
                state["paused_time"] = None
            elif action == "next-team" and state["random_value"] == "Lose Turn":
                state["current_team"] = (state["current_team"] + 1) % len(TEAM_NAMES)
                state["random_value"] = None
                _start_turn(state)
            elif action == "correct":
                _stop_timer(state)
                state["team_scores"][state["current_team"]] += 500
                state["day_totals"][state["current_team"]] += state["team_scores"][state["current_team"]]
                state["team_scores"] = [0, 0, 0, 0]
                state["revealed"] = True
                _message(state, f"{TEAM_NAMES[state['current_team']]} solved the puzzle! {state['puzzle'].get('reference', 'No reference available')}", "success")
            elif action == "incorrect":
                _stop_timer(state)
                state["current_team"] = (state["current_team"] + 1) % len(TEAM_NAMES)
                state["random_value"] = None
                _message(state, "Incorrect guess. Next team’s turn.", "error")
                _start_turn(state)
            return state

        if isinstance(triggered, dict) and triggered.get("type") == f"{PREFIX}-letter":
            letter = triggered.get("letter")
            _stop_timer(state)
            if state["random_value"] is None:
                _message(state, "Error: No spin value. Please refresh the page.", "error")
                return state
            phrase = state["puzzle"]["text"].upper()
            if letter in "AEIOU":
                if state["team_scores"][state["current_team"]] < VOWEL_COST:
                    _message(state, "Not enough money to buy a vowel!", "error")
                    return state
                state["team_scores"][state["current_team"]] -= VOWEL_COST
                if phrase.count(letter) == 0:
                    state["current_team"] = (state["current_team"] + 1) % len(TEAM_NAMES)
                    _message(state)
                else:
                    state["guessed_letters"] = sorted(set(state["guessed_letters"]) | {letter})
                    _message(state, f"Vowel '{letter}' guessed correctly!")
                state["random_value"] = None
                _start_turn(state)
                return state

            state["guessed_letters"] = sorted(set(state["guessed_letters"]) | {letter})
            count = phrase.count(letter)
            if count:
                if isinstance(state["random_value"], int):
                    state["team_scores"][state["current_team"]] += count * state["random_value"]
                unique_chars = {char for char in phrase if char.isalpha()}
                if unique_chars.issubset(set(state["guessed_letters"])):
                    state["revealed"] = True
                    _message(state, "Puzzle solved!")
                else:
                    _message(state)
            else:
                state["current_team"] = (state["current_team"] + 1) % len(TEAM_NAMES)
                _message(state)
            state["random_value"] = None
            _start_turn(state)
            return state
        return no_update

    @app.callback(
        Output(f"{PREFIX}-view", "children"),
        Input(STORE_ID, "data"),
    )
    def render_game(state):
        return _render_view(state or _new_game_state())

    @app.callback(
        Output(f"{PREFIX}-timer-display", "children"),
        Output(f"{PREFIX}-timer-display", "style"),
        Input(INTERVAL_ID, "n_intervals"),
        State(STORE_ID, "data"),
    )
    def update_timer_display(_tick, state):
        if not state or not state["timer_enabled"] or not state["timer_running"]:
            return "--", {
                "fontSize": "3rem",
                "fontWeight": "800",
                "textAlign": "center",
                "padding": ".5rem 1rem",
                "borderRadius": "1rem",
                "margin": "1rem auto",
                "backgroundColor": "#334155",
                "color": "white",
            }
        seconds_left = _time_left(state)
        if seconds_left > TIMER_DURATION * 0.6:
            color = "#22c55e"
        elif seconds_left > TIMER_DURATION * 0.3:
            color = "#eab308"
        else:
            color = "#ef4444"
        return seconds_left, {
            "fontSize": "3rem",
            "fontWeight": "800",
            "textAlign": "center",
            "padding": ".5rem 1rem",
            "borderRadius": "1rem",
            "margin": "1rem auto",
            "backgroundColor": color,
            "color": "white",
        }
