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

# returns pie chart based on filters values
# column makes the fonction reusable 
def pie_chart(column):

    group = dm.df.groupby(column).count()
    labels = group.index
    values = group.ID.tolist()

    layout = go.Layout(
        margin=dict(l=0, r=0, b=0, t=4, pad=8),
        legend=dict(orientation="h"),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    trace = go.Pie(
        labels=labels,
        values=values,
        marker={"colors": ["#264e86", "#0074e4", "#74dbef", "#eff0f4"]},
    )

    return {"data": [trace], "layout": layout}

def cases_by_period(df, period, priority, origin):
    # df = df.dropna(subset=["Type", "Reason", "Origin"])
    # stages = df["Type"].unique()

    # priority filtering
    # if priority != "all_p":
    #     df = df[df["Priority"] == priority]

    # period filtering

    df = dm.df
    stages = df["Proyecto"].unique()

    # df["CreatedDate"] = pd.to_datetime(df["CreatedDate"], format="%Y-%m-%d")
    
    if period == "W-MON":
        df["CreatedDate"] = pd.to_datetime(df["CreatedDate"]) - pd.to_timedelta(7, unit="d")
    
    df = df.groupby([pd.Grouper(key="CreatedDate", freq=period), "Type"]).count() 
    
    dates = df.index.get_level_values("CreatedDate").unique()
    dates = [str(i) for i in dates]
    
    # co = { # colors for stages
    #     "Electrical": "#264e86",
    #     "Other": "#0074e4",
    #     "Structural": "#74dbef",
    #     "Mechanical": "#eff0f4",
    #     "Electronic": "rgb(255, 127, 14)",
    # }

    data = []
    for stage in stages:
        stage_rows = []
        for date in dates:
            try:
                row = df.loc[(date, stage)]
                stage_rows.append(row["IsDeleted"])
            except Exception as e:
                stage_rows.append(0)

        data_trace = go.Bar(
            x=dates, y=stage_rows, name=stage, marker=dict(color=co[stage])
        )
        data.append(data_trace)

    layout = go.Layout(
        # barmode="stack",
        margin=dict(l=40, r=25, b=40, t=0, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}

def bar_period_chart():
    cot_fecha = dm.df.set_index('Fecha Cotizacion')
    cot_fecha['cantidad'] = 1
    yearly = cot_fecha.cantidad.resample('Y').sum()
    y_data = yearly.tolist()
    x_data = [int(str(x).split('-')[0]) for x in yearly.index.tolist()]
    trace1 = go.Bar(
        x = x_data,
        y = y_data,
        name='Todos los Proyectos',
        marker = dict(color='rgb(55, 83, 109)')
    )

    data = [trace1]

    layout = go.Layout(
        margin=dict(l=40, r=25, b=40, t=0, pad=4),
        xaxis=dict(
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            # title='# Cotizaciones',
            titlefont=dict(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1
    )
    return {"data": data, "layout": layout}

layout = [
	# top controls
    html.Div(
        [
            html.Div(
                dcc.Dropdown(
                    id="proyectos_dropdown",
                    options=dm.options,
                    value="TD",
                    clearable=False,
                ),
                className="two columns",
                style={"marginBottom": "10"},
            ),
            # html.Div(
            #     dcc.Dropdown(
            #         id="priority_dropdown",
            #         options=[
            #             {"label": "All priority", "value": "all_p"},
            #             {"label": "High priority", "value": "High"},
            #             {"label": "Medium priority", "value": "Medium"},
            #             {"label": "Low priority", "value": "Low"},
            #         ],
            #         value="all_p",
            #         clearable=False,
            #     ),
            #     className="two columns",
            # ),
            # html.Div(
            #     dcc.Dropdown(
            #         id="origin_dropdown",
            #         options=[
            #             {"label": "All origins", "value": "all"},
            #             {"label": "Phone", "value": "Phone"},
            #             {"label": "Web", "value": "Web"},
            #             {"label": "Email", "value": "Email"},
            #         ],
            #         value="all",
            #         clearable=False,
            #     ),
            #     className="two columns",
            # ),

            # add button
            # html.Div(
            #     html.Span(
            #         "Add new",
            #         id="new_case",
            #         n_clicks=0,
            #         className="button button--primary add",
                    
            #     ),
            #     className="two columns",
            #     style={"float": "right"},
            # ),
        ],
        className="row",
        style={},
    ),
        # indicators div 
    html.Div(
        [
            indicator(
                "#00cc96",
                "Total Cotizaciones",
                "left_cases_indicator",
            ),
            indicator(
                "#119DFF",
                "Total Personas",
                "middle_cases_indicator",
            ),
            indicator(
                "#EF553B",
                "Promedio Cotizacion Persona",
                "right_cases_indicator",
            ),
        ],
        className="row",
    ),

    html.Div(
       	[
        html.Div(
           [
            html.P("Cases Type"),
                dcc.Graph(
                    id="cases_types",
                    config=dict(displayModeBar=False),
                    style={"height": "89%", "width": "98%"},
                ),
           ],className="six columns chart_div",
        ),

        html.Div(
            [
            html.P("Cases Reasons"),
                dcc.Graph(
                    id="cases_reasons",
                    config=dict(displayModeBar=False),
                    style={"height": "89%", "width": "98%"},
                ),
            ],className="six columns chart_div"
        ),
    		],
    		className="row",
    		style={"marginTop": "5px"},
    ),

   	html.Div(
        [
            html.Div(
                [
                    html.P("Cotizaciones en el Tiempo"),
                    dcc.Graph(
                        id="cases_by_period",
                        config=dict(displayModeBar=False),
                        style={"height": "89%", "width": "98%"},
                    ),
                ],
                className="six columns chart_div"
            ),

            html.Div(
                [
                    html.P("Cases by Company"),
                    dcc.Graph(
                        id="cases_by_account",
                        #figure=cases_by_account(accounts, cases),
                        config=dict(displayModeBar=False),
                        style={"height": "87%", "width": "98%"},
                    ),
                ],
                className="six columns chart_div"
            ),
        ],
        className="row",
        style={"marginTop": "5px"},
    ),
]

@app.callback(
    Output("left_cases_indicator", "children"), 
    [Input("proyectos_dropdown", "children"),
    Input("proyectos_dropdown", "value")]
)
def left_cases_indicator_callback(df, value):
    print(value)
    return dm.get_nro_cotizaciones()

@app.callback(
    Output("middle_cases_indicator", "children"), 
    [Input("proyectos_dropdown", "children"),
    Input("proyectos_dropdown", "value")]
)
def middle_cases_indicator_callback(df, value):
    return dm.get_personas_total()
@app.callback(
    Output("right_cases_indicator", "children"), 
    [Input("proyectos_dropdown", "children"),
    Input("proyectos_dropdown", "value")]
)
def right_cases_indicator_callback(df, value):
    return dm.get_personas_cot_mean()

@app.callback(
    Output("cases_types", "figure"),
    [
        # Input("priority_dropdown", "value"),
        Input("proyectos_dropdown", "value"),
        # Input("cases_df", "children"),
    ],
)
def cases_types_callback(value):
    print('llamada PIE')
    # df = pd.read_json(df, orient="split")
    return pie_chart('Medio')


@app.callback(
    Output("cases_by_period", "figure"),
    [
        Input("proyectos_dropdown", "value"),
    ],
)
def cases_period_callback(value):
    # df = pd.read_json(df, orient="split")
    return bar_period_chart()

