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
def pie_chart(df, column):

    group = df.groupby(column).count()
    labels = group.index
    values = group.ID.tolist()

    layout = go.Layout(
        margin=dict(l=0, r=0, b=0, t=4, pad=8),
        #legend=dict(orientation="h"),
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

def bar_period_chart(periodo, df):
    df = df.groupby([pd.Grouper(key='Fecha Cotizacion', freq=periodo), "Proyecto"]).count()

    dates = df.index.get_level_values('Fecha Cotizacion').unique()
    dates = [str(i) for i in dates]

    proyectos = dm.df.Proyecto.unique().tolist()
    data = []
    for proyecto in proyectos:
        proyecto_rows = []
        for date in dates:
            try:
                row = df.loc[(date, proyecto)]
                #             print(row['Medio'])
                proyecto_rows.append(row['Medio'])
            except Exception as e:
                proyecto_rows.append(0)

        data_trace = go.Bar(
            x=dates, y=proyecto_rows, name=proyecto
        )
        data.append(data_trace)

    layout = go.Layout(
        barmode="stack",
        margin=dict(l=40, r=25, b=40, t=0, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}

def categorical_columnbycolumn(column1, column2, df):
    col1 = column1
    col2 = column2
    col1_labels = df[col1].unique().tolist()
    col2_labels = df[col2].unique().tolist()

    values = []  # list of lists

    for value2 in col2_labels:
        col_values = []
        for value1 in col1_labels:
            col_values.append(dm.df[(dm.df[col1] == value1) & (dm.df[col2] == value2)]['ID'].count())
        values.append(col_values)

    traces = []

    for l in range(0, len(values)):
        trace = go.Bar(
            x=col1_labels,
            y=values[l],
            name=col2_labels[l]
        )
        traces.append(trace)

    data = traces
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
    return {'data':data, 'layour':layout}

layout = [
    # top controls
    html.Div(
            [
                html.Div(
                    dcc.Dropdown(
                        id="data_dropdown",
                        options=[{'label': 'Cotizaciones', 'value': 'cot'},
                                 {'label': 'Negocios', 'value': 'neg'}],
                        value="cot",
                        clearable=False,
                    ),
                    className="two columns",
                    style={},
                ),

                html.Div(
                    dcc.Dropdown(
                        id="proyectos_dropdown",
                        options=dm.proyects_options,
                        value="TP",
                        clearable=False,
                    ),
                    className="two columns",
                    style={},
                ),
                html.Div(
                    dcc.Dropdown(
                        id="column1_dropdown",
                        options=dm.cat_options,
                        value="Medio",
                        clearable=False,
                    ),
                    className="two columns",
                    style={},
                ),

                html.Div(
                    dcc.Dropdown(
                        id="column2_dropdown",
                        options=dm.cat_options,
                        value="Sexo",
                        clearable=False,
                    ),
                    className="two columns",
                    style={},
                ),
                html.Div(
                dcc.Dropdown(
                    id="period_dropdown",
                    options=[{'label': 'Anual', 'value': 'A'},
                             {'label': 'Trimestral', 'value': 'Q'},
                             {'label': 'Mensual', 'value': 'M'}],
                    value="A",
                    clearable=False,
                ),
                className="two columns",
                style={},
            ),
            ],
            className="row",
            style={"marginBottom": "5"},
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

    #Mid Controls
    html.Div(
            [
                # html.Div(
                #     dcc.Dropdown(
                #         id="column1_dropdown",
                #         options=dm.cat_options,
                #         value="Medio",
                #         clearable=False,
                #     ),
                #     className="two columns",
                #     style={"marginBottom": "10", 'marginTop':'10'},
                # ),

                # html.Div(
                #     dcc.Dropdown(
                #         id="column2_dropdown",
                #         options=dm.cat_options,
                #         value="Sexo",
                #         clearable=False,
                #     ),
                #     className="two columns",
                #     style={"marginBottom": "10", 'marginTop':'10'},
                # ),
            ],
            className="row",
            style={},
    ),

    html.Div(
        [
        # Single Column Chart
        html.Div(
           [
            html.P("Pie Chart"),
            dcc.Graph(
                id="cases_types",
                config=dict(displayModeBar=False),
                style={"height": "89%", "width": "98%"},
            ),
           ],className="six columns chart_div",
        ),
        #Double Column Chart
        html.Div(
            [
            html.P("Bar Chart"),
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

    # Period Controls
    html.Div(
        [
            # html.Div(
            #     dcc.Dropdown(
            #         id="period_dropdown",
            #         options=[{'label': 'Anual', 'value': 'A'},
            #                  {'label': 'Trimestral', 'value': 'Q'},
            #                  {'label': 'Mensual', 'value': 'M'}],
            #         value="A",
            #         clearable=False,
            #     ),
            #     className="two columns",
            #     style={"marginBottom": "10", 'marginTop':'10'},
            # ),
        ],
        className="row",
        style={},
    ),
   	html.Div(
        [
            html.Div(
                [
                    html.P("Total filas en el Tiempo"),
                    dcc.Graph(
                        id="cases_by_period",
                        config=dict(displayModeBar=False),
                        style={"height": "89%", "width": "98%"},
                    ),
                ],
                className="twelve columns chart_div"
            ),
        ],
        className="row",
        style={"marginTop": "5px"},
    ),
]

@app.callback(
    Output('column1_dropdown', 'options'),
    [Input('data_dropdown', 'value')]
)
def column1_options_callback(data):
    tmp_df = dm.data_change(data)
    tmp_columns = dm.get_categorical_columns(tmp_df)
    return [{'label':x, 'value':x} for x in tmp_columns]
    #return [0]

@app.callback(
    Output('column2_dropdown', 'options'),
    [Input('column1_dropdown', 'value'),
    Input('data_dropdown', 'value')]
)
def column2_options_callback(value, data):
    tmp_df = dm.data_change(data)
    tmp_columns = dm.get_categorical_columns(tmp_df)
    tmp_columns.remove(value)
    return [{'label':x, 'value':x} for x in tmp_columns]
    #return [0]

@app.callback(
    Output("left_cases_indicator", "children"), 
    [Input("proyectos_dropdown", "children"),
    Input("proyectos_dropdown", "value"),
    Input('data_dropdown', 'value')]
)
def left_cases_indicator_callback(df, proyecto, data):
    df_tmp = dm.data_change(data)
    if proyecto != 'TP':
        df_tmp = df_tmp[df_tmp['Proyecto'] == proyecto]
    print(data, proyecto)
    return dm.get_filas_data(df_tmp)

@app.callback(
    Output("middle_cases_indicator", "children"), 
    [Input("proyectos_dropdown", "children"),
    Input("proyectos_dropdown", "value"),
    Input('data_dropdown', 'value')]
)
def middle_cases_indicator_callback(df, proyecto, data):
    df_tmp = dm.data_change(data)
    if proyecto != 'TP':
        df_tmp = df_tmp[df_tmp['Proyecto'] == proyecto]
    return dm.get_personas_total(df_tmp)

@app.callback(
    Output("right_cases_indicator", "children"), 
    [Input("proyectos_dropdown", "children"),
    Input("proyectos_dropdown", "value"),
    Input('data_dropdown', 'value')]
)
def right_cases_indicator_callback(df, proyecto, data):
    df_tmp = dm.data_change(data)
    if proyecto != 'TP':
        df_tmp = df_tmp[df_tmp['Proyecto'] == proyecto]
    return dm.get_personas_cot_mean(df_tmp)

@app.callback(
    Output("cases_types", "figure"),
    [
        Input("column1_dropdown", "value"),
        Input('data_dropdown', 'value'),
        Input("proyectos_dropdown", "value")
    ],
)
def cases_types_callback(vcol1, data, proyecto):
    tmp_data = dm.data_change(data)
    if proyecto != 'TP':
        tmp_data = tmp_data[tmp_data['Proyecto'] == proyecto]
    return pie_chart(tmp_data, vcol1)

@app.callback(
    Output("cases_by_period", "figure"),
    [
        Input("proyectos_dropdown", "value"),
        Input("period_dropdown", "value"),
        Input('data_dropdown', 'value'),
    ],
)
def cases_period_callback(proyecto, periodo, data):
    tmp_data = dm.data_change(data)
    if proyecto != 'TP':
        tmp_data = tmp_data[tmp_data['Proyecto'] == proyecto]
    return bar_period_chart(periodo, tmp_data)

@app.callback(
    Output('cases_reasons', 'figure'),
    [Input("column1_dropdown", 'value'),
     Input("column2_dropdown", 'value'),
     Input('data_dropdown', 'value'),
     Input("proyectos_dropdown", "value")
     ]
)
def cases_reasons_callback(column1, column2, data, proyecto):
    tmp_data = dm.data_change(data)
    if proyecto != 'TP':
        tmp_data = tmp_data[tmp_data['Proyecto'] == proyecto]
    return categorical_columnbycolumn(column1, column2, tmp_data)