import random
import time
from collections import defaultdict

from dash import ALL, Input, Output, State, ctx, dcc, html

from question_bank import question_bank


TEAM_COLORS = ["#3b82f6", "#ef4444", "#22c55e", "#a855f7"]
TEAM_COUNT = 4
TIMER_DURATIONS = {"reading": 15, "answering": 10, "discussion": 30}


def _questions_by_category():
    categories = defaultdict(list)
    for question in question_bank:
        categories[question["category"]].append(question)
    return categories


def _new_game():
    category_map = _questions_by_category()
    selected_categories = random.sample(list(category_map), 5)
    board = {}
    for category in selected_categories:
        questions = category_map[category]
        chosen = random.choices(questions, k=5) if len(questions) < 5 else random.sample(questions, 5)
        board[category] = {
            str((index + 1) * 100): {"q": item["q"], "a": item["a"]}
            for index, item in enumerate(chosen)
        }
    return {
        "board": board,
        "team_names": [f"Team {index + 1}" for index in range(TEAM_COUNT)],
        "team_scores": [0] * TEAM_COUNT,
        "current_team": 0,
        "current_question": None,
        "answered_questions": [],
        "show_answer": False,
        "timer_start": None,
        "timer_running": False,
        "timer_mode": "reading",
        "first_buzz": None,
    }


def _remaining(game, now=None):
    duration = TIMER_DURATIONS[game["timer_mode"]]
    if not game["timer_running"] or game["timer_start"] is None:
        return duration
    now = time.time() if now is None else now
    return max(0, duration - int(now - game["timer_start"]))


def _timer_color(seconds_left, mode):
    total = TIMER_DURATIONS[mode]
    if seconds_left > total * 0.6:
        return "#22c55e"
    if seconds_left > total * 0.3:
        return "#eab308"
    return "#ef4444"


def _render_game(game):
    category_columns = []
    for category, values in game["board"].items():
        buttons = [html.H3(category)]
        for points in values:
            key = [category, points]
            answered = key in game["answered_questions"]
            buttons.append(
                html.Button(
                    f"${points}",
                    id={"type": "jeopardy-question", "category": category, "points": points},
                    n_clicks=0,
                    disabled=answered or game["current_question"] is not None,
                    style={"width": "100%", "minHeight": "3rem", "marginBottom": "0.4rem"},
                )
            )
        category_columns.append(
            html.Div(buttons, style={"flex": "1 1 16%", "minWidth": "150px", "padding": "0.35rem"})
        )

    team_cards = []
    for index, name in enumerate(game["team_names"]):
        selected = index == game["current_team"]
        team_cards.append(
            html.Div(
                [
                    html.Button(
                        name,
                        id={"type": "jeopardy-team-select", "index": index},
                        n_clicks=0,
                        style={
                            "width": "100%",
                            "padding": "0.7rem 0.3rem",
                            "fontSize": "1rem",
                            "fontWeight": "bold",
                            "color": "white" if selected else TEAM_COLORS[index],
                            "backgroundColor": TEAM_COLORS[index] if selected else "white",
                            "border": f"3px solid {TEAM_COLORS[index]}",
                            "borderRadius": "0.6rem",
                        },
                    ),
                    dcc.Input(
                        id={"type": "jeopardy-team-name", "index": index},
                        value=name,
                        maxLength=30,
                        debounce=True,
                        placeholder=f"Team {index + 1}",
                        style={"width": "calc(100% - 1rem)", "margin": "0.4rem"},
                    ),
                    html.Div(
                        f"${game['team_scores'][index]}",
                        style={"textAlign": "center", "fontSize": "1.2rem", "fontWeight": "bold", "color": TEAM_COLORS[index]},
                    ),
                ],
                style={"flex": "1", "minWidth": "130px", "padding": "0.4rem"},
            )
        )

    question_view = []
    if game["current_question"]:
        category, points = game["current_question"]
        question = game["board"][category][points]
        seconds = _remaining(game)
        first_buzz = game["first_buzz"]
        question_view = [
            html.H2(f"{category} — ${points}"),
            html.H3(question["q"]),
            html.Div(
                str(seconds),
                style={
                    "fontSize": "5rem",
                    "fontWeight": "800",
                    "textAlign": "center",
                    "padding": "0.5rem 1rem",
                    "borderRadius": "1rem",
                    "margin": "1rem auto",
                    "backgroundColor": _timer_color(seconds, game["timer_mode"]),
                    "color": "white",
                    "width": "min(60%, 420px)",
                },
            ),
            html.Div(
                f"🔔 {game['team_names'][first_buzz]} buzzed in first!"
                if first_buzz is not None
                else "No team has buzzed in yet.",
                style={
                    "backgroundColor": "#22c55e" if first_buzz is not None else "#e8eef5",
                    "color": "white" if first_buzz is not None else "#333",
                    "padding": "1rem",
                    "textAlign": "center",
                    "fontSize": "1.25rem",
                    "fontWeight": "bold",
                    "borderRadius": "0.6rem",
                },
            ),
            html.H4("Team buzzers"),
            html.Div(
                [
                    html.Button(
                        f"🔴 {game['team_names'][index]} — BUZZ IN!",
                        id={"type": "jeopardy-buzz", "index": index},
                        n_clicks=0,
                        disabled=not game["timer_running"] or game["timer_mode"] != "reading" or first_buzz is not None,
                        style={"flex": "1", "minWidth": "180px", "padding": "0.9rem", "margin": "0.25rem"},
                    )
                    for index in range(TEAM_COUNT)
                ],
                style={"display": "flex", "flexWrap": "wrap"},
            ),
            html.Div(
                [
                    html.Button("▶️ Restart Timer", id="jeopardy-restart-timer", n_clicks=0),
                    html.Button("⏹️ Stop Timer", id="jeopardy-stop-timer", n_clicks=0),
                    html.Button("🧹 Clear Buzzers", id="jeopardy-clear-buzzers", n_clicks=0),
                    html.Button("👁️ Show Answer", id="jeopardy-show-answer", n_clicks=0),
                ],
                style={"display": "flex", "gap": "0.5rem", "flexWrap": "wrap", "margin": "1rem 0"},
            ),
        ]
        if game["show_answer"]:
            question_view.extend(
                [
                    html.H3(f"✅ Answer: {question['a']}"),
                    html.Button("⏳ Start Discussion Timer (30s)", id="jeopardy-discussion-timer", n_clicks=0),
                    html.Div(
                        [
                            html.Button("✅ Correct", id="jeopardy-correct", n_clicks=0),
                            html.Button("❌ Wrong", id="jeopardy-wrong", n_clicks=0),
                            html.Button("➡️ Skip", id="jeopardy-skip", n_clicks=0),
                        ],
                        style={"display": "flex", "gap": "0.5rem", "marginTop": "0.75rem"},
                    ),
                ]
            )
    else:
        question_view = [html.P("Choose a question to start a round.")]

    return html.Div(
        [
            html.H1("📘 Scripture Jeopardy — Teacher Control"),
            html.Div(team_cards, style={"display": "flex", "gap": "0.5rem", "flexWrap": "wrap"}),
            html.Button("💾 Save Team Names", id="jeopardy-save-teams", n_clicks=0, style={"margin": "0.5rem"}),
            html.Hr(),
            html.Div(
                [
                    html.Div(question_view, style={"marginBottom": "1rem"}),
                    html.Div(
                        category_columns,
                        style={"display": "flex", "flexWrap": "wrap", "alignItems": "stretch"},
                    ),
                ]
            ),
            html.P(
                "Buzz-in controls run in this browser session. To buzz from separate devices, the shared app needs a server-side real-time buzzer service.",
                style={"fontSize": "0.85rem", "color": "#666", "marginTop": "1.5rem"},
            ),
        ],
        style={"fontFamily": "Arial, sans-serif"},
    )


def layout():
    game = _new_game()
    return html.Div(
        [
            dcc.Store(id="jeopardy-state", data=game, storage_type="session"),
            dcc.Interval(id="jeopardy-timer-interval", interval=1000, disabled=True),
            html.Div(id="jeopardy-content", children=_render_game(game)),
        ]
    )


def register_callbacks(app):
    @app.callback(
        Output("jeopardy-state", "data"),
        Output("jeopardy-content", "children"),
        Output("jeopardy-timer-interval", "disabled"),
        Input({"type": "jeopardy-question", "category": ALL, "points": ALL}, "n_clicks"),
        Input({"type": "jeopardy-team-select", "index": ALL}, "n_clicks"),
        Input({"type": "jeopardy-buzz", "index": ALL}, "n_clicks"),
        Input("jeopardy-save-teams", "n_clicks"),
        Input("jeopardy-restart-timer", "n_clicks", allow_optional=True),
        Input("jeopardy-stop-timer", "n_clicks", allow_optional=True),
        Input("jeopardy-clear-buzzers", "n_clicks", allow_optional=True),
        Input("jeopardy-show-answer", "n_clicks", allow_optional=True),
        Input("jeopardy-discussion-timer", "n_clicks", allow_optional=True),
        Input("jeopardy-correct", "n_clicks", allow_optional=True),
        Input("jeopardy-wrong", "n_clicks", allow_optional=True),
        Input("jeopardy-skip", "n_clicks", allow_optional=True),
        Input("jeopardy-timer-interval", "n_intervals"),
        State({"type": "jeopardy-team-name", "index": ALL}, "value"),
        State("jeopardy-state", "data"),
        prevent_initial_call=True,
    )
    def update_game(
        _questions,
        _teams,
        _buzzes,
        _save,
        _restart,
        _stop,
        _clear,
        _show_answer,
        _discussion,
        _correct,
        _wrong,
        _skip,
        _ticks,
        team_names,
        data,
    ):
        game = data or _new_game()
        trigger = ctx.triggered_id
        now = time.time()

        if isinstance(trigger, dict):
            if trigger.get("type") == "jeopardy-question":
                selection = [trigger["category"], trigger["points"]]
                if selection not in game["answered_questions"] and game["current_question"] is None:
                    game["current_question"] = selection
                    game["show_answer"] = False
                    game["timer_mode"] = "reading"
                    game["timer_start"] = now
                    game["timer_running"] = True
                    game["first_buzz"] = None
            elif trigger.get("type") == "jeopardy-team-select":
                game["current_team"] = trigger["index"]
            elif trigger.get("type") == "jeopardy-buzz":
                index = trigger["index"]
                if (
                    game["current_question"] is not None
                    and game["timer_running"]
                    and game["timer_mode"] == "reading"
                    and game["first_buzz"] is None
                ):
                    game["first_buzz"] = index
                    game["current_team"] = index
                    game["timer_mode"] = "answering"
                    game["timer_start"] = now
        elif trigger == "jeopardy-save-teams":
            if team_names:
                game["team_names"] = [
                    str(name or "").strip()[:30] or f"Team {index + 1}"
                    for index, name in enumerate(team_names[:TEAM_COUNT])
                ]
        elif trigger == "jeopardy-restart-timer":
            game["timer_start"] = now
            game["timer_running"] = game["current_question"] is not None
        elif trigger == "jeopardy-stop-timer":
            game["timer_running"] = False
        elif trigger == "jeopardy-clear-buzzers":
            game["first_buzz"] = None
        elif trigger == "jeopardy-show-answer":
            game["show_answer"] = True
            game["timer_running"] = False
        elif trigger == "jeopardy-discussion-timer":
            game["timer_mode"] = "discussion"
            game["timer_start"] = now
            game["timer_running"] = True
        elif trigger in ("jeopardy-correct", "jeopardy-wrong", "jeopardy-skip"):
            if game["current_question"] is not None:
                category, points_text = game["current_question"]
                points = int(points_text)
                if trigger == "jeopardy-correct":
                    game["team_scores"][game["current_team"]] += points
                elif trigger == "jeopardy-wrong":
                    game["team_scores"][game["current_team"]] -= points
                game["answered_questions"].append([category, points_text])
                game["current_question"] = None
                game["show_answer"] = False
                game["timer_running"] = False
                game["timer_start"] = None
        elif trigger == "jeopardy-timer-interval" and game["timer_running"] and _remaining(game, now) == 0:
            game["timer_running"] = False

        return game, _render_game(game), not game["timer_running"]
