import dash
from dash import Dash, html, dcc, Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from pydantic import BaseModel
import json
import numpy as np

from . import ids
from .panel import Panel


class AllPanels(BaseModel):
    panels: list[Panel] = []

    @property
    def ready(self) -> bool:
        return np.all([p.ready for p in self.panels])


def render(app: Dash) -> html.Div:
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
