# -*- coding: utf-8 -*-
import math
import json

import pandas as pd
import flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly import graph_objs as go

from app import app, indicator, millify, df_to_table
import data_manager as dm

colors = {"background": "#F3F6FA", "background_div": "white"}
def modal():
    contacts["Name"] = (
        contacts["Salutation"]
        + " "
        + contacts["FirstName"]
        + " "
        + contacts["LastName"]
    )
    return html.Div(
        html.Div(
            [
                html.Div(
                    [
                        # modal header
                        html.Div(
                            [
                                html.Span(
                                    "New Case",
                                    style={
                                        "color": "#506784",
                                        "fontWeight": "bold",
                                        "fontSize": "20",
                                    },
                                ),
                                html.Span(
                                    "×",
                                    id="cases_modal_close",
                                    n_clicks=0,
                                    style={
                                        "float": "right",
                                        "cursor": "pointer",
                                        "marginTop": "0",
                                        "marginBottom": "17",
                                    },
                                ),
                            ],
                            className="row",
                            style={"borderBottom": "1px solid #C8D4E3"},
                        ),

                        # modal form
                        html.Div(
                            [

                                # left Div
                                html.Div(
                                    [
                                        html.P(
                                            "Account name",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        html.Div(
                                            dcc.Dropdown(
                                                id="new_case_account",
                                                options=[
                                                    {
                                                        "label": row["Name"],
                                                        "value": row["Id"],
                                                    }
                                                    for index, row in accounts.iterrows()
                                                ],
                                                clearable=False,
                                                value=accounts.iloc[0].Id,
                                            )
                                        ),
                                        html.P(
                                            "Priority",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="new_case_priority",
                                            options=[
                                                {"label": "High", "value": "High"},
                                                {"label": "Medium", "value": "Medium"},
                                                {"label": "Low", "value": "Low"},
                                            ],
                                            value="Medium",
                                            clearable=False,
                                        ),
                                        html.P(
                                            "Origin",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="new_case_origin",
                                            options=[
                                                {"label": "Phone", "value": "Phone"},
                                                {"label": "Web", "value": "Web"},
                                                {"label": "Email", "value": "Email"},
                                            ],
                                            value="Phone",
                                            clearable=False,
                                        ),
                                        html.P(
                                            "Reason",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="new_case_reason",
                                            options=[
                                                {
                                                    "label": "Installation",
                                                    "value": "Installation",
                                                },
                                                {
                                                    "label": "Equipment Complexity",
                                                    "value": "Equipment Complexity",
                                                },
                                                {
                                                    "label": "Performance",
                                                    "value": "Performance",
                                                },
                                                {
                                                    "label": "Breakdown",
                                                    "value": "Breakdown",
                                                },
                                                {
                                                    "label": "Equipment Design",
                                                    "value": "Equipment Design",
                                                },
                                                {
                                                    "label": "Feedback",
                                                    "value": "Feedback",
                                                },
                                                {"label": "Other", "value": "Other"},
                                            ],
                                            value="Installation",
                                            clearable=False,
                                        ),
                                        html.P(
                                            "Subject",
                                            style={
                                                "float": "left",
                                                "marginTop": "4",
                                                "marginBottom": "2",
                                            },
                                            className="row",
                                        ),
                                        dcc.Input(
                                            id="new_case_subject",
                                            placeholder="The Subject of the case",
                                            type="text",
                                            value="",
                                            style={"width": "100%"},
                                        ),
                                    ],
                                    className="six columns",
                                    style={"paddingRight": "15"},
                                ),


                                # right Div
                                html.Div(
                                    [
                                        html.P(
                                            "Contact name",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        html.Div(
                                            dcc.Dropdown(
                                                id="new_case_contact",
                                                options=[
                                                    {
                                                        "label": row["Name"],
                                                        "value": row["Id"],
                                                    }
                                                    for index, row in contacts.iterrows()
                                                ],
                                                clearable=False,
                                                value=contacts.iloc[0].Id,
                                            )
                                        ),
                                        html.P(
                                            "Type",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="new_case_type",
                                            options=[
                                                {
                                                    "label": "Electrical",
                                                    "value": "Electrical",
                                                },
                                                {
                                                    "label": "Mechanical",
                                                    "value": "Mechanical",
                                                },
                                                {
                                                    "label": "Electronic",
                                                    "value": "Electronic",
                                                },
                                                {
                                                    "label": "Structural",
                                                    "value": "Structural",
                                                },
                                                {"label": "Other", "value": "Other"},
                                            ],
                                            value="Electrical",
                                        ),
                                        html.P(
                                            "Status",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="new_case_status",
                                            options=[
                                                {"label": "New", "value": "New"},
                                                {
                                                    "label": "Working",
                                                    "value": "Working",
                                                },
                                                {
                                                    "label": "Escalated",
                                                    "value": "Escalated",
                                                },
                                                {"label": "Closed", "value": "Closed"},
                                            ],
                                            value="New",
                                        ),
                                        html.P(
                                            "Supplied Email",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Input(
                                            id="new_case_email",
                                            placeholder="email",
                                            type="email",
                                            value="",
                                            style={"width": "100%"},
                                        ),
                                        html.P(
                                            "Description",
                                            style={
                                                "float": "left",
                                                "marginTop": "4",
                                                "marginBottom": "2",
                                            },
                                            className="row",
                                        ),
                                        dcc.Textarea(
                                            id="new_case_description",
                                            placeholder="Description of the case",
                                            value="",
                                            style={"width": "100%"},
                                        ),
                                    ],
                                    className="six columns",
                                    style={"paddingLeft": "15"},
                                ),
                            ],
                            style={"marginTop": "10", "textAlign": "center"},
                            className="row",
                        ),

                        # submit button
                        html.Span(
                            "Submit",
                            id="submit_new_case",
                            n_clicks=0,
                            className="button button--primary add"
                        ),

                    ],
                    className="modal-content",
                    style={"textAlign": "center", "border": "1px solid #C8D4E3"},
                )
            ],
            className="modal",
        ),
        id="cases_modal",
        style={"display": "none"},
    )


# returns pie chart based on filters values
# column makes the fonction reusable 
layout = [
	# top controls
    html.Div(
        [
            html.Div(
                dcc.Dropdown(
                    id="proyectos_dropdown",
                    options=dm.proyects_options,
                    value="TD",
                    clearable=False,
                ),
                className="two columns",
                style={"marginBottom": "10"},
            ),
            #add button
            html.Div(
                html.Span(
                    "Add new",
                    id="new_case",
                    n_clicks=0,
                    className="button button--primary add",
                    
                ),
                className="two columns",
                style={"float": "right"},
            ),
        ],
        className="row",
        style={},
    ),
        # indicators div 
    # html.Div(
    #     [
    #         indicator(
    #             "#00cc96",
    #             "Total Cotizaciones",
    #             "left_cases_indicator",
    #         ),
    #         indicator(
    #             "#119DFF",
    #             "Total Personas",
    #             "middle_cases_indicator",
    #         ),
    #         indicator(
    #             "#EF553B",
    #             "Promedio Cotizacion Persona",
    #             "right_cases_indicator",
    #         ),
    #     ],
    #     className="row",
    # ),

    # html.Div(
    #    	[
    #     html.Div(
    #        [
    #         html.P("Cases Type"),
    #             dcc.Graph(
    #                 id="cases_types",
    #                 config=dict(displayModeBar=False),
    #                 style={"height": "89%", "width": "98%"},
    #             ),
    #        ],className="six columns chart_div",
    #     ),

    #     html.Div(
    #         [
    #         html.P("Cases Reasons"),
    #             dcc.Graph(
    #                 id="cases_reasons",
    #                 config=dict(displayModeBar=False),
    #                 style={"height": "89%", "width": "98%"},
    #             ),
    #         ],className="six columns chart_div"
    #     ),
    # 		],
    # 		className="row",
    # 		style={"marginTop": "5px"},
    # ),

   	# html.Div(
    #     [
    #         html.Div(
    #             [
    #                 html.P("Cotizaciones en el Tiempo"),
    #                 dcc.Graph(
    #                     id="cases_by_period",
    #                     config=dict(displayModeBar=False),
    #                     style={"height": "89%", "width": "98%"},
    #                 ),
    #             ],
    #             className="six columns chart_div"
    #         ),

    #         html.Div(
    #             [
    #                 html.P("Cases by Company"),
    #                 dcc.Graph(
    #                     id="cases_by_account",
    #                     #figure=cases_by_account(accounts, cases),
    #                     config=dict(displayModeBar=False),
    #                     style={"height": "87%", "width": "98%"},
    #                 ),
    #             ],
    #             className="six columns chart_div"
    #         ),
    #     ],
    #     className="row",
    #     style={"marginTop": "5px"},
    # ),
    html.Div([
        html.H6("Risk Potential",
            className="gs-header gs-table-header padded"),
                dcc.Graph(
                    id='graph-3',
                    figure = {
                        'data': [
                            go.Scatter(
                                    x = ["0", "0.18", "0.18", "0"],
                                    y = ["0.2", "0.2", "0.4", "0.2"],
                                    fill = "tozerox",
                                    fillcolor = "rgba(31, 119, 180, 0.2)",
                                    hoverinfo = "none",
                                    line = {"width": 0},
                                    mode = "lines",
                                    name = "B",
                                    showlegend = False
                                ),
                            go.Scatter(
                                    x = ["0.2", "0.38", "0.38", "0.2", "0.2"],
                                    y = ["0.2", "0.2", "0.6", "0.4", "0.2"],
                                    fill = "tozerox",
                                    fillcolor = "rgba(31, 119, 180, 0.4)",
                                    hoverinfo = "none",
                                    line = {"width": 0},
                                    mode = "lines",
                                    name = "D",
                                    showlegend = False
                                ),
                            go.Scatter(
                                    x = ["0.4", "0.58", "0.58", "0.4", "0.4"],
                                    y = ["0.2", "0.2", "0.8", "0.6", "0.2"],
                                    fill = "tozerox",
                                    fillcolor = "rgba(31, 119, 180, 0.6)",
                                    hoverinfo = "none",
                                    line = {"width": 0},
                                    mode = "lines",
                                    name = "F",
                                    showlegend = False
                                ),
                            go.Scatter(
                                    x = ["0.6", "0.78", "0.78", "0.6", "0.6"],
                                    y = ["0.2", "0.2", "1", "0.8", "0.2"],
                                    fill = "tozerox",
                                    fillcolor = "rgb(31, 119, 180)",
                                    hoverinfo = "none",
                                    line = {"width": 0},
                                    mode = "lines",
                                    name = "H",
                                    showlegend = False
                                ),
                            go.Scatter(
                                    x = ["0.8", "0.98", "0.98", "0.8", "0.8"],
                                    y = ["0.2", "0.2", "1.2", "1", "0.2"],
                                    fill = "tozerox",
                                    fillcolor = "rgba(31, 119, 180, 0.8)",
                                    hoverinfo = "none",
                                    line = {"width": 0},
                                    mode = "lines",
                                    name = "J",
                                    showlegend = False
                                ),
                            ],
                        'layout': go.Layout(
                            title = "",
                            annotations = [
                                {
                                      "x": 0.69,
                                      "y": 0.6,
                                      "font": {
                                        "color": "rgb(31, 119, 180)",
                                        "family": "Raleway",
                                        "size": 30
                                      },
                                      "showarrow": False,
                                      "text": "<b>4</b>",
                                      "xref": "x",
                                      "yref": "y"
                                    },
                                    {
                                      "x": 0.0631034482759,
                                      "y": -0.04,
                                      "align": "left",
                                      "font": {
                                        "color": "rgb(44, 160, 44)",
                                        "family": "Raleway",
                                        "size": 10
                                      },
                                      "showarrow": False,
                                      "text": "<b>Less risk<br>Less reward</b>",
                                      "xref": "x",
                                      "yref": "y"
                                    },
                                    {
                                      "x": 0.92125,
                                      "y": -0.04,
                                      "align": "right",
                                      "font": {
                                        "color": "rgb(214, 39, 40)",
                                        "family": "Raleway",
                                        "size": 10
                                      },
                                      "showarrow": False,
                                      "text": "<b>More risk<br>More reward</b>",
                                      "xref": "x",
                                      "yref": "y"
                                    }
                                  ],
                                  autosize = False,
                                  height = 200,
                                  width = 340,
                                  hovermode = "closest",
                                  margin = {
                                    "r": 10,
                                    "t": 20,
                                    "b": 80,
                                    "l": 10
                                  },
                                  shapes = [
                                    {
                                      "fillcolor": "rgb(255, 255, 255)",
                                      "line": {
                                        "color": "rgb(31, 119, 180)",
                                        "width": 4
                                      },
                                      "opacity": 1,
                                      "type": "circle",
                                      "x0": 0.621,
                                      "x1": 0.764,
                                      "xref": "x",
                                      "y0": 0.135238095238,
                                      "y1": 0.98619047619,
                                      "yref": "y"
                                    }
                                  ],
                                  showlegend = True,
                                  xaxis = {
                                    "autorange": False,
                                    "fixedrange": True,
                                    "range": [-0.05, 1.05],
                                    "showgrid": False,
                                    "showticklabels": False,
                                    "title": "<br>",
                                    "type": "linear",
                                    "zeroline": False
                                  },
                                  yaxis = {
                                    "autorange": False,
                                    "fixedrange": True,
                                    "range": [-0.3, 1.6],
                                    "showgrid": False,
                                    "showticklabels": False,
                                    "title": "<br>",
                                    "type": "linear",
                                    "zeroline": False
                                }
                            )
                        },
                        config={
                            'displayModeBar': False
                        }
                    )
                ], className="six columns"),
]

@app.callback(Output("cases_modal", "style"), 
    [Input("new_case", "n_clicks")])
def display_cases_modal_callback(n):
    print('open modal')
    if n > 0:
        return {"display": "block"}
    return {"display": "none"}


@app.callback(
    Output("new_case", "n_clicks"),
    [Input("cases_modal_close", "n_clicks"), 
    Input("submit_new_case", "n_clicks")],
)
def close_modal_callback(n, n2):
    return 0