import dash
import gunicorn

from dash import dcc, html, no_update
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

import dash_bootstrap_components as dbc

from components import layout

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.icons.BOOTSTRAP,
        dbc.themes.BOOTSTRAP,
    ],  # CYBORG BOOTSTRAP SLATE MORPH FLATLY
)
app.title = "PV Design"
app.layout = layout.create_layout(app)

server = app.server  # for gunicorn: run "gunicorn app:server"

if __name__ == "__main__":
    app.run_server(debug=True, port=8888)
