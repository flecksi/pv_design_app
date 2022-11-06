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
from . import ids

tf = TimezoneFinder()  # reuse


class Geolocation(BaseModel):
    lat: float = None
    lon: float = None
    ele: float = None
    tz_str: str = None
    year: int = None
    month: int = None
    day: int = None
    address: str = None

    @property
    def ready(self) -> bool:
        return (
            isinstance(self.lat, float)
            and isinstance(self.lon, float)
            and isinstance(self.ele, float)
            and isinstance(self.tz_str, str)
            and isinstance(self.year, int)
            and isinstance(self.month, int)
            and isinstance(self.day, int)
        )


def render(app: Dash) -> html.Div:
    @app.callback(
        [
            Output(ids.STORE_GEOLOCATION, "data"),
            Output(ids.INPUT_LOCATION, "valid"),
            Output(ids.INPUT_LOCATION, "invalid"),
        ],
        [
            Input(ids.INPUT_DATE, "date"),
            Input(ids.INPUT_LOCATION, "value"),
        ],
    )
    def update_geostore(date_value, location_str):
        tz_str = None
        tz = None
        date_object = date.fromisoformat(date_value)

        if location_str is not None and location_str != "":
            geolocator = Nominatim(user_agent="myGeocoder")
            location = geolocator.geocode(location_str, timeout=2)
            if location is None:
                return ({}, False, True)
            lat = location.latitude
            lon = location.longitude

            tz_str = tf.timezone_at(lng=lon, lat=lat)

            # lookup elevation for location, https://www.open-elevation.com
            ele_response = requests.get(
                f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
            )
            ele = ele_response.json()["results"][0]["elevation"]

            return (
                Geolocation(
                    lat=lat,
                    lon=lon,
                    ele=ele,
                    tz_str=tz_str,
                    year=date_object.year,
                    month=date_object.month,
                    day=date_object.day,
                    address=location.address,
                ).dict(),
                True,
                False,
            )
        return ({}, False, True)

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

    return html.Div(
        [
            dcc.Store(id=ids.STORE_GEOLOCATION, storage_type="local"),
            dbc.Card(
                [
                    dbc.CardHeader(
                        [
                            html.H4(
                                [
                                    html.I(className="bi bi-globe"),
                                    " + ",
                                    html.I(className="bi bi-calendar-week me-2"),
                                    " Location & Date",
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
                                                dbc.InputGroupText(
                                                    [
                                                        html.I(
                                                            className="bi bi-globe"  # me-2"
                                                        ),
                                                    ]
                                                ),
                                                dbc.Input(
                                                    id=ids.INPUT_LOCATION,
                                                    type="text",
                                                    placeholder="Enter address here and press enter",
                                                    persistence=True,
                                                    debounce=True,
                                                ),
                                            ]
                                        )
                                    ),
                                    dbc.Col(
                                        dbc.InputGroup(
                                            [
                                                dbc.InputGroupText(
                                                    html.I(
                                                        className="bi bi-calendar-week"
                                                    )
                                                ),
                                                dcc.DatePickerSingle(
                                                    id=ids.INPUT_DATE,
                                                    display_format="D. MMM YYYY",
                                                    month_format="D. MMMM YYYY",
                                                    placeholder="D. MMM YY",
                                                    date=date.today(),
                                                    persistence=True,
                                                    persistence_type="local",
                                                ),
                                            ]
                                        ),
                                        width="auto",
                                    ),
                                ]
                            ),
                            html.P(
                                "Resolved City/Country and Timezone",
                                id=ids.TEXT_GEOLOC,
                                className="card-text",
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
    )
