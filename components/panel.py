from dash import Dash, html
import dash_bootstrap_components as dbc
from pydantic import BaseModel
import pytz
import calendar
from datetime import datetime

import numpy as np
import pandas as pd
from pvlib import pvsystem, modelchain, location


from . import ids
from .geolocation import Geolocation

PDC0_DEFAULT = round(5000 / 35, 2)


class Panel(BaseModel):
    label: str = None
    size_m2: float = None
    azimuth_deg: float = None
    altitude_deg: float = None
    active: bool = True
    color: str = None
    pdc0_Wpm2: float = None

    @property
    def ready(self) -> bool:
        return (
            isinstance(self.size_m2, float)
            and isinstance(self.altitude_deg, float)
            and isinstance(self.azimuth_deg, float)
            and isinstance(self.size_m2, float)
        ) or self.active == False

    def dc_power(self, loc: Geolocation, times: pd.DatetimeIndex) -> np.ndarray:
        tz = pytz.timezone(loc.tz_str)

        pdc0_specific = (
            self.pdc0_Wpm2 if isinstance(self.pdc0_Wpm2, float) else PDC0_DEFAULT
        )
        pdc0 = self.size_m2 * pdc0_specific

        array_kwargs = dict(
            module_parameters=dict(pdc0=pdc0, gamma_pdc=-0.004),
            temperature_model_parameters=dict(a=-3.56, b=-0.075, deltaT=3),
        )

        arrays = [
            pvsystem.Array(
                pvsystem.FixedMount(
                    surface_tilt=self.altitude_deg, surface_azimuth=self.azimuth_deg
                ),
                name="MyArray",
                **array_kwargs,
            )
        ]
        loc = location.Location(
            latitude=loc.lat, longitude=loc.lon, tz=tz, altitude=loc.ele
        )
        system = pvsystem.PVSystem(
            arrays=arrays, inverter_parameters=dict(pdc0=pdc0, eta_inv_nom=0.97)
        )
        mc = modelchain.ModelChain(
            system, loc, aoi_model="physical", spectral_model="no_loss"
        )

        clearsky = loc.get_clearsky(times, model="simplified_solis")
        mc.run_model(clearsky)
        return mc.results.dc.values

    def monthly_energy(
        self, loc: Geolocation, year: int, label: str, freq_minutes: int = 60
    ) -> pd.DataFrame:

        tz = pytz.timezone(loc.tz_str)

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

        pwr = self.dc_power(loc=loc, times=times)

        df_times = pd.DataFrame(
            dict(pwr=pwr, month=[t.month for t in times]), index=times
        )

        pwr_mean_W = df_times.groupby("month").mean().pwr.values
        pwr_count_h = df_times.groupby("month").count().pwr.values * freq_minutes / 60
        e_kWh = pwr_mean_W * pwr_count_h / 1000

        months = [calendar.month_abbr[m + 1] for m in range(12)]

        df_result = pd.DataFrame(data={f"{label}": e_kWh}, index=months)
        return df_result

    def render_as_card(self, app: Dash, i: int) -> dbc.Card:
        return dbc.Card(
            [
                dbc.CardHeader(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.InputGroup(
                                        [
                                            dbc.InputGroupText(
                                                f"{i+1}.Panel",
                                            ),
                                            dbc.Input(
                                                value=self.label,
                                                type="text",
                                                placeholder="enter a name...",
                                                id=dict(
                                                    type=ids.INPUT_PANEL_LABEL, index=i
                                                ),
                                            ),
                                            dbc.Input(
                                                id=dict(
                                                    type=ids.INPUT_PANEL_COLOR, index=i
                                                ),
                                                type="color",
                                                value=self.color
                                                if self.color and self.color != ""
                                                else "#FF0000",
                                                style={
                                                    # "width": 10,
                                                    "height": "auto",
                                                },
                                            ),
                                            dbc.InputGroupText(
                                                dbc.Checkbox(
                                                    value=self.active,
                                                    label="Active",
                                                    id=dict(
                                                        type=ids.CHECKBOX_PANEL_ACTIVE,
                                                        index=i,
                                                    ),
                                                ),
                                            ),
                                            dbc.Button(
                                                html.I(className="bi bi-trash"),
                                                id=dict(
                                                    type=ids.BTN_DELETE_PANEL, index=i
                                                ),
                                            ),
                                            dbc.Tooltip(
                                                "Delete this panel",
                                                target=dict(
                                                    type=ids.BTN_DELETE_PANEL, index=i
                                                ),
                                            ),
                                        ]
                                    ),
                                    width=True,
                                ),
                            ]
                        ),
                    ]
                ),
                dbc.CardBody(
                    [
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Azimuth Angle"),
                                dbc.Input(
                                    value=self.azimuth_deg,
                                    type="number",
                                    min=0,
                                    max=360,
                                    required=True,
                                    inputmode="numeric",
                                    placeholder="0°:N, 90°:E, 180°:S, 270°:W",
                                    id=dict(type=ids.INPUT_PANEL_AZI, index=i),
                                ),
                                dbc.InputGroupText("deg"),
                            ]
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Tilt Angle"),
                                dbc.Input(
                                    value=self.altitude_deg,
                                    type="number",
                                    min=0,
                                    max=90,
                                    required=True,
                                    placeholder="0°:facing up, 90°:facing sideways",
                                    inputmode="numeric",
                                    id=dict(type=ids.INPUT_PANEL_ALT, index=i),
                                ),
                                dbc.InputGroupText("deg"),
                            ]
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Size"),
                                dbc.Input(
                                    value=self.size_m2,
                                    type="number",
                                    min=0,
                                    # max=90,
                                    required=True,
                                    inputmode="numeric",
                                    placeholder="effective PV area",
                                    id=dict(type=ids.INPUT_PANEL_SIZE, index=i),
                                ),
                                dbc.InputGroupText("m²"),
                            ]
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("PDC0"),
                                dbc.Input(
                                    value=self.pdc0_Wpm2,
                                    type="number",
                                    min=0,
                                    # max=90,
                                    # required=True,
                                    inputmode="numeric",
                                    placeholder=PDC0_DEFAULT,  # "specific. power/area",
                                    id=dict(
                                        type=ids.INPUT_PANEL_SPECPWR,
                                        index=i,
                                    ),
                                ),
                                dbc.InputGroupText("W/m²"),
                            ]
                        ),
                        dbc.Tooltip(
                            "Specifc DC Power output per m² under best conditions",
                            target=dict(type=ids.INPUT_PANEL_SPECPWR, index=i),
                        ),
                    ]
                ),
            ],
            className="shadow mb-3",
            color=self.color,  # "warning",
            inverse=True,
        )
