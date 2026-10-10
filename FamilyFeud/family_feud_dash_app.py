"""Dash page for the Family Feud game."""

import importlib.util
import random
from pathlib import Path

from dash import ALL, Input, Output, State, ctx, dcc, html, no_update


def _load_feud_data():
    try:
        from .data import feud_data
    except ImportError:
        try:
            from data import feud_data
        except ImportError:
            path = Path(__file__).with_name("data.py")
            spec = importlib.util.spec_from_file_location("_family_feud_data", path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Unable to load Family Feud data from {path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            feud_data = module.feud_data
    return feud_data


FEUD_DATA = _load_feud_data()
PREFIX = "feud"
STORE_ID = f"{PREFIX}-state"


def _initial_state():
    game_indices = list(range(len(FEUD_DATA)))
    random.shuffle(game_indices)
    return {
        "game_indices": game_indices,
        "round_index": 0,
        "scores": [0, 0],
        "revealed": [],
        "strikes": 0,
        "round_points": 0,
    }


def _reset_round(state, new_round_index):
    state["round_index"] = new_round_index
    state["revealed"] = []
    state["strikes"] = 0
    state["round_points"] = 0


def _score_box(team_number, score, background):
    return html.Div(
        [f"Team {team_number}", html.Br(), str(score)],
        style={
            "fontSize": "24px",
            "fontWeight": "bold",
            "textAlign": "center",
            "padding": "10px",
            "borderRadius": "10px",
            "color": "white",
            "backgroundColor": background,
        },
    )


def _answer_card(answer_text, points, revealed):
    if revealed:
        return html.Div(
            [html.Span(answer_text), html.Span(str(points))],
            style={
                "backgroundColor": "#FEF3C7",
                "color": "#1E3A8A",
                "fontSize": "24px",
                "fontWeight": "bold",
                "padding": "15px 20px",
                "margin": "5px 0",
                "borderRadius": "8px",
                "border": "2px solid #1E3A8A",
                "height": "70px",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "space-between",
                "boxShadow": "3px 3px 5px rgba(0,0,0,.3)",
            },
        )
    return html.Div(
        "",
        style={
            "backgroundColor": "#1E40AF",
            "color": "white",
            "fontSize": "24px",
            "fontWeight": "bold",
            "padding": "15px",
            "margin": "5px 0",
            "borderRadius": "8px",
            "border": "2px solid white",
            "height": "70px",
            "boxShadow": "3px 3px 5px rgba(0,0,0,.3)",
        },
    )


def _render_view(state):
    actual_index = state["game_indices"][state["round_index"]]
    current_data = FEUD_DATA[actual_index]
    answers = current_data["answers"]
    split_at = (len(answers) + 1) // 2
    columns = [answers[:split_at], answers[split_at:]]
    boards = []
    for column_index, answer_column in enumerate(columns):
        answer_rows = []
        first_answer_index = 0 if column_index == 0 else split_at
        for local_index, (answer_text, points) in enumerate(answer_column):
            answer_index = first_answer_index + local_index
            revealed = answer_index in state["revealed"]
            answer_rows.append(
                html.Div(
                    [
                        html.Button(
                            "✔" if revealed else str(answer_index + 1),
                            id={"type": f"{PREFIX}-reveal", "index": answer_index},
                            n_clicks=0,
                            disabled=revealed,
                            style={"width": "54px", "height": "54px", "fontSize": "20px"},
                        ),
                        _answer_card(answer_text, points, revealed),
                    ],
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "54px minmax(0, 1fr)",
                        "alignItems": "center",
                        "gap": "8px",
                    },
                )
            )
        boards.append(html.Div(answer_rows, style={"flex": "1", "minWidth": "280px"}))

    strikes = " ".join(["❌"] * state["strikes"]) if state["strikes"] else ""
    return html.Div(
        [
            html.H1("👨‍👩‍👧‍👦 Family Feud"),
            html.Div(
                [
                    html.Div(
                        [
                            _score_box(1, state["scores"][0], "#3b82f6"),
                            html.Button("Award Bank to Team 1", id=f"{PREFIX}-award-0", n_clicks=0, style={"width": "100%", "marginTop": "8px"}),
                        ],
                        style={"flex": "1"},
                    ),
                    html.Div(
                        f"BANK: {state['round_points']}",
                        style={"textAlign": "center", "fontSize": "40px", "fontWeight": "bold", "flex": "2"},
                    ),
                    html.Div(
                        [
                            _score_box(2, state["scores"][1], "#ef4444"),
                            html.Button("Award Bank to Team 2", id=f"{PREFIX}-award-1", n_clicks=0, style={"width": "100%", "marginTop": "8px"}),
                        ],
                        style={"flex": "1"},
                    ),
                ],
                style={"display": "flex", "alignItems": "center", "gap": "16px"},
            ),
            html.Hr(),
            html.Div(
                current_data["question"],
                style={
                    "fontSize": "32px",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "color": "#1E3A8A",
                    "marginBottom": "20px",
                    "padding": "20px",
                    "backgroundColor": "#DBEAFE",
                    "borderRadius": "10px",
                    "border": "2px solid #1E3A8A",
                },
            ),
            html.Div(boards, style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}),
            html.Hr(),
            html.Div(
                [
                    html.Section(
                        [
                            html.H3("Strikes"),
                            html.Button("❌ Strike", id=f"{PREFIX}-strike", n_clicks=0),
                            html.Button("Clear", id=f"{PREFIX}-clear-strikes", n_clicks=0, style={"marginLeft": "8px"}),
                            html.Div(strikes, style={"fontSize": "60px", "minHeight": "70px", "color": "#DC2626", "fontWeight": "900"}),
                        ],
                        style={"flex": "1"},
                    ),
                    html.Section(
                        [
                            html.H3("Navigation"),
                            html.Button(
                                "⬅️ Prev",
                                id=f"{PREFIX}-prev",
                                n_clicks=0,
                                disabled=state["round_index"] <= 0,
                            ),
                            html.Button(
                                "Next ➡️",
                                id=f"{PREFIX}-next",
                                n_clicks=0,
                                disabled=state["round_index"] >= len(state["game_indices"]) - 1,
                                style={"marginLeft": "8px"},
                            ),
                        ],
                        style={"flex": "1"},
                    ),
                ],
                style={"display": "flex", "gap": "24px", "flexWrap": "wrap"},
            ),
        ],
        style={"fontFamily": "Arial, sans-serif", "maxWidth": "1100px", "margin": "0 auto"},
    )


def layout():
    state = _initial_state()
    return html.Div(
        [
            dcc.Store(id=STORE_ID, data=state, storage_type="session"),
            html.Div(_render_view(state), id=f"{PREFIX}-view"),
        ]
    )


def register_callbacks(app):
    @app.callback(
        Output(STORE_ID, "data"),
        Input(f"{PREFIX}-next", "n_clicks"),
        Input(f"{PREFIX}-prev", "n_clicks"),
        Input(f"{PREFIX}-strike", "n_clicks"),
        Input(f"{PREFIX}-clear-strikes", "n_clicks"),
        Input(f"{PREFIX}-award-0", "n_clicks"),
        Input(f"{PREFIX}-award-1", "n_clicks"),
        Input({"type": f"{PREFIX}-reveal", "index": ALL}, "n_clicks"),
        State(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def update_game(_next, _prev, _strike, _clear, _award_0, _award_1, _reveals, current):
        if not current:
            return _initial_state()
        state = dict(current)
        triggered = ctx.triggered_id
        if not ctx.triggered or not ctx.triggered[0].get("value"):
            return no_update
        if triggered == f"{PREFIX}-next":
            if state["round_index"] < len(state["game_indices"]) - 1:
                _reset_round(state, state["round_index"] + 1)
            return state
        if triggered == f"{PREFIX}-prev":
            if state["round_index"] > 0:
                _reset_round(state, state["round_index"] - 1)
            return state
        if triggered == f"{PREFIX}-strike":
            state["strikes"] = min(3, state["strikes"] + 1)
            return state
        if triggered == f"{PREFIX}-clear-strikes":
            state["strikes"] = 0
            return state
        if triggered == f"{PREFIX}-award-0" or triggered == f"{PREFIX}-award-1":
            team_index = int(triggered.rsplit("-", 1)[1])
            state["scores"][team_index] += state["round_points"]
            state["round_points"] = 0
            return state
        if isinstance(triggered, dict) and triggered.get("type") == f"{PREFIX}-reveal":
            answer_index = int(triggered["index"])
            actual_index = state["game_indices"][state["round_index"]]
            answers = FEUD_DATA[actual_index]["answers"]
            if answer_index not in state["revealed"] and 0 <= answer_index < len(answers):
                state["revealed"] = [*state["revealed"], answer_index]
                state["round_points"] += answers[answer_index][1]
            return state
        return no_update

    @app.callback(
        Output(f"{PREFIX}-view", "children"),
        Input(STORE_ID, "data"),
    )
    def render_game(state):
        return _render_view(state or _initial_state())
