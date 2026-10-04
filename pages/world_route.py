import plotly.graph_objects as go
from dash import Input, Output, callback, clientside_callback, dcc, html, register_page

from world_route import CITIES, MAX_LEGS, MIN_LEGS, build_route, route_distance_km


register_page(__name__, path="/apps/world-route", name="World Route")

START_CITY = "London"
LEG_OPTIONS = [{"label": str(count), "value": count} for count in range(MIN_LEGS, MAX_LEGS + 1)]


def _route_coordinates(route):
    longitudes = []
    latitudes = []
    for first, second in zip(route, route[1:]):
        start_longitude = first.longitude
        end_longitude = second.longitude
        while end_longitude <= start_longitude:
            end_longitude += 360

        crosses_dateline = end_longitude > 180
        if crosses_dateline:
            boundary = 180
            fraction = (boundary - start_longitude) / (end_longitude - start_longitude)
            boundary_latitude = first.latitude + fraction * (second.latitude - first.latitude)
            longitudes.extend([start_longitude, boundary, None, -180, end_longitude - 360, None])
            latitudes.extend(
                [first.latitude, boundary_latitude, None, boundary_latitude, second.latitude, None]
            )
        else:
            longitudes.extend([start_longitude, end_longitude, None])
            latitudes.extend([first.latitude, second.latitude, None])

    return longitudes, latitudes


def _make_map(route):
    line_longitudes, line_latitudes = _route_coordinates(route)
    stops = route[:-1]
    figure = go.Figure()
    figure.add_trace(
        go.Scattergeo(
            lon=line_longitudes,
            lat=line_latitudes,
            mode="lines",
            line={"color": "#df6d51", "width": 2},
            hoverinfo="skip",
            showlegend=False,
        )
    )
    figure.add_trace(
        go.Scattergeo(
            lon=[city.longitude for city in stops[1:]],
            lat=[city.latitude for city in stops[1:]],
            text=[city.label for city in stops[1:]],
            customdata=list(range(1, len(stops))),
            mode="markers",
            marker={"size": 9, "color": "#27634d", "line": {"color": "white", "width": 1.5}},
            hovertemplate="<b>%{text}</b><br>Stop %{customdata}<extra></extra>",
            name="Route stop",
        )
    )
    figure.add_trace(
        go.Scattergeo(
            lon=[stops[0].longitude],
            lat=[stops[0].latitude],
            text=[stops[0].label],
            mode="markers",
            marker={"size": 12, "color": "#df6d51", "line": {"color": "white", "width": 1.5}},
            hovertemplate="<b>%{text}</b><br>Starting city<extra></extra>",
            name="Start / finish",
        )
    )
    figure.update_layout(
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        paper_bgcolor="white",
        showlegend=True,
        legend={"orientation": "h", "y": 0, "x": 0.02, "font": {"size": 11}},
        geo={
            "projection_type": "natural earth",
            "showland": True,
            "landcolor": "#f0f1eb",
            "showocean": True,
            "oceancolor": "#f8faf7",
            "showlakes": True,
            "lakecolor": "#f8faf7",
            "showcoastlines": True,
            "coastlinecolor": "#cbd2c7",
            "showcountries": True,
            "countrycolor": "#dfe2d9",
            "bgcolor": "white",
            "lataxis_range": [-60, 85],
        },
    )
    return figure


def _make_stop_list(route):
    stops = route[:-1]
    items = []
    for index, city in enumerate(stops):
        is_start = index == 0
        items.append(
            html.Li(
                [
                    html.Span(f"{index + 1:02}", className="route-stop-index"),
                    html.Div(
                        [
                            html.Div(city.name, className="route-stop-city"),
                            html.Div(city.country, className="route-stop-country"),
                        ]
                    ),
                    html.Span(
                        "START / FINISH" if is_start else f"LEG {index}",
                        className="route-stop-tag" + (" route-stop-tag-start" if is_start else ""),
                    ),
                ],
                className="route-stop",
            )
        )

    items.append(
        html.Li(
            [
                html.Span(f"{len(stops) + 1:02}", className="route-stop-index"),
                html.Div(
                    [
                        html.Div(stops[0].name, className="route-stop-city"),
                        html.Div(stops[0].country, className="route-stop-country"),
                    ]
                ),
                html.Span("FINISH", className="route-stop-tag route-stop-tag-start"),
            ],
            className="route-stop route-stop-finish",
        )
    )
    return html.Ol(items, className="route-stop-list")


layout = html.Main(
    [
        html.A("<- All apps", href="/", className="back-link"),
        html.Div(
            [
                html.Div("TRAVEL / 02", className="eyebrow"),
                html.H1("World Route"),
                html.P(
                    "Pick a home city and a leg count. We’ll space major cities around the globe, "
                    "then bring the route all the way home."
                ),
            ],
            className="tool-heading",
        ),
        html.Section(
            [
                html.Div(
                    [
                        html.Label("Starting city", htmlFor="world-route-start", className="field-label"),
                        dcc.Dropdown(
                            id="world-route-start",
                            options=[
                                {"label": city.label, "value": city.name}
                                for city in sorted(CITIES, key=lambda item: item.name)
                            ],
                            value=START_CITY,
                            clearable=False,
                            searchable=True,
                            className="route-dropdown",
                        ),
                    ],
                    className="route-control",
                ),
                html.Div(
                    [
                        html.Label("Total route legs", htmlFor="world-route-legs", className="field-label"),
                        dcc.Dropdown(
                            id="world-route-legs",
                            options=LEG_OPTIONS,
                            value=6,
                            clearable=False,
                            searchable=False,
                            className="route-dropdown route-leg-dropdown",
                        ),
                        html.Div(
                            "Includes the final leg back to your starting city.",
                            className="route-control-hint",
                        ),
                    ],
                    className="route-control route-control-legs",
                ),
            ],
            className="route-controls",
        ),
        html.Section(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div("0", id="world-route-leg-count", className="metric-value"),
                                html.Div("route legs", className="metric-label"),
                            ],
                            className="metric",
                        ),
                        html.Div(
                            [
                                html.Div("0 km", id="world-route-distance", className="metric-value"),
                                html.Div("approximate distance", className="metric-label"),
                            ],
                            className="metric",
                        ),
                    ],
                    className="metrics route-metrics",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div("ROUTE MAP", className="eyebrow"),
                                        html.Button(
                                            "Print / Save PDF",
                                            id="world-route-print-button",
                                            n_clicks=0,
                                            className="primary-button route-print-button",
                                        ),
                                    ],
                                    className="route-map-heading",
                                ),
                                html.Div(id="world-route-print-summary", className="route-print-summary"),
                                dcc.Graph(
                                    id="world-route-map",
                                    config={"displayModeBar": False, "responsive": True},
                                    className="route-map",
                                ),
                                html.Div(id="world-route-print-status", className="visually-hidden", role="status"),
                            ],
                            className="route-map-panel",
                        ),
                        html.Div(
                            [
                                html.Div("YOUR CITIES", className="eyebrow"),
                                html.Div(id="world-route-stops"),
                            ],
                            className="route-stops-panel",
                        ),
                    ],
                    className="route-results-grid",
                ),
            ],
            className="results-section world-route-results",
        ),
    ],
    className="tool-page page-width",
)


@callback(
    Output("world-route-map", "figure"),
    Output("world-route-stops", "children"),
    Output("world-route-leg-count", "children"),
    Output("world-route-distance", "children"),
    Output("world-route-print-summary", "children"),
    Input("world-route-start", "value"),
    Input("world-route-legs", "value"),
)
def update_world_route(start_name, leg_count):
    route = build_route(start_name, leg_count)
    distance = route_distance_km(route)
    start = route[0]
    return (
        _make_map(route),
        _make_stop_list(route),
        str(leg_count),
        f"{distance:,.0f} km",
        f"{start.label}  |  {leg_count} legs  |  Approx. {distance:,.0f} km",
    )


clientside_callback(
    """
    function (clicks) {
        if (!clicks) {
            return "";
        }
        window.print();
        return "";
    }
    """,
    Output("world-route-print-status", "children"),
    Input("world-route-print-button", "n_clicks"),
    prevent_initial_call=True,
)
