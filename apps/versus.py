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
from datetime import datetime as dt
from utils.figures import pie_chart, bar_period_chart, categorical_columnbycolumn

colors = {"background": "#F3F6FA", "background_div": "white"}

layout = [
    html.Div(id='test-div', style={'display': 'none'}),
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
                                disabled=True
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
    # Headers
	html.Div(
    [
    	html.H3(children='Cotizaciones',className="four columns" ),
    	html.H3(children='Negocios',className="four columns" ),
        html.H3(children='Compras',className="four columns" ),
    ],className="row",
            style={"marginBottom": "5"},
    ),
	
    # First Compare Figure
    html.Div(
        [
        # Single Column Chart
        html.Div(
           [
            # html.P("Pie Chart"),
            dcc.Graph(
                id="cot_graph1",
                config=dict(displayModeBar=False),
                style={"height": "89%", "width": "98%"},
            ),
           ],className="four columns chart_div",
        ),
        #Double Column Chart
        html.Div(
            [
            # html.P("Pie Chart"),
            dcc.Graph(
                id="neg_graph1",
                config=dict(displayModeBar=False),
                style={"height": "89%", "width": "98%"},
            ),
            ],className="four columns chart_div"
        ),
        html.Div(
            [
            # html.P("Pie Chart"),
            dcc.Graph(
                id="comp_graph1",
                config=dict(displayModeBar=False),
                style={"height": "89%", "width": "98%"},
            ),
            ],className="four columns chart_div"
        ),
    		],
    		className="row",
    		style={"marginTop": "5px"},
    ),
    # Second Compare Bar Figure
    html.Div(
        [
        # Single Column Chart
        html.Div(
           [
            # html.P("Bar Chart"),
            dcc.Graph(
                id="cot_graph2",
                config=dict(displayModeBar=False),
                style={"height": "89%", "width": "98%"},
            ),
           ],className="four columns chart_div",
        ),
        #Double Column Chart
        html.Div(
            [
            # html.P("Bar Chart"),
            dcc.Graph(
                id="neg_graph2",
                config=dict(displayModeBar=False),
                style={"height": "89%", "width": "98%"},
            ),
            ],className="four columns chart_div"
        ),
        html.Div(
            [
            # html.P("Bar Chart"),
            dcc.Graph(
                id="comp_graph2",
                config=dict(displayModeBar=False),
                style={"height": "89%", "width": "98%"},
            ),
            ],className="four columns chart_div"
        ),
    		],
    		className="row",
    		style={"marginTop": "5px"},
    ),

    # Period Comparing Figure
    html.Div(
        [
            html.Div(
                [
                    html.P("Cotizaciones y Negocios en el Tiempo"),
                    dcc.Graph(
                        id="cot_neg_period",
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

#Queda mal con el loading, se loopea
# @app.callback(
#     Output('test-div', 'children'),
#     [Input('comp_graph1', 'hoverData')])
# def display_click_data(hoverData):
#     print(json.dumps(hoverData, indent=2))
#     return 0


################################################################################################


######################################################################################################
# Grafico de Pie
@app.callback(
    Output("cot_graph1", "figure"),
    [
        Input("column1_dropdown", "value"),
        Input("inmuebles_dropdown", "value"),
        Input("etapa_dropdown", "value"),
        Input("proyectos_dropdown", "value"),
        Input('datos_year_rangeslider', 'value'),
        Input('datos_month_rangeslider', 'value')
    ],
)
def cot_pie_callback(vcol1, inmueble, etapa, proyecto, year_values, month_values):
    if inmueble == 'Casa':
        data = dm.get_data_whithin_dates('cot', proyecto, inmueble, year_values, month_values, etapa)
    else: 
        data = dm.get_data_whithin_dates('cot', proyecto, inmueble, year_values, month_values)


    return pie_chart(data, vcol1)

#PIE
# Grafico doble columna
@app.callback(
    Output('cot_graph2', 'figure'),
    [Input("column1_dropdown", 'value'),
    Input("column2_dropdown", 'value'),
    Input("inmuebles_dropdown", "value"),
    Input("etapa_dropdown", "value"),
    Input('proyectos_dropdown', 'value'),
    Input('datos_year_rangeslider', 'value'),
    Input('datos_month_rangeslider', 'value')
     ]
)
def cot_bar_callback(column1, column2, inmueble, etapa, proyecto, year_values, month_values):

    if inmueble == 'Casa':
        data = dm.get_data_whithin_dates('cot', proyecto, inmueble, year_values, month_values, etapa)
    else: 
        data = dm.get_data_whithin_dates('cot', proyecto, inmueble, year_values, month_values)

    return categorical_columnbycolumn(column1, column2, data)

# Grafico de Pie
@app.callback(
    Output("neg_graph1", "figure"),
    [
        Input("column1_dropdown", "value"),
        Input("inmuebles_dropdown", "value"),
        Input("etapa_dropdown", "value"),
        Input("proyectos_dropdown", "value"),
        Input('datos_year_rangeslider', 'value'),
        Input('datos_month_rangeslider', 'value')
    ],
)
def neg_pie_callback(vcol1, inmueble, etapa, proyecto, year_values, month_values):
    if inmueble == 'Casa':
        data = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values, etapa)
    else: 
        data = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values)


    return pie_chart(data, vcol1)

#PIE
# Grafico doble columna
@app.callback(
    Output('neg_graph2', 'figure'),
    [Input("column1_dropdown", 'value'),
    Input("column2_dropdown", 'value'),
    Input("inmuebles_dropdown", "value"),
    Input("etapa_dropdown", "value"),
    Input('proyectos_dropdown', 'value'),
    Input('datos_year_rangeslider', 'value'),
    Input('datos_month_rangeslider', 'value')
     ]
)
def neg_bar_callback(column1, column2, inmueble, etapa, proyecto, year_values, month_values):

    if inmueble == 'Casa':
        data = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values, etapa)
    else: 
        data = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values)

    return categorical_columnbycolumn(column1, column2, data)
# Grafico de Pie
@app.callback(
    Output("comp_graph1", "figure"),
    [
        Input("column1_dropdown", "value"),
        Input("inmuebles_dropdown", "value"),
        Input("etapa_dropdown", "value"),
        Input("proyectos_dropdown", "value"),
        Input('datos_year_rangeslider', 'value'),
        Input('datos_month_rangeslider', 'value')
    ],
)
def comp_pie_callback(vcol1, inmueble, etapa, proyecto, year_values, month_values):
    if inmueble == 'Casa':
        data = dm.get_data_whithin_dates('comp', proyecto, inmueble, year_values, month_values, etapa)
    else: 
        data = dm.get_data_whithin_dates('comp', proyecto, inmueble, year_values, month_values)


    return pie_chart(data, vcol1)

#PIE
# Grafico doble columna
@app.callback(
    Output('comp_graph2', 'figure'),
    [Input("column1_dropdown", 'value'),
    Input("column2_dropdown", 'value'),
    Input("inmuebles_dropdown", "value"),
    Input("etapa_dropdown", "value"),
    Input('proyectos_dropdown', 'value'),
    Input('datos_year_rangeslider', 'value'),
    Input('datos_month_rangeslider', 'value')
     ]
)
def comp_bar_callback(column1, column2,  inmueble, etapa, proyecto, year_values, month_values):

    if inmueble == 'Casa':
        data = dm.get_data_whithin_dates('comp', proyecto, inmueble, year_values, month_values, etapa)
    else: 
        data = dm.get_data_whithin_dates('comp', proyecto, inmueble, year_values, month_values)

    return categorical_columnbycolumn(column1, column2, data)


@app.callback(
    Output("cot_neg_period", "figure"),
    [
        Input("proyectos_dropdown", "value"),
        Input("period_dropdown", "value"),
    ],
)
def cases_period_callback(proyecto, periodo):
    return bar_period_chart(periodo, proyecto)