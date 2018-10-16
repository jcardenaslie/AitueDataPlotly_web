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

from app import app, indicator, small_indicator, millify, df_to_table
import data_manager as dm

from datetime import datetime as dt

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
            col_values.append(df[(df[col1] == value1) & (df[col2] == value2)]['ID'].count())
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
                    html.Div(
                        html.Div(
                            [
                            html.P("Data:"),
                            dcc.Dropdown(
                                id="data_dropdown",
                                options=[{'label': 'Cotizaciones', 'value': 'cot'},
                                         {'label': 'Negocios', 'value': 'neg'}],
                                value="cot",
                                clearable=False,
                            ), 
                            html.P("Inmueble:"),
                            html.Div(
                                dcc.Dropdown(
                                    id="inmuebles_dropdown",
                                    options=dm.inmb_options,
                                    value="TI",
                                    clearable=False,
                                ),className='twelve columns'),
                            ]
                            ,className='row')
                        ,className='three columns'
                    ),
                ),

                html.Div(
                    html.Div(
                        html.Div(
                            [
                            html.P("Proyecto:"),
                            dcc.Dropdown(
                                id="proyectos_dropdown",
                                options=[{'label':'Todos', 'value':'TP'}],
                                value="TP",
                                clearable=False,
                            ),
                            html.P("Etapa:"),
                            html.Div(
                                dcc.Dropdown(
                                    id="etapa_dropdown",
                                    options=[{'label':'No disponible', 'value':None}],
                                    value=None,
                                    clearable=False,
                                ),
                            )
                            ]
                            ,className='row')
                        ,className='three columns'
                    ),
                ),

                html.Div(
                    html.Div(
                        html.Div(
                            [
                            html.P("Columna 1:"),
                            dcc.Dropdown(
                                id="column1_dropdown",
                                options=dm.cat_options,
                                value="Medio",
                                clearable=False,
                            ), 
                            html.P("Columna 2:"),
                            html.Div(
                                dcc.Dropdown(
                                id="column2_dropdown",
                                options=dm.cat_options,
                                value="Sexo",
                                clearable=False,
                            ),className='twelve columns'),
                            ]
                            ,className='row')
                        ,className='three columns'
                    ),
                ),

                html.Div(
                    html.Div(
                        html.Div(
                            [
                            html.P("Unidad Tiempo:"),
                            html.Div(
                                dcc.Dropdown(
                                    id="period_dropdown",
                                    options=[{'label': 'Anual', 'value': 'A'},
                                             {'label': 'Trimestral', 'value': 'Q'},
                                             {'label': 'Mensual', 'value': 'M'}],
                                    value="A",
                                    clearable=False,
                                ),
                            ), 

                            ]
                            ,className='row')
                        ,className='three columns'
                    ),
                ),


            ],
            className="row",
            style={"marginBottom": "5"},
    ),

    html.Div([
        html.P("Periodo de Tiempo:"),
                    dcc.DatePickerRange(
                                    id='date-picker-range',
                                    start_date=dt(1997, 5, 3),
                                    end_date_placeholder_text='Select a date!'
                                )
                    ], className='row'),
    # indicators div 
    html.Div(
            [
                indicator(
                    "#00cc96",
                    "Total Filas",
                    "left_cases_indicator",
                ),
                indicator(
                    "#119DFF",
                    "Total Personas",
                    "middle_cases_indicator",
                ),
                indicator(
                    "#EF553B",
                    "Promedio Filas Persona",
                    "right_cases_indicator",
                ),
            ],
            className="row",
    ),

        # indicators div 
    html.Div(
            [
                indicator(
                    "#00cc96",
                    "Total Reservas",
                    "first_cases_indicator",
                ),
                indicator(
                    "#119DFF",
                    "Total Promesados",
                    "second_cases_indicator",
                ),
                indicator(
                    "#EF553B",
                    "Total Escrituras",
                    "third_cases_indicator",
                ),
                indicator(
                    "#EF553B",
                    "Total Entregas",
                    "fourth_cases_indicator",
                ),
            ],
            className="row",
    ),

    # html.Div([
    #     html.Div([
    #         html.Div([
    #             html.P('P'),
    #             html.P('P')]
    #             ,className='three columns'
    #         ),
    #         html.Div([
    #             html.P('P'),
    #             html.P('P')]
    #             ,className='three columns'
    #         ),
    #         html.Div([
    #             html.P('P'),
    #             html.P('P')]
    #             ,className='three columns'
    #         ),
    #         html.Div([
    #             html.P('P'),
    #             html.P('P')]
    #             ,className='three columns'
    #         )]
    #     ,className='row', style={}),
    # ]),

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
            # html.P("Pie Chart"),
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
            # html.P("Bar Chart"),
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
                    # html.P("Total filas en el Tiempo"),
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


###CONTROLES
#############################################################################
# Proyectos depende de Casa y data para recuperar los datos
@app.callback(
    Output('proyectos_dropdown', 'options'),
    [
    # Input('data_dropdown', 'children'),
    Input('data_dropdown', 'value'),
    Input('inmuebles_dropdown', 'value')]
    )
def inmuebles_dropdown_callback(data, inmueble):
    proyectos = dm.get_proyectos_in_inmueble(data, inmueble)
    return proyectos

# etapa depende de inmueble y data y proyecto para recuperar los datos
@app.callback(
    Output('etapa_dropdown', 'options'),
    [
    # Input('data_dropdown', 'children'),
    Input('data_dropdown', 'value'),
    Input('inmuebles_dropdown', 'value'),
    Input('proyectos_dropdown', 'value')]
    )

def etapa_dropdown_callback(data, inmueble, proyecto):
    
    if inmueble == 'Casa':
        return dm.get_etapa_in_proyecto(data, inmueble, proyecto) 
    else:
        return [{'label':'No disponible', 'value':None}] 


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
    [Input('data_dropdown', 'value'),
    Input('column1_dropdown', 'value')
    ]
)
def column2_options_callback(data, value):
    tmp_df = dm.data_change(data)
    tmp_columns = dm.get_categorical_columns(tmp_df)
    tmp_columns.remove(value)
    return [{'label':x, 'value':x} for x in tmp_columns]
    #return [0]

##INDICADORES
############################################################################
@app.callback(
    Output("left_cases_indicator", "children"), 
    [Input("data_dropdown", "value"),
    Input("inmuebles_dropdown", "value"),
    Input("etapa_dropdown", "value"),
    Input('proyectos_dropdown', 'value')]
)
def left_cases_indicator_callback(data, inmueble, etapa, proyecto):
    if inmueble == 'Casa':
        return dm.get_filas_data(data, inmueble, proyecto, etapa)
    else: 
        return dm.get_filas_data(data, inmueble, proyecto)

@app.callback(
    Output("middle_cases_indicator", "children"), 
    [Input("data_dropdown", "value"),
    Input("inmuebles_dropdown", "value"),
    Input("etapa_dropdown", "value"),
    Input('proyectos_dropdown', 'value')]
)
def middle_cases_indicator_callback(data, inmueble, etapa, proyecto):
    if inmueble == 'Casa':
        return dm.get_personas_total(data, inmueble, proyecto, etapa)
    else: 
        return dm.get_personas_total(data, inmueble, proyecto)

@app.callback(
    Output("right_cases_indicator", "children"), 
    [Input("data_dropdown", "value"),
    Input("inmuebles_dropdown", "value"),
    Input("etapa_dropdown", "value"),
    Input('proyectos_dropdown', 'value')]
)
def right_cases_indicator_callback(data, inmueble, etapa, proyecto):
    if inmueble == 'Casa':
        return dm.get_personas_cot_mean(data, inmueble, proyecto, etapa)
    else: 
        return dm.get_personas_cot_mean(data, inmueble, proyecto)

@app.callback(
    Output("first_cases_indicator", "children"), 
    [Input("data_dropdown", "value"),
    Input("inmuebles_dropdown", "value"),
    Input("etapa_dropdown", "value"),
    Input('proyectos_dropdown', 'value')]
)
def first_indicator_callback(data, inmueble, etapa, proyecto):
    if data != 'neg':
        return []

    if inmueble == 'Casa':
        return dm.get_reservas(data, inmueble,  proyecto, etapa)
    else: 
        return dm.get_reservas(data, inmueble,  proyecto)

@app.callback(
    Output("second_cases_indicator", "children"), 
    [Input("data_dropdown", "value"),
    Input("inmuebles_dropdown", "value"),
    Input("etapa_dropdown", "value"),
    Input('proyectos_dropdown', 'value')]
)
def second_indicator_callback(data, inmueble, etapa, proyecto):
    if data != 'neg':
        return []

    if inmueble == 'Casa':
        return dm.get_promesas(data, inmueble,  proyecto, etapa)
    else: 
        return dm.get_promesas(data, inmueble,  proyecto)

@app.callback(
    Output("third_cases_indicator", "children"), 
    [Input("data_dropdown", "value"),
    Input("inmuebles_dropdown", "value"),
    Input("etapa_dropdown", "value"),
    Input('proyectos_dropdown', 'value')]
)
def third_indicator_callback(data, inmueble, etapa, proyecto):
    if data != 'neg':
        return []

    if inmueble == 'Casa':
        return dm.get_escrituras(data, inmueble,  proyecto, etapa)
    else: 
        return dm.get_escrituras(data, inmueble,  proyecto)

@app.callback(
    Output("fourth_cases_indicator", "children"), 
    [Input("data_dropdown", "value"),
    Input("inmuebles_dropdown", "value"),
    Input("etapa_dropdown", "value"),
    Input('proyectos_dropdown', 'value')]
)
def fourth_indicator_callback(data, inmueble, etapa, proyecto):
    if data != 'neg':
        return []

    if inmueble == 'Casa':
        return dm.get_entregas(data, inmueble,  proyecto, etapa)
    else: 
        return dm.get_entregas(data, inmueble,  proyecto)


##GRAFICOS
#############################################################################
# Grafico de Pie
@app.callback(
    Output("cases_types", "figure"),
    [
        Input("column1_dropdown", "value"),
        Input("data_dropdown", "value"),
        Input("inmuebles_dropdown", "value"),
        Input("etapa_dropdown", "value"),
        Input('proyectos_dropdown', 'value')
    ],
)
def pie_chart_callback(vcol1, data, inmueble, etapa, proyecto):
    if inmueble == 'Casa':
        tmp_data = dm.get_data(data, inmueble, proyecto, etapa)
    else: 
        tmp_data = dm.get_data(data, inmueble, proyecto)

    return pie_chart(tmp_data, vcol1)

# Grafico de barras en el tiempo
@app.callback(
    Output("cases_by_period", "figure"),
    [
        Input("proyectos_dropdown", "value"),
        Input("period_dropdown", "value"),
        Input('data_dropdown', 'value'),
    ],
)
def data_period_callback(proyecto, periodo, data):
    tmp_data = dm.data_change(data)
    if proyecto != 'TP':
        tmp_data = tmp_data[tmp_data['Proyecto'] == proyecto]
    return bar_period_chart(periodo, tmp_data)

# Grafico doble columna
@app.callback(
    Output('cases_reasons', 'figure'),
    [Input("column1_dropdown", 'value'),
     Input("column2_dropdown", 'value'),
     Input("data_dropdown", "value"),
        Input("inmuebles_dropdown", "value"),
        Input("etapa_dropdown", "value"),
        Input('proyectos_dropdown', 'value')
     ]
)
def columns_two_callback(column1, column2, data, inmueble, etapa, proyecto):
    if inmueble == 'Casa':
        tmp_data = dm.get_data(data, inmueble, proyecto, etapa)
    else: 
        tmp_data = dm.get_data(data, inmueble, proyecto)
    
    return categorical_columnbycolumn(column1, column2, tmp_data)