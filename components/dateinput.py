import dash
from dash import Dash, html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from datetime import date

from . import ids

from .panels import AllPanels
from .geolocation import Geolocation


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
        State(ids.STORE_PANELS, "data"),
        State(ids.STORE_GEOLOCATION, "data"),
        Input(ids.BTN_DATE_TODAY, "n_clicks"),
        Input(ids.BTN_DATE_PMIN, "n_clicks"),
        Input(ids.BTN_DATE_PMAX, "n_clicks"),
        Input(ids.BTN_DATE_EMIN, "n_clicks"),
        Input(ids.BTN_DATE_EMAX, "n_clicks"),
        prevent_initial_call=True,
    )
    def set_date(
        date_value,
        panel_data: dict,
        geolocation_data: dict,
        today_nclicks,
        pmin_nclicks,
        pmax_nclicks,
        emin_nclicks,
        emax_nclicks,
    ):
        ctx = dash.callback_context
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger_id == ids.BTN_DATE_TODAY:
            return date.today().isoformat()

        if panel_data == None:
            raise PreventUpdate
        if geolocation_data == None:
            raise PreventUpdate

        allpanels = AllPanels(**panel_data)
        geolocation = Geolocation(**geolocation_data)
        date_object = date.fromisoformat(date_value)
        active_year = date_object.year

        daysofinterest = allpanels.get_days_of_interest(
            year=active_year,
            tz_str=geolocation.tz_str,
            lat=geolocation.lat,
            lon=geolocation.lon,
            ele=geolocation.ele,
            freq_minutes=30,
        )

        if trigger_id == ids.BTN_DATE_PMIN:
            return daysofinterest.day_Pmin.isoformat()
        elif trigger_id == ids.BTN_DATE_PMAX:
            return daysofinterest.day_Pmax.isoformat()
        elif trigger_id == ids.BTN_DATE_EMIN:
            return daysofinterest.day_Emin.isoformat()
        elif trigger_id == ids.BTN_DATE_EMAX:
            return daysofinterest.day_Emax.isoformat()
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
