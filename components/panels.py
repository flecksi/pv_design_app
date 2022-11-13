import dash
from dash import Dash, html, dcc, Input, Output, State, ALL, MATCH
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import json
import numpy as np
from scipy.interpolate import interp2d
from scipy.optimize import minimize

import pandas as pd
from pydantic import BaseModel

from . import ids
from .panel import Panel
from .location import Geolocation
from datetime import date, datetime, timedelta
import pytz
import calendar

from functools import partial


class DaysOfInterest(BaseModel):
    day_Pmin: date
    day_Pmax: date
    day_Emin: date
    day_Emax: date


class AllPanels(BaseModel):
    panels: list[Panel] = []

    @property
    def ready(self) -> bool:
        return np.all([p.ready for p in self.panels])

    def get_days_of_interest(
        self,
        year: int,
        tz_str: str,
        lat: float,
        lon: float,
        ele: float,
        freq_minutes: int = 60,
    ) -> DaysOfInterest:

        tz = pytz.timezone(tz_str)

        starttime = datetime(
            year=year,
            month=1,
            day=1,
        )
        endtime = datetime(
            year=year + 1,
            month=1,
            day=1,
        )

        times = pd.date_range(
            f"{starttime:%Y-%m-%d %H:%M}",
            f"{endtime:%Y-%m-%d %H:%M}",
            freq=f"{freq_minutes}min",
            tz=tz,
        )[:-1]

        panel_powers = []
        for p in self.panels:
            if p.active and p.ready:
                panel_powers.append(
                    p.dc_power(tz_str=tz_str, lat=lat, lon=lon, ele=ele, times=times)
                )

        if len(panel_powers) == 0:
            raise PreventUpdate

        pwr = np.zeros_like(panel_powers[0])
        for pp in panel_powers:
            pwr += pp

        df_times = pd.DataFrame(
            dict(pwr=pwr, day=[t.day_of_year for t in times]), index=times
        )

        pwr_mean_W = df_times.groupby("day").mean().pwr.values
        pwr_max_W = df_times.groupby("day").max().pwr.values
        pwr_count_h = df_times.groupby("day").count().pwr.values * freq_minutes / 60
        e_kWh = pwr_mean_W * pwr_count_h / 1000

        day_in_year_pmin = int(np.argmin(pwr_max_W))
        day_in_year_pmax = int(np.argmax(pwr_max_W))
        day_in_year_emin = int(np.argmin(e_kWh))
        day_in_year_emax = int(np.argmax(e_kWh))

        return DaysOfInterest(
            day_Pmin=starttime + timedelta(days=day_in_year_pmin),
            day_Pmax=starttime + timedelta(days=day_in_year_pmax),
            day_Emin=starttime + timedelta(days=day_in_year_emin),
            day_Emax=starttime + timedelta(days=day_in_year_emax),
        )


def render(app: Dash) -> html.Div:
    @app.callback(
        Output({"type": ids.INPUT_PANEL_AZI, "index": MATCH}, "value"),
        Input({"type": ids.BTN_OPTIMIZE_AZI, "index": MATCH}, "n_clicks"),
        State({"type": ids.INPUT_PANEL_ALT, "index": MATCH}, "value"),
        State(ids.STORE_GEOLOCATION, "data"),
        State(ids.STORE_WEATHER, "data"),
        prevent_initial_call=True,
    )
    def opti_azi_callback(nclicks, tilt: float, geolocation_data: dict, weather: list):
        if geolocation_data == None:
            raise PreventUpdate
        if tilt == None or tilt == "":
            raise PreventUpdate
        geolocation = Geolocation(**geolocation_data)
        monthly_weather_factors = [1.0] * 12
        if isinstance(weather, list):
            if len(weather) == 12:
                monthly_weather_factors = weather
        (x, y, z) = geolocation.get_opti_matrix(monthly_weather_factors)
        f_2d = interp2d(x, y, z.T, kind="cubic")

        def f_opt(azi):
            return -f_2d(azi, tilt)[0]

        result = minimize(fun=f_opt, x0=180.0, bounds=[(0, 360)])
        return round(result.x[0])

    @app.callback(
        Output({"type": ids.INPUT_PANEL_ALT, "index": MATCH}, "value"),
        Input({"type": ids.BTN_OPTIMIZE_TILT, "index": MATCH}, "n_clicks"),
        State({"type": ids.INPUT_PANEL_AZI, "index": MATCH}, "value"),
        State(ids.STORE_GEOLOCATION, "data"),
        State(ids.STORE_WEATHER, "data"),
        prevent_initial_call=True,
    )
    def opti_tilt_callback(nclicks, azi: float, geolocation_data: dict, weather: list):
        if geolocation_data == None:
            raise PreventUpdate
        if azi == None or azi == "":
            raise PreventUpdate
        geolocation = Geolocation(**geolocation_data)
        monthly_weather_factors = [1.0] * 12
        if isinstance(weather, list):
            if len(weather) == 12:
                monthly_weather_factors = weather
        (x, y, z) = geolocation.get_opti_matrix(monthly_weather_factors)
        f_2d = interp2d(x, y, z.T, kind="cubic")

        def f_opt(tilt):
            return -f_2d(azi, tilt)[0]

        result = minimize(fun=f_opt, x0=45.0, bounds=[(0, 90)])
        return round(result.x[0])

    @app.callback(
        Output(ids.STORE_PANELS, "data"),
        State(ids.STORE_PANELS, "data"),
        Input(ids.BTN_ADD_PANEL, "n_clicks"),
        Input(ids.BTN_CLEAR_PANELS, "n_clicks"),
        Input({"type": ids.CHECKBOX_PANEL_ACTIVE, "index": ALL}, "value"),
        Input({"type": ids.BTN_DELETE_PANEL, "index": ALL}, "n_clicks"),
        Input({"type": ids.INPUT_PANEL_LABEL, "index": ALL}, "value"),
        Input({"type": ids.INPUT_PANEL_AZI, "index": ALL}, "value"),
        Input({"type": ids.INPUT_PANEL_ALT, "index": ALL}, "value"),
        Input({"type": ids.INPUT_PANEL_SIZE, "index": ALL}, "value"),
        Input({"type": ids.INPUT_PANEL_COLOR, "index": ALL}, "value"),
        Input({"type": ids.INPUT_PANEL_SPECPWR, "index": ALL}, "value"),
        prevent_initial_call=True,
    )
    def modify_panels(
        data: dict,
        add_nclicks: int,
        clear_nclicks: int,
        active_values,
        delete_panel_nclicks: int,
        label_values,
        azi_values,
        alt_values,
        size_values,
        color_values,
        pdc0_values,
    ):
        ctx = dash.callback_context
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if data == None:
            data = {}
        allpanels = AllPanels(**data)
        if trigger_id == ids.BTN_ADD_PANEL:
            allpanels.panels.append(Panel())
            return allpanels.dict()
        elif trigger_id == ids.BTN_CLEAR_PANELS:
            return {}
        else:
            trigger = json.loads(trigger_id)
            if "index" in trigger:
                i = trigger["index"]
            if "type" in trigger:
                if trigger["type"] == ids.BTN_DELETE_PANEL:
                    if delete_panel_nclicks[i] is not None:
                        allpanels.panels.pop(i)
                else:
                    allpanels.panels[i].active = active_values[i]
                    allpanels.panels[i].label = label_values[i]
                    allpanels.panels[i].azimuth_deg = azi_values[i]
                    allpanels.panels[i].altitude_deg = alt_values[i]
                    allpanels.panels[i].size_m2 = size_values[i]
                    allpanels.panels[i].color = color_values[i]
                    allpanels.panels[i].pdc0_Wpm2 = pdc0_values[i]

                return allpanels.dict()

            raise PreventUpdate

    @app.callback(
        Output(ids.DIV_PANEL_LIST, "children"),
        Input(ids.STORE_PANELS, "data"),
    )
    def render_panels(data: dict):
        if data == None:
            data = {}
        allpanels = AllPanels(**data)

        return [p.render_as_card(app, i) for i, p in enumerate(allpanels.panels)]

    return html.Div(
        [
            dcc.Store(id=ids.STORE_PANELS, storage_type="local"),
            html.H4([html.I(className="bi bi-microsoft me-2"), "Photovoltaic Panels"]),
            dbc.Row(
                dbc.Col(
                    [
                        dbc.Button(
                            [
                                html.I(className="bi bi-plus-circle me-2"),
                                "Add Panel",
                            ],
                            className="m-1",
                            id=ids.BTN_ADD_PANEL,
                        ),
                        dbc.Button(
                            [
                                html.I(className="bi bi-trash me-2"),
                                "Clear All",
                            ],
                            className="m-1",
                            id=ids.BTN_CLEAR_PANELS,
                        ),
                    ]
                )
            ),
            html.Div(["Panels go here..."], id=ids.DIV_PANEL_LIST),
        ]
    )
