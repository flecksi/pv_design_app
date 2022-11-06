from dash import Dash, html, dcc

import dash_bootstrap_components as dbc

from . import geolocation, panels, result_graph, ids


def create_layout(app: Dash) -> dbc.Container:
    return dbc.Container(
        [
            dbc.Row(dbc.Col(geolocation.render(app))),
            dbc.Row(
                [
                    dbc.Col(
                        children=[panels.render(app)],
                        # style=dict(background="grey"),
                        width="auto",
                    ),
                    dbc.Col(
                        children=[result_graph.render(app)],
                        # style=dict(background="orange"),
                        width=True,
                    ),
                ]
            ),
        ],
        fluid=True,
    )
