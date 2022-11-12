from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from datetime import date

from . import ids


def render(app: Dash) -> html.Div:
    @app.callback(
        Output(ids.DIV_DATEPICKER, "hidden"),
        Input(ids.TABS_PLOT, "active_tab"),
    )
    def render_panels(tab):
        if tab == ids.TAB_PLOT_DAY:
            return False
        else:
            return True

    return html.Div(
        [
            dbc.InputGroup(
                [
                    dbc.InputGroupText(html.I(className="bi bi-calendar-week")),
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
        ],
        hidden=True,
        id=ids.DIV_DATEPICKER,
    )
