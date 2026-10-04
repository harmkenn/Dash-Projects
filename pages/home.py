from dash import html, register_page


register_page(__name__, path="/", name="Apps", title="Dash Projects")

layout = html.Main(
    [
        html.Div(
            [
                html.Div("PROJECT DIRECTORY", className="eyebrow"),
                html.H1("Small tools.\nUseful work.", className="home-title"),
                html.P("A home for focused apps that turn personal data into something you can use."),
            ],
            className="home-intro",
        ),
        html.Div(
            [
                html.Div("AVAILABLE APPS", className="eyebrow"),
                html.A(
                    [
                        html.Div(
                            [html.Span("01", className="app-index"), html.Span("DATA INTAKE", className="app-category")],
                            className="app-card-top",
                        ),
                        html.H2("Google Photos Metadata"),
                        html.P("Build a searchable dataset from a Google Takeout export."),
                        html.Div([html.Span("Open app"), html.Span("->", className="app-arrow")], className="app-card-action"),
                    ],
                    href="/apps/google-photos",
                    className="app-card",
                ),
                html.A(
                    [
                        html.Div(
                            [html.Span("02", className="app-index"), html.Span("TRAVEL", className="app-category")],
                            className="app-card-top",
                        ),
                        html.H2("World Route"),
                        html.P("Plan an evenly spaced trip around the world, starting and finishing at home."),
                        html.Div([html.Span("Open app"), html.Span("->", className="app-arrow")], className="app-card-action"),
                    ],
                    href="/apps/world-route",
                    className="app-card",
                ),
            ],
            className="directory-section",
        ),
    ],
    className="home-page page-width",
)