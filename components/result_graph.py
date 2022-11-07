from dash import Dash, html, dcc, Input, Output

from . import ids
from .panels import AllPanels
from .geolocation import Geolocation

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pytz
from datetime import date, datetime

import numpy as np
import pandas as pd
from scipy.integrate import cumtrapz


def render(app: Dash) -> html.Div:
    @app.callback(
        Output(ids.DIV_GRAPH, "children"),
        Input(ids.STORE_PANELS, "data"),
        Input(ids.STORE_GEOLOCATION, "data"),
    )
    def render_panels(panel_data: dict, geolocation_data: dict):
        if panel_data == None:
            panel_data = {}
        if geolocation_data == None:
            geolocation_data = {}

        allpanels = AllPanels(**panel_data)
        geolocation = Geolocation(**geolocation_data)

        if geolocation.ready == False:
            return html.H4("⇧ 🚫 Please define a location!")
        if len(allpanels.panels) == 0:
            return html.H4("⇦ 🚫 Please add a new panel!")
        if len([p for p in allpanels.panels if p.active == True]) == 0:
            return html.H4("⇦ 🚫 Please activate at least one panel!")
        if allpanels.ready == False:
            return html.H4("⇦ 🚫 At least one panel is not parametrized!")

        tz = pytz.timezone(geolocation.tz_str)

        starttime = datetime(
            year=geolocation.year,
            month=geolocation.month,
            day=geolocation.day,
            hour=0,
            minute=0,
            second=0,
        )
        endtime = datetime(
            year=geolocation.year,
            month=geolocation.month,
            day=geolocation.day,
            hour=23,
            minute=59,
            second=59,
        )

        freq_minutes = 30
        times = pd.date_range(
            f"{starttime:%Y-%m-%d %H:%M}",
            f"{endtime:%Y-%m-%d %H:%M}",
            freq=f"{freq_minutes}min",
            tz=tz,
        )

        dc_powers_W = [
            p.dc_power(loc=geolocation, times=times) if p.active and p.ready else None
            for p in allpanels.panels
        ]

        # fig = go.Figure()
        fig = make_subplots(
            rows=1,
            cols=1,
            # subplot_titles=["Max Yield Day", "Energy over the Year"],
            vertical_spacing=0.06,
            specs=[[{"secondary_y": True}]],
        )
        pwr_sum_W = np.zeros_like(dc_powers_W[0])
        e_sum_kWh = np.zeros_like(dc_powers_W[0])
        for i, p in enumerate(allpanels.panels):
            if p.active:
                energy_kWh = (
                    cumtrapz(dc_powers_W[i], initial=dc_powers_W[i][0] / 1000)
                    / 1000
                    * freq_minutes
                    / 60
                )
                pwr_sum_W = pwr_sum_W + dc_powers_W[i]
                e_sum_kWh = e_sum_kWh + energy_kWh
                label = (
                    p.label
                    if (p.label is not None and p.label != "")
                    else f"{i+1}.Panel"
                )
                fig.add_trace(
                    go.Scatter(
                        x=times,
                        y=dc_powers_W[i],
                        name=f"Pwr {label} [W]",
                        hovertemplate="%{y:.1f}%{_xother}",
                        line=dict(width=3, color=p.color),
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=times,
                        y=energy_kWh,
                        name=f"Energy {label} [kWh]",
                        hovertemplate="%{y:.2f}%{_xother}",
                        line=dict(width=3, dash="dot", color=p.color),
                    ),
                    secondary_y=True,
                )

        fig.add_trace(
            go.Scatter(
                x=times,
                y=pwr_sum_W,
                name="Pwr Sum [W]",
                hovertemplate="%{y:.1f}%{_xother}",
                line=dict(color="black", width=4),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=times,
                y=e_sum_kWh,
                name="Energy Sum [kWh]",
                hovertemplate="%{y:.2f}%{_xother}",
                line=dict(color="black", width=4, dash="dot"),
            ),
            secondary_y=True,
        )
        # fig.add_trace(
        #     go.Bar(
        #         x=["January", "February", "March", "April", "May"], y=[6, 2, 3, 7, 1]
        #     ),
        #     row=2,
        #     col=1,
        # )
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="DarkGrey",
            # showline=True,
            # linecolor="black",
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor="black",
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="DarkGrey",
            # showline=True,
            # linecolor="black",
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor="black",
        )
        fig.update_layout(
            autosize=True,
            # height=800,
            # width="90vh",
            margin=dict(l=5, r=5, t=50, b=5),
            hovermode="x unified",
            # plot_bgcolor="white",
            title=f"Optimal DC power and energy in one day ({geolocation.day}.{geolocation.month}.{geolocation.year})",
            yaxis1=dict(title="Power [W]"),
            yaxis2=dict(title="Energy [kWh]"),
        )
        return dcc.Graph(figure=fig, responsive=True, style={"height": "70vh"})

    return dcc.Loading(
        html.Div(
            "Graph goes here",
            id=ids.DIV_GRAPH,
            # style=dict(background="red"),
        ),
        type="default",
        # fullscreen=True,
        debug=True,
    )  #'graph', 'cube', 'circle', 'dot', 'default
