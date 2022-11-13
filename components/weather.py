from dash import Dash, html, dcc, Input, Output, ALL
import dash_bootstrap_components as dbc
from datetime import date
import calendar
import numpy as np
from . import ids


def render(app: Dash) -> html.Div:
    @app.callback(
        Output(ids.COLLAPSE_WEATHER, "is_open"),
        Input(ids.SWITCH_WEATHER, "value"),
    )
    def show_hide_weather(switch):
        if switch == True:
            return True
        else:
            return False

    @app.callback(
        Output(ids.STORE_WEATHER, "data"),
        Input(ids.INPUT_WEATHER_OVEREALL, "value"),
        Input({"type": ids.INPUT_WEATHER_MONTH, "index": ALL}, "value"),
        Input(ids.COLLAPSE_WEATHER, "is_open"),
        # prevent_initial_call=True,
    )
    def store_weather(overall_percentage, month_percentages, weather_active):
        if weather_active is False:
            return tuple([1.0] * 12)
        factors = np.array([1.0] * 12)
        if overall_percentage is not None:
            factors *= float(overall_percentage) / 100

        for i, month_percentage in enumerate(month_percentages):
            if month_percentage is not None:
                factors[i] *= float(month_percentage) / 100
        return tuple(factors)

    return dcc.Loading(
        html.Div(
            [
                dcc.Store(id=ids.STORE_WEATHER, storage_type="local"),
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.H4(
                                                [
                                                    html.I(
                                                        className="bi bi-cloud-sun me-2"
                                                    ),
                                                    "Weather",
                                                ]
                                            ),
                                            width="auto",
                                        ),
                                        dbc.Col(
                                            dbc.Switch(
                                                id=ids.SWITCH_WEATHER,
                                                label="Activate",
                                                value=False,
                                                persistence="local",
                                            ),
                                            width=True,
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    html.P(
                                        "The weather influences the output of your PV system and changes over the year. You can enter a percentage for each month which represents the ratio between real and ideal yield (caused by clouds, fog, rain, snow, smog or other reasons) at your location.",
                                        # id=ids.TEXT_GEOLOC,
                                        className="card-text",
                                    )
                                ),
                            ]
                        ),
                        dbc.CardBody(
                            dbc.Collapse(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Row(
                                                        [
                                                            dbc.InputGroup(
                                                                [
                                                                    dbc.InputGroupText(
                                                                        "Overall"
                                                                    ),
                                                                ],
                                                                # className="ml-1 mr-1",
                                                                # size="sm",
                                                            ),
                                                        ]
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Input(
                                                                type="number",
                                                                min=0,
                                                                max=100,
                                                                # step=1,
                                                                inputmode="numeric",
                                                                placeholder="100%",
                                                                persistence="local",
                                                                debounce=True,
                                                                id=ids.INPUT_WEATHER_OVEREALL,
                                                            )
                                                        ]
                                                    ),
                                                ],
                                                className="m-1",
                                                # width="auto",
                                            )
                                            # )
                                            ,
                                            # dbc.Row(
                                            # [
                                            *[
                                                dbc.Col(
                                                    [
                                                        dbc.Row(
                                                            dbc.Col(
                                                                [
                                                                    dbc.InputGroup(
                                                                        [
                                                                            dbc.InputGroupText(
                                                                                f"{calendar.month_abbr[i + 1]}"
                                                                            ),
                                                                        ],
                                                                        # size="sm",  # className="m1 ml-1 mr-1",
                                                                    )
                                                                ],
                                                                # width="auto",
                                                            ),
                                                        ),
                                                        dbc.Row(
                                                            dbc.Input(
                                                                type="number",
                                                                min=0,
                                                                max=100,
                                                                # step=1,
                                                                inputmode="numeric",
                                                                placeholder="100%",
                                                                persistence="local",
                                                                debounce=True,
                                                                id=dict(
                                                                    type=ids.INPUT_WEATHER_MONTH,
                                                                    index=i,
                                                                ),
                                                            ),
                                                        ),
                                                    ],
                                                    className="m-1",
                                                )
                                                for i in range(12)
                                            ],
                                        ]
                                    ),
                                ],
                                is_open=False,
                                id=ids.COLLAPSE_WEATHER,
                            )
                        ),
                    ],
                    color="goldenrod",
                    inverse=True,
                    className="shadow mb-3"
                    # style={"width": "18rem"},
                ),
            ]
        ),
        debug=True,
    )
