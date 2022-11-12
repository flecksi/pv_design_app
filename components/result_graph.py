from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

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


def create_day_figure(
    geolocation: Geolocation,
    allpanels: AllPanels,
    thedate: date,
    freq_minutes: int = 30,
) -> go.Figure:
    tz = pytz.timezone(geolocation.tz_str)

    starttime = datetime(
        year=thedate.year,
        month=thedate.month,
        day=thedate.day,
        hour=0,
        minute=0,
        second=0,
    )
    endtime = datetime(
        year=thedate.year,
        month=thedate.month,
        day=thedate.day,
        hour=23,
        minute=59,
        second=59,
    )

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
        # vertical_spacing=0.06,
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
                p.label if (p.label is not None and p.label != "") else f"{i+1}.Panel"
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

    fig.update_layout(
        hovermode="x unified",
        title=f"DC power and energy in one day ({thedate.day}.{thedate.month}.{thedate.year}) - best case (not considering weather)",
        yaxis1=dict(title="Power [W]"),
        yaxis2=dict(title="Energy [kWh]"),
    )
    style_figure(fig=fig)
    return fig


def create_annual_figure(
    geolocation: Geolocation,
    allpanels: AllPanels,
    thedate: date,
    monthly_weather_factors: list[float],
    freq_minutes: int = 60,
) -> tuple[go.Figure, pd.DataFrame]:
    tz = pytz.timezone(geolocation.tz_str)

    panel_energy_dfs = [
        p.monthly_energy(
            loc=geolocation,
            monthly_weather_factors=monthly_weather_factors,
            year=thedate.year,
            label=f"p_{i}",
        )
        if p.active and p.ready
        else None
        for i, p in enumerate(allpanels.panels)
    ]

    result = pd.concat(panel_energy_dfs, axis=1)

    fig = go.Figure()
    for col in result.columns:
        i = int(col.split("_")[1])
        p = allpanels.panels[i]
        label = p.label if (p.label is not None and p.label != "") else f"{i+1}.Panel"
        fig.add_trace(
            go.Bar(
                name=f"{label}",  # ({result[col].sum():.1f} kWh/Y)",
                x=result.index,
                y=result[col],
                hovertemplate="%{x}: %{y:.1f} kWh",  #%{_xother}",
                # hovertemplate="%{y:.1f} kWh%{_xother}",
                marker_color=p.color,
            )
        )
        result.rename(columns={f"p_{i}": label}, inplace=True)

    fig.add_trace(
        go.Bar(
            name=f"<b>total",  # ({result.sum().sum():.1f} kWh/Y)</b>",
            x=result.index,
            y=result.sum(axis=1),
            hovertemplate="%{x}: %{y:.1f} kWh",  #%{_xother}",
            # hovertemplate="%{y:.1f} kWh%{_xother}",
            marker_color="black",
        )
    )

    fig.update_layout(
        # barmode='stack',
        barmode="group",
        # margin=dict(l=10, r=10, t=50, b=5),
        title=f"Monthly energy yields within one year ({thedate.year})",
        yaxis_title="Energy [kWh]",
    )
    style_figure(fig=fig)
    # fig.update_layout(margin=dict(l=100, r=115, t=50, b=5))

    return fig, result


def style_figure(fig: go.Figure):
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="DarkGrey",
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="black",
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="DarkGrey",
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="black",
    )
    fig.update_layout(
        margin=dict(l=5, r=5, t=50, b=5),
        legend=dict(
            x=0.0,
            y=1.0,
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="rgba(255, 255, 255, 1)",
        ),
    )


def render(app: Dash) -> html.Div:
    @app.callback(
        Output(ids.DIV_GRAPH, "children"),
        Input(ids.STORE_PANELS, "data"),
        Input(ids.STORE_GEOLOCATION, "data"),
        Input(ids.STORE_WEATHER, "data"),
        Input(ids.DATEPICKER, "date"),
        Input(ids.TABS_PLOT, "active_tab"),
    )
    def render_graph(
        panel_data: dict, geolocation_data: dict, weather: list, date_value, tab
    ):
        if panel_data == None:
            panel_data = {}
        if geolocation_data == None:
            geolocation_data = {}

        allpanels = AllPanels(**panel_data)
        geolocation = Geolocation(**geolocation_data)
        date_object = date.fromisoformat(date_value)
        # year=date_object.year
        # month=date_object.month
        # day=date_object.day

        monthly_weather_factors = [1.0] * 12
        if isinstance(weather, list):
            if len(weather) == 12:
                monthly_weather_factors = weather
        if geolocation.ready == False:
            return html.H4("⇧ 🚫 Please define a location!")
        if len(allpanels.panels) == 0:
            return html.H4("⇦ 🚫 Please add a new panel!")
        if len([p for p in allpanels.panels if p.active == True]) == 0:
            return html.H4("⇦ 🚫 Please activate at least one panel!")
        if allpanels.ready == False:
            return html.H4("⇦ 🚫 At least one panel is not parametrized!")

        if tab == ids.TAB_PLOT_DAY:
            fig = create_day_figure(
                geolocation=geolocation, allpanels=allpanels, thedate=date_object
            )
            return dcc.Graph(figure=fig, responsive=True, style={"height": "70vh"})

        elif tab == ids.TAB_PLOT_YEAR:
            fig, df_annual = create_annual_figure(
                geolocation=geolocation,
                monthly_weather_factors=monthly_weather_factors,
                allpanels=allpanels,
                thedate=date_object,
            )
            df_annual = df_annual.T
            df_annual["Total"] = df_annual.sum(axis=1)
            totals_dict = df_annual.sum(axis=0).to_dict()
            df_annual = pd.concat(
                [df_annual, pd.DataFrame(totals_dict, index=["Total"])], axis=0
            )

            for col in df_annual:
                for i in range(len(df_annual)):
                    df_annual[col].iloc[i] = round(
                        df_annual[col].iloc[i], 1
                    )  # f"{round(df_annual[col].iloc[i], 1):.01f}"
            df_annual.index.set_names("Panel", inplace=True)

            table = dbc.Table.from_dataframe(
                df_annual, striped=True, bordered=True, hover=False, index=True
            )

            return [
                dcc.Graph(figure=fig, responsive=True, style={"height": "70vh"}),
                table,
            ]

        else:
            return html.H4("Something went horribly wrong!")

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
