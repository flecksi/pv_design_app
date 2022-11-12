import dash
from dash import Dash, html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from datetime import date

from . import ids


def render(app: Dash) -> html.Div:
    @app.callback(
        Output(ids.DIV_DATEPICKER, "hidden"),
        Input(ids.TABS_PLOT, "active_tab"),
    )
    def show_hide_datediv(tab):
        if tab == ids.TAB_PLOT_DAY:
            return False
        else:
            return True

    @app.callback(
        Output(ids.DATEPICKER, "date"),
        State(ids.DATEPICKER, "date"),
        Input(ids.BTN_DATE_TODAY, "n_clicks"),
        Input(ids.BTN_DATE_PMIN, "n_clicks"),
        Input(ids.BTN_DATE_PMAX, "n_clicks"),
        Input(ids.BTN_DATE_EMIN, "n_clicks"),
        Input(ids.BTN_DATE_EMAX, "n_clicks"),
        prevent_initial_call=True,
    )
    def set_date(
        date_value,
        today_nclicks,
        pmin_nclicks,
        pmax_nclicks,
        emin_nclicks,
        emax_nclicks,
    ):
        date_object = date.fromisoformat(date_value)
        active_year = date_object.year

        ctx = dash.callback_context
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger_id == ids.BTN_DATE_TODAY:
            return date.today().isoformat()
        elif trigger_id == ids.BTN_DATE_PMIN:
            raise PreventUpdate  # TODO: set to according optimal day
        elif trigger_id == ids.BTN_DATE_PMAX:
            raise PreventUpdate  # TODO: set to according optimal day
        elif trigger_id == ids.BTN_DATE_EMIN:
            raise PreventUpdate  # TODO: set to according optimal day
        elif trigger_id == ids.BTN_DATE_EMAX:
            raise PreventUpdate  # TODO: set to according optimal day
        else:
            raise PreventUpdate

    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText(
                                    [
                                        html.I(className="bi bi-calendar-week me-2"),
                                        "Select day",
                                    ]
                                ),
                                dcc.DatePickerSingle(
                                    id=ids.DATEPICKER,
                                    display_format="D. MMM YY",
                                    month_format="D. MMMM YY",
                                    placeholder="D. MMM YY",
                                    date=date.today(),
                                    persistence=True,
                                    persistence_type="local",
                                ),
                            ]
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        [
                            dbc.Button("Today", className="m-1", id=ids.BTN_DATE_TODAY),
                            dbc.Button(
                                "Min. Power Day", className="m-1", id=ids.BTN_DATE_PMIN
                            ),
                            dbc.Button(
                                "Max. Power Day", className="m-1", id=ids.BTN_DATE_PMAX
                            ),
                            dbc.Button(
                                "Min. Energy Day", className="m-1", id=ids.BTN_DATE_EMIN
                            ),
                            dbc.Button(
                                "Max. Energy Day", className="m-1", id=ids.BTN_DATE_EMAX
                            ),
                        ]
                    ),
                ]
            )
        ],
        hidden=True,
        id=ids.DIV_DATEPICKER,
    )
