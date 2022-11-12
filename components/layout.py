from dash import Dash, html, dcc

import dash_bootstrap_components as dbc

from . import dateinput, geolocation, weather, panels, result_graph, ids


def create_layout(app: Dash) -> dbc.Container:
    return dbc.Container(
        [
            dbc.NavbarSimple(
                children=[
                    dbc.NavItem(
                        dbc.NavLink(html.P("look at the sourcecode on my")),
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            html.H4([html.I(className="bi bi-github me-2"), "Github"]),
                            href="https://github.com/flecksi/pv_design_app",
                            target="https://github.com/flecksi/pv_design_app",
                        )
                    ),
                ],
                brand="PV Design - plan your photovoltaic system and estimate its yield",
                fluid=True,
                # brand_href="#",
                color="dark",
                sticky="top",
                dark=True,
            ),
            dbc.Row(dbc.Col(geolocation.render(app))),
            dbc.Row(dbc.Col(weather.render(app))),
            dbc.Row(
                [
                    dbc.Col(
                        children=[panels.render(app)],
                        width="auto",
                        style={"maxHeight": "70vh", "overflow": "scroll"},
                    ),
                    dbc.Col(
                        children=[
                            dbc.Row(
                                [
                                    dbc.Tabs(
                                        [
                                            dbc.Tab(
                                                label="Day",
                                                tab_style={"marginLeft": "auto"},
                                                tab_id=ids.TAB_PLOT_DAY,
                                            ),
                                            dbc.Tab(
                                                label="Year",
                                                tab_style={"marginRight": "auto"},
                                                tab_id=ids.TAB_PLOT_YEAR,
                                            ),
                                        ],
                                        id=ids.TABS_PLOT,
                                    ),
                                    dateinput.render(app),
                                    dbc.Row(result_graph.render(app)),
                                ]
                            ),
                        ],
                        width=True,
                    ),
                ]
            ),
        ],
        fluid=True,
    )
