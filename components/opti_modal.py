import dash
from dash import Dash, html, dcc, Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from pydantic import BaseModel
import json
import numpy as np

from . import ids


def render(app: Dash) -> html.Div:
    @app.callback(
        Output(ids.MODAL_OPTI, "is_open"),
        Output(ids.DIV_OPTI_GRAPH, "children"),
        State(ids.STORE_GEOLOCATION, "data"),
        Input(ids.BTN_OPTIMIZE_ANGLES, "n_clicks"),
        prevent_initial_call=True,
    )
    def open_modal(geolocation: dict, nclicks):
        fig = go.Figure()
        fig.add_trace(
            go.Contour(
                x=[0, 180, 360],
                y=[0, 34, 90],
                z=[[1, 30, 3], [30, 100, 30], [7, 30, 9]],
                contours=dict(
                    coloring="heatmap",
                    showlabels=True,  # show labels on contours
                    labelfont=dict(  # label font properties
                        size=16,
                        # color="white",
                    ),
                ),
            )
        )
        fig.add_vline(
            x=180,
            line=dict(color="black", width=2, dash="dash"),
            annotation_text="Optimal Azimuth=180°",
            annotation_position="top left",
            annotation=dict(font_size=20, font_color="black"),
        )
        fig.add_hline(
            y=34,
            line=dict(color="black", width=2, dash="dash"),
            annotation_text="Optimal Tilt=34°",
            annotation_position="top left",
            annotation=dict(font_size=20, font_color="black"),
        )
        fig.update_layout(
            margin=dict(l=5, r=5, t=5, b=5),
            yaxis_title="Tilt Angle [deg]",
            xaxis_title="Azimuth Angle [deg]",
            xaxis=dict(dtick=45),
            yaxis=dict(dtick=10),
        )
        return True, dcc.Graph(figure=fig, responsive=True, style={"height": "80vh"})

    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle("Annual yield in percent of optimal value (DUMMY DATA)")
            ),
            dbc.ModalBody("An extra large modal.", id=ids.DIV_OPTI_GRAPH),
        ],
        id=ids.MODAL_OPTI,
        size="xl",
        is_open=False,
    )
