# -*- coding: utf-8 -*-
import math
import json
import numpy as np

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
from utils.figures import pie_chart, cases_by_period, bar_period_chart, categorical_columnbycolumn

colors = {"background": "#F3F6FA", "background_div": "white"}

layout = [
    # top controls
    html.Div(
            [
                # Data & Inmueble
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
                                ),className=''),
                            ]
                            ,className='row')
                        ,className='two columns'
                    ),
                ),
                # Proyecto & Etapa
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
                        ,className='two columns'
                    ),
                ),
                # Columnas
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
                        ,className='two columns'
                    ),
                ),
                # Unidad Tiempo
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
                        ,className='two columns'
                    ),
                ),
                # Date Picker
                html.Div([
                        html.Div(
                            [
                                # html.P("Unidad Tiempo:"),
                                html.Div(
                                    dcc.RangeSlider(
                                    id='datos_year_rangeslider',
                                    marks={i: '{}'.format(i) for i in dm.data_years},
                                    min=dm.date_min,
                                    max=dm.date_max,
                                    value=[dm.date_min, dm.date_max]
                                )
                                ),                              
                            ]
                            ,className='row', style={'padding':'30'}),
                        
                    html.Div(
                            [
                                # html.P("Unidad Tiempo:"),
                                html.Div(
                                    dcc.RangeSlider(
                                    id='datos_month_rangeslider',
                                    marks={i: '{}'.format(j) for i, j in zip(range(1, 13), dm.months)},
                                    min=1,
                                    max=12,
                                    value=[1,12]
                                )
                                ),                              
                            ]
                            ,className='row', style={'padding':'30'})
                ],className='four columns'),


            ],
            className="row",
            style={"marginBottom": "5"},
    ),

    
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
    Input('proyectos_dropdown', 'value'),
    Input('datos_year_rangeslider', 'value'),
    Input('datos_month_rangeslider', 'value')]
)
def left_cases_indicator_callback(data, inmueble, etapa, proyecto, year_values, month_values):
    if inmueble == 'Casa':
        data = dm.get_data_whithin_dates(data, proyecto, inmueble, year_values, month_values, etapa)
    else: 
        data = dm.get_data_whithin_dates(data, proyecto, inmueble, year_values, month_values)

    return data.shape[0]

@app.callback(
    Output("middle_cases_indicator", "children"), 
    [Input("data_dropdown", "value"),
    Input("inmuebles_dropdown", "value"),
    Input("etapa_dropdown", "value"),
    Input('proyectos_dropdown', 'value'),
    Input('datos_year_rangeslider', 'value'),
    Input('datos_month_rangeslider', 'value')]
)
def middle_cases_indicator_callback(data, inmueble, etapa, proyecto, year_values, month_values):

    if inmueble == 'Casa':
        data = dm.get_data_whithin_dates(data, proyecto, inmueble, year_values, month_values, etapa)
    else: 
        data = dm.get_data_whithin_dates(data, proyecto, inmueble, year_values, month_values)

    return data.RUT.nunique()

@app.callback(
    Output("right_cases_indicator", "children"), 
    [Input("data_dropdown", "value"),
    Input("inmuebles_dropdown", "value"),
    Input("etapa_dropdown", "value"),
    Input('proyectos_dropdown', 'value'),
    Input('datos_year_rangeslider', 'value'),
    Input('datos_month_rangeslider', 'value')]
)
def right_cases_indicator_callback(data, inmueble, etapa, proyecto, year_values, month_values):

    if inmueble == 'Casa':
        data = dm.get_data_whithin_dates(data, proyecto, inmueble, year_values, month_values, etapa)
    else: 
        data = dm.get_data_whithin_dates(data, proyecto, inmueble, year_values, month_values)


    num_cot = []
    for group, frame in data.groupby('RUT'):
        num_cot.append(frame.shape[0])
    
    try:
        return millify(np.mean(num_cot))
    except ValueError:
        return 'Error'

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
        Input("proyectos_dropdown", "value"),
        Input('datos_year_rangeslider', 'value'),
        Input('datos_month_rangeslider', 'value')
    ],
)
def pie_chart_callback(vcol1, data, inmueble, etapa, proyecto, year_values, month_values):
    if inmueble == 'Casa':
        data = dm.get_data_whithin_dates(data, proyecto, inmueble, year_values, month_values, etapa)
    else: 
        data = dm.get_data_whithin_dates(data, proyecto, inmueble, year_values, month_values)


    return pie_chart(data, vcol1)

# Grafico doble columna
@app.callback(
    Output('cases_reasons', 'figure'),
    [Input("column1_dropdown", 'value'),
    Input("column2_dropdown", 'value'),
    Input("data_dropdown", "value"),
    Input("inmuebles_dropdown", "value"),
    Input("etapa_dropdown", "value"),
    Input('proyectos_dropdown', 'value'),
    Input('datos_year_rangeslider', 'value'),
    Input('datos_month_rangeslider', 'value')
     ]
)
def columns_two_callback(column1, column2, data, inmueble, etapa, proyecto, year_values, month_values):

    if inmueble == 'Casa':
        data = dm.get_data_whithin_dates(data, proyecto, inmueble, year_values, month_values, etapa)
    else: 
        data = dm.get_data_whithin_dates(data, proyecto, inmueble, year_values, month_values)

    return categorical_columnbycolumn(column1, column2, data)

# Grafico de barras en el tiempo
@app.callback(
    Output("cases_by_period", "figure"),
    [
    Input("proyectos_dropdown", "value"),
    Input("period_dropdown", "value"),
    Input('data_dropdown', 'value'),
    Input('datos_year_rangeslider', 'value'),
    Input('datos_month_rangeslider', 'value')
    ],
)
def data_period_callback(proyecto, periodo, data, year_values, month_values):
    tmp_data = dm.data_change(data)
    if proyecto != 'TP':
        tmp_data = tmp_data[tmp_data['Proyecto'] == proyecto]
    return bar_period_chart(periodo, tmp_data)

