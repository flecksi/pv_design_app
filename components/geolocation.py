import dash
from dash import Dash, html, dcc, Input, Output, State, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import requests
import pytz
from datetime import date, datetime
from pydantic import BaseModel
import numpy as np

from . import ids
from .location import Geolocation
from .panel import Panel

tf = TimezoneFinder()  # reuse


def render(app: Dash) -> html.Div:
    @app.callback(
        [
            Output(ids.STORE_GEOLOCATION, "data"),
            Output(ids.INPUT_LOCATION, "valid"),
            Output(ids.INPUT_LOCATION, "invalid"),
            Output(ids.COLLAPSE_MAIN_APP, "is_open"),
        ],
        [
            Input(ids.INPUT_LOCATION, "value"),
        ],
    )
    def update_geostore(location_str):
        tz_str = None
        tz = None

        if location_str is not None and location_str != "":
            geolocator = Nominatim(user_agent="myGeocoder")
            location = geolocator.geocode(location_str, timeout=2)
            if location is None:
                return ({}, False, True, False)
            lat = location.latitude
            lon = location.longitude

            tz_str = tf.timezone_at(lng=lon, lat=lat)

            # lookup elevation for location, https://www.open-elevation.com
            ele_response = requests.get(
                f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
            )
            ele = ele_response.json()["results"][0]["elevation"]

            geolocation = Geolocation(
                lat=lat,
                lon=lon,
                ele=ele,
                tz_str=tz_str,
                address=location.address,
            )

            azi_vect = np.linspace(0, 360, 8, endpoint=False)
            tilt_vect = np.linspace(0, 90, 7, endpoint=True)
            opti_angle_matrix = np.zeros((8, 7, 12))

            for i, azi in enumerate(azi_vect):
                for j, tilt in enumerate(tilt_vect):
                    p = Panel(
                        label="opti_panel",
                        size_m2=1.0,
                        azimuth_deg=azi,
                        altitude_deg=tilt,
                    )
                    df = p.monthly_energy(
                        loc=geolocation,
                        monthly_weather_factors=[1.0] * 12,
                        year=date.today().year,
                        label="o",
                    )
                    opti_angle_matrix[i, j, :] = df["o"].values

            geolocation.opti_angle_matrix = list(opti_angle_matrix)
            geolocation.opti_azi_vect = list(azi_vect)
            geolocation.opti_tilt_vect = list(tilt_vect)
            return (geolocation.dict(), True, False, True)
        return ({}, False, True, False)

    @app.callback(
        Output(ids.TEXT_GEOLOC, "children"),
        Input(ids.STORE_GEOLOCATION, "data"),
    )
    def update_geotext(data: dict):
        if data == None:
            data = {}

        loc = Geolocation(**data)

        if loc.ready:
            tz = pytz.timezone(loc.tz_str)
            now = datetime.now(tz)
            return [
                dbc.Row(
                    f"{loc.address}, local time={now:%H:%M:%S}, timezone={loc.tz_str}"
                ),
                dbc.Row(f"Lat={loc.lat}°, Lon={loc.lon}°, Ele={loc.ele}m"),
            ]

        else:
            return "no valid coordinates"

    return dcc.Loading(
        html.Div(
            [
                dcc.Store(id=ids.STORE_GEOLOCATION, storage_type="local"),
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                html.H4(
                                    [
                                        html.I(
                                            className="bi bi-geo-alt me-2"
                                        ),  # bi-globe
                                        " Location",
                                    ]
                                ),
                            ]
                        ),
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.InputGroup(
                                                [
                                                    # dbc.InputGroupText(
                                                    #     [
                                                    #         html.I(
                                                    #             className="bi bi-globe"  # me-2"
                                                    #         ),
                                                    #     ]
                                                    # ),
                                                    dbc.Input(
                                                        id=ids.INPUT_LOCATION,
                                                        type="text",
                                                        placeholder="Enter address here and press enter",
                                                        persistence=True,
                                                        debounce=True,
                                                    ),
                                                ]
                                            )
                                        )
                                    ]
                                ),
                                dbc.Row(
                                    dbc.Col(
                                        html.P(
                                            "Resolved City/Country and Timezone",
                                            id=ids.TEXT_GEOLOC,
                                            className="card-text",
                                        )
                                    )
                                ),
                            ]
                        ),
                    ],
                    color="success",
                    inverse=True,
                    className="shadow mb-3"
                    # style={"width": "18rem"},
                ),
            ]
        ),
        # debug=True,
        fullscreen=True,
    )
