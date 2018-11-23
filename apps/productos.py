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
import timeit
from utils.figures import bar_period_chart


layout = [
    html.Div([html.P("* Esta pestaña toma un tiempo en cargar")]),
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
	#charts row div 
    html.Div(
        [
            html.Div(
                [
                    html.P("Estados vs Etapas"),
                    dcc.Graph(
                        id="etapa_bar_stacked",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],id = 'etapas_vs_estado',
                className="twelve columns chart_div"
            ),
        ],id = 'prueba',
        className="row",
        style={"marginTop": "5px"}
    ),
	# indicators div 
    html.Div(
            [
                indicator(
                    "#00cc96",
                    "Más Cotizado",
                    "prod_mas_cotizado",
                ),
                indicator(
                    "#119DFF",
                    "Más Negocio",
                    "prod_mas_negocio",
                ),
                indicator(
                    "#EF553B",
                    "Más Vendido",
                    "prod_mas_vendido",
                ),
            ],
            className="row",
    ),

    # tables row div
    html.Div(
        [
            html.Div(
                [
                    html.P(
                        "Top Productos Cotizados",
                        style={
                            "color": "#2a3f5f",
                            "fontSize": "13px",
                            "textAlign": "center",
                            "marginBottom": "0",
                        },
                    ),
                    html.Div(
                        id="top_prod_cotizados",
                        style={"padding": "0px 13px 5px 13px", "marginBottom": "5"},
                    ),
                   
                ],
                className="four columns",
                style={
                    "backgroundColor": "white",
                    "border": "1px solid #C8D4E3",
                    "borderRadius": "3px",
                    "height": "100%",
                    "overflowY": "scroll",
                },
            ),
            html.Div(
                [
                    html.P(
                        "Top Productos Negociados",
                        style={
                            "color": "#2a3f5f",
                            "fontSize": "13px",
                            "textAlign": "center",
                            "marginBottom": "0",
                        },
                    ),
                    html.Div(
                        id="top_prod_negociados",
                        style={"padding": "0px 13px 5px 13px", "marginBottom": "5"},
                    )
                ],
                className="four columns",
                style={
                    "backgroundColor": "white",
                    "border": "1px solid #C8D4E3",
                    "borderRadius": "3px",
                    "height": "100%",
                    "overflowY": "scroll",
                },
            ),
            html.Div(
                [
                    html.P(
                        "Top Productos Vendidos",
                        style={
                            "color": "#2a3f5f",
                            "fontSize": "13px",
                            "textAlign": "center",
                            "marginBottom": "0",
                        },
                    ),
                    html.Div(
                        id="top_prod_vendidos",
                        style={"padding": "0px 13px 5px 13px", "marginBottom": "5"},
                    )
                ],
                className="four columns",
                style={
                    "backgroundColor": "white",
                    "border": "1px solid #C8D4E3",
                    "borderRadius": "3px",
                    "height": "100%",
                    "overflowY": "scroll",
                },
            ),
        ],
        className="row",
        style={"marginTop": "5px", "max height": "200px"},
    ),

    # indicators div 
    html.Div(
            [
                indicator(
                    "#00cc96",
                    "Menos Cotizado",
                    "prod_menos_cotizado",
                ),
                indicator(
                    "#119DFF",
                    "Menos Negocio",
                    "prod_menos_negocio",
                ),
                indicator(
                    "#EF553B",
                    "Menos Vendido",
                    "prod_menos_vendido",
                ),
            ],
            className="row",
    ),

    html.Div(
        [
            html.Div(
                [
                    html.P(
                        "Menor Productos Cotizados",
                        style={
                            "color": "#2a3f5f",
                            "fontSize": "13px",
                            "textAlign": "center",
                            "marginBottom": "0",
                        },
                    ),
                    html.Div(
                        id="menor_prod_cotizados",
                        style={"padding": "0px 13px 5px 13px", "marginBottom": "5"},
                    ),
                   
                ],
                className="four columns",
                style={
                    "backgroundColor": "white",
                    "border": "1px solid #C8D4E3",
                    "borderRadius": "3px",
                    "height": "100%",
                    "overflowY": "scroll",
                },
            ),
            html.Div(
                [
                    html.P(
                        "Menor Productos Negociados",
                        style={
                            "color": "#2a3f5f",
                            "fontSize": "13px",
                            "textAlign": "center",
                            "marginBottom": "0",
                        },
                    ),
                    html.Div(
                        id="menor_prod_negociados",
                        style={"padding": "0px 13px 5px 13px", "marginBottom": "5"},
                    )
                ],
                className="four columns",
                style={
                    "backgroundColor": "white",
                    "border": "1px solid #C8D4E3",
                    "borderRadius": "3px",
                    "height": "100%",
                    "overflowY": "scroll",
                },
            ),
            html.Div(
                [
                    html.P(
                        "Menor Productos Vendidos",
                        style={
                            "color": "#2a3f5f",
                            "fontSize": "13px",
                            "textAlign": "center",
                            "marginBottom": "0",
                        },
                    ),
                    html.Div(
                        id="menor_prod_vendidos",
                        style={"padding": "0px 13px 5px 13px", "marginBottom": "5"},
                    )
                ],
                className="four columns",
                style={
                    "backgroundColor": "white",
                    "border": "1px solid #C8D4E3",
                    "borderRadius": "3px",
                    "height": "100%",
                    "overflowY": "scroll",
                },
            ),
        ],
        className="row",
        style={"marginTop": "5px", "max height": "200px"},
    ),
    html.Div(id="cot_prod_info", style={"display": "none"},),
    html.Div(id="neg_prod_info", style={"display": "none"},),
    html.Div(id="comp_prod_info", style={"display": "none"},),
]

@app.callback(
    Output('cot_prod_info', 'children'),
    [Input("inmuebles_dropdown", "value"),
    Input("etapa_dropdown", "value"),
    Input('proyectos_dropdown', 'value'),
    Input('datos_year_rangeslider', 'value'),
    Input('datos_month_rangeslider', 'value')]
)
def calculate_productos_cot(inmueble, etapa, proyecto, year_values, month_values):
    if inmueble == 'Casa':
        df = dm.calc_nro_cotizaciones('cot', inmueble, proyecto, year_values, month_values, etapa=etapa)
    else:
        df = dm.calc_nro_cotizaciones('cot', inmueble, proyecto, year_values, month_values)
    # print(df.head())
    return df.to_json(date_format='iso', orient='split')

@app.callback(
    Output('neg_prod_info', 'children'),
    [Input("inmuebles_dropdown", "value"),
    Input("etapa_dropdown", "value"),
    Input('proyectos_dropdown', 'value'),
    Input('datos_year_rangeslider', 'value'),
    Input('datos_month_rangeslider', 'value')]
)
def calculate_productos_neg(inmueble, etapa, proyecto, year_values, month_values):
    start = timeit.default_timer()
    
    if inmueble == 'Casa':
        df = dm.calc_nro_cotizaciones('neg', inmueble, proyecto, year_values, month_values, etapa=etapa)
    else:
        df = dm.calc_nro_cotizaciones('neg', inmueble, proyecto, year_values, month_values)
    stop = timeit.default_timer()
    print('END PROD CALCULATION','Time: ', stop - start)
    # print(df.head())
    return df.to_json(date_format='iso', orient='split')

@app.callback(
    Output('comp_prod_info', 'children'),
    [Input("inmuebles_dropdown", "value"),
    Input("etapa_dropdown", "value"),
    Input('proyectos_dropdown', 'value'),
    Input('datos_year_rangeslider', 'value'),
    Input('datos_month_rangeslider', 'value')]
)
def calculate_productos_comp(inmueble, etapa, proyecto, year_values, month_values):
    if inmueble == 'Casa':
        df = dm.calc_nro_cotizaciones('comp', inmueble, proyecto, year_values, month_values, etapa=etapa)
    else:
        df = dm.calc_nro_cotizaciones('comp', inmueble, proyecto, year_values, month_values)
    # print(df.head())
    return df.to_json(date_format='iso', orient='split')

##############################################################################################################
@app.callback(
	Output("prueba", 'children'),
	[
	Input('proyectos_dropdown', 'value'),
    ]
)
def etapa_bar_stacked_callback(proyecto,):
    
    if proyecto != None and proyecto != 'TP':
        fig = bar_stacked_graph(proyecto)
        children = [html.Div(
                [
                    html.P("Estados vs Etapas"),
                    dcc.Graph(
                        id="etapa_bar_stacked",
                        figure=fig,
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ])]
        return children
    else:
        return []
    # return bar_stacked_graph(proyecto)

#############################################################################################
@app.callback(
	Output("prod_mas_cotizado", 'children'),
	[Input('cot_prod_info', 'children')]
)

def prod_mas_cotizado(jsondf):
    df = pd.read_json(jsondf, orient='split')
    return df.Programa.head(1)

@app.callback(
    Output("prod_mas_negocio", 'children'),
    [Input('neg_prod_info', 'children')]
)

def prod_mas_negociado(jsondf):
    df = pd.read_json(jsondf, orient='split')
    return df.Programa.head(1)

@app.callback(
    Output("prod_mas_vendido", 'children'),
    [Input('comp_prod_info', 'children')]
)

def prod_mas_vendido(jsondf):
    df = pd.read_json(jsondf, orient='split')
    return df.Programa.head(1)

# ############################################################################################
@app.callback(
    Output("top_prod_cotizados", 'children'),
    [Input('cot_prod_info', 'children')]
)

def prod_mas_cotizado(jsondf):
    df = pd.read_json(jsondf, orient='split')
    columns = ['Numero Unidad', 'Nombre', 'Estado', 'Programa', 'Nro Personas']
    return df_to_table(df[columns].head())

@app.callback(
    Output("top_prod_negociados", 'children'),
    [Input('neg_prod_info', 'children')]
)

def prod_mas_negociado(jsondf):
    df = pd.read_json(jsondf, orient='split')
    columns = ['Numero Unidad', 'Nombre', 'Estado', 'Programa', 'Nro Personas']
    return df_to_table(df[columns].head())

@app.callback(
    Output("top_prod_vendidos", 'children'),
    [Input('comp_prod_info', 'children')]
)

def prod_mas_vendido(jsondf):
    df = pd.read_json(jsondf, orient='split')
    columns = ['Numero Unidad', 'Nombre', 'Estado', 'Programa', 'Nro Personas']
    return df_to_table(df[columns].head())

#############################################################################################
@app.callback(
    Output("prod_menos_cotizado", 'children'),
    [Input('cot_prod_info', 'children')]
)

def prod_menos_cotizado(jsondf):
    df = pd.read_json(jsondf, orient='split')
    return df.Programa.head(1)

@app.callback(
    Output("prod_menos_negocio", 'children'),
    [Input('neg_prod_info', 'children')]
)

def prod_menos_negociado(jsondf):
    df = pd.read_json(jsondf, orient='split')
    return df.Programa.head(1)

@app.callback(
    Output("prod_menos_vendido", 'children'),
    [Input('comp_prod_info', 'children')]
)

def prod_menos_vendido(jsondf):
    df = pd.read_json(jsondf, orient='split')
    return df.Programa.head(1)

# ############################################################################################
@app.callback(
    Output("menor_prod_cotizados", 'children'),
    [Input('cot_prod_info', 'children')]
)

def prod_menor_cotizado(jsondf):
    df = pd.read_json(jsondf, orient='split')
    df = df.sort_values(by='Nro Personas', ascending=True)
    columns = ['Numero Unidad', 'Nombre', 'Estado', 'Programa', 'Nro Personas']
    return df_to_table(df[columns].head())

@app.callback(
    Output("menor_prod_negociados", 'children'),
    [Input('neg_prod_info', 'children')]
)

def prod_menor_negociado(jsondf):
    df = pd.read_json(jsondf, orient='split')
    df = df.sort_values(by='Nro Personas', ascending=True)
    columns = ['Numero Unidad', 'Nombre', 'Estado', 'Programa', 'Nro Personas']
    return df_to_table(df[columns].head())

@app.callback(
    Output("menor_prod_vendidos", 'children'),
    [Input('comp_prod_info', 'children')]
)

def prod_menor_vendido(jsondf):
    df = pd.read_json(jsondf, orient='split')
    df = df.sort_values(by='Nro Personas', ascending=True)
    columns = ['Numero Unidad', 'Nombre', 'Estado', 'Programa', 'Nro Personas']
    return df_to_table(df[columns].head())