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

def bar_stacked_graph(proyecto):
    
    proyecto = proyecto
    products = dm.productos
    prod_sdv = products[products.Proyecto == proyecto]
	# prod_sdv.Etapa.unique()

    top_labels = prod_sdv.Estado.unique()

    y_data = prod_sdv.Etapa.unique()


    x_data = []

    for etapa in prod_sdv.Etapa.unique():
	    p = prod_sdv[prod_sdv.Etapa == etapa]
	    values = []
	    for estado in prod_sdv.Estado.unique():
	        per = p[p['Estado'] == estado]['Estado'].count()/p.shape[0]
	        per = float(("%.2f"% per))
	        values.append(per)
	    x_data.append(values)

    colors = ['rgba(38, 24, 74, 0.8)', 'rgba(71, 58, 131, 0.8)',
	          'rgba(122, 120, 168, 0.8)', 'rgba(164, 163, 204, 0.85)',
	          'rgba(190, 192, 213, 1)', 'rgb(210, 226, 241)','rgb(234, 232, 253)']


    traces = []

    for i in range(0, len(x_data[0])):
	    j=1
	    for xd, yd in zip(x_data, y_data):
	        if j > 1: 
	            sl = False
	        else:
	            sl=True
	        j+=1
	        traces.append(go.Bar(
	            x=[xd[i]],
	            y=[yd],
	            orientation='h',
	            marker=dict(
	                color=colors[i],
	                line=dict(
	                        color='rgb(248, 248, 249)',
	                        width=1)
	            ),
	            name = top_labels[i],
	            showlegend=sl
	        ))

    layout = go.Layout(
	    xaxis=dict(
	        showgrid=False,
	        showline=False,
	        showticklabels=False,
	        zeroline=False,
	        domain=[0.15, 1]
	    ),
	    yaxis=dict(
	        showgrid=False,
	        showline=False,
	        showticklabels=False,
	        zeroline=False,
	    ),
	    barmode='stack',
	    paper_bgcolor="white",
        plot_bgcolor="white",
	    # margin=dict(l=120,r=10,t=140,b=80),
	    margin=dict(t=10, l=100, b=85, pad=4),
	    showlegend=True,
	    # legend=dict(orientation="h")
	)

    annotations = []

    for yd, xd in zip(y_data, x_data):
	    # labeling the y-axis
	    annotations.append(dict(xref='paper', yref='y',
	                            x=0.14, y=yd,
	                            xanchor='right',
	                            text=str(yd),
	                            font=dict(family='Arial', size=14,
	                                      color='rgb(67, 67, 67)'),
	                            showarrow=False, align='right'))

    layout['annotations'] = annotations

    fig = go.Figure(data=traces, layout=layout)
    return fig

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

    
]



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
	[Input("inmuebles_dropdown", "value"),
	Input("etapa_dropdown", "value"),
	Input('proyectos_dropdown', 'value'),
	Input('datos_year_rangeslider', 'value'),
	Input('datos_month_rangeslider', 'value')
	]
)

def prod_mas_cotizado(inmueble, etapa, proyecto, year_values, month_values):
	if inmueble == 'Casa':
			top = dm.get_prod_mas_cotizado_persona('cot', proyecto, etapa)
	else:
			top = dm.get_prod_mas_cotizado_persona('cot', proyecto)
	
	return top.Programa

@app.callback(
	Output("prod_mas_negocio", 'children'),
	[Input("inmuebles_dropdown", "value"),
	Input("etapa_dropdown", "value"),
	Input('proyectos_dropdown', 'value'),
	Input('datos_year_rangeslider', 'value'),
	Input('datos_month_rangeslider', 'value')
	]
)

def prod_mas_negocio(inmueble, etapa, proyecto, year_values, month_values):
	if inmueble == 'Casa':
			top = dm.get_prod_mas_cotizado_persona('neg', proyecto, etapa)
	else:
			top = dm.get_prod_mas_cotizado_persona('neg', proyecto)
	
	return top.Programa

@app.callback(
	Output("prod_mas_vendido", 'children'),
	[Input("inmuebles_dropdown", "value"),
	Input("etapa_dropdown", "value"),
	Input('proyectos_dropdown', 'value'),
	Input('datos_year_rangeslider', 'value'),
	Input('datos_month_rangeslider', 'value')
	]
)

def prod_mas_compra(inmueble, etapa, proyecto, year_values, month_values):
	if inmueble == 'Casa':
			top = dm.get_prod_mas_cotizado_persona('comp', proyecto, etapa)
	else:
			top = dm.get_prod_mas_cotizado_persona('comp', proyecto)
	
	return top.Programa

############################################################################################
@app.callback(
	Output("prod_menos_cotizado", 'children'),
	[Input("inmuebles_dropdown", "value"),
	Input("etapa_dropdown", "value"),
	Input('proyectos_dropdown', 'value'),
	Input('datos_year_rangeslider', 'value'),
	Input('datos_month_rangeslider', 'value')
	]
)

def prod_menos_cotizado(inmueble, etapa, proyecto, year_values, month_values):
	if inmueble == 'Casa':
			top = dm.get_prod_mas_cotizado_persona('cot', proyecto, etapa, ascending=True)
	else:
			top = dm.get_prod_mas_cotizado_persona('cot', proyecto, ascending=True)
	
	return top.Programa

@app.callback(
	Output("prod_menos_negocio", 'children'),
	[Input("inmuebles_dropdown", "value"),
	Input("etapa_dropdown", "value"),
	Input('proyectos_dropdown', 'value'),
	Input('datos_year_rangeslider', 'value'),
	Input('datos_month_rangeslider', 'value')
	]
)

def prod_menos_negocio(inmueble, etapa, proyecto, year_values, month_values):
	if inmueble == 'Casa':
			top = dm.get_prod_mas_cotizado_persona('neg', proyecto, etapa, ascending=True)
	else:
			top = dm.get_prod_mas_cotizado_persona('neg', proyecto, ascending=True)
	
	return top.Programa

@app.callback(
	Output("prod_menos_vendido", 'children'),
	[Input("inmuebles_dropdown", "value"),
	Input("etapa_dropdown", "value"),
	Input('proyectos_dropdown', 'value'),
	Input('datos_year_rangeslider', 'value'),
	Input('datos_month_rangeslider', 'value')
	]
)

def prod_menos_compra(inmueble, etapa, proyecto, year_values, month_values):
	if inmueble == 'Casa':
			top = dm.get_prod_mas_cotizado_persona('comp', proyecto, etapa, ascending=True)
	else:
			top = dm.get_prod_mas_cotizado_persona('comp', proyecto, ascending=True)
	
	return top.Programa

############################################################################################

@app.callback(
	Output("top_prod_cotizados", 'children'),
	[Input("inmuebles_dropdown", "value"),
	Input("etapa_dropdown", "value"),
	Input('proyectos_dropdown', 'value'),
	Input('datos_year_rangeslider', 'value'),
	Input('datos_month_rangeslider', 'value')
	]
)
def top_prod_cotizados(inmueble, etapa, proyecto, year_values, month_values):
	if inmueble == 'Casa':
			top = dm.get_prod_mas_cotizado_persona('cot', proyecto, etapa, q=5)
	else:
			top = dm.get_prod_mas_cotizado_persona('cot', proyecto, q=5)
	
	columns = ['Numero Unidad', 'Nombre', 'Estado', 'Programa', 'Nro Personas']
	table = df_to_table(top[columns])
	return table

@app.callback(
	Output("top_prod_negociados", 'children'),
	[Input("inmuebles_dropdown", "value"),
	Input("etapa_dropdown", "value"),
	Input('proyectos_dropdown', 'value'),
	Input('datos_year_rangeslider', 'value'),
	Input('datos_month_rangeslider', 'value')
	]
)
def top_prod_negociados(inmueble, etapa, proyecto, year_values, month_values):
	if inmueble == 'Casa':
			top = dm.get_prod_mas_cotizado_persona('neg', proyecto, etapa, q=5)
	else:
			top = dm.get_prod_mas_cotizado_persona('neg', proyecto, q=5)
	
	columns = ['Numero Unidad', 'Nombre', 'Estado', 'Programa', 'Nro Personas']
	table = df_to_table(top[columns])
	return table

@app.callback(
	Output("top_prod_vendidos", 'children'),
	[Input("inmuebles_dropdown", "value"),
	Input("etapa_dropdown", "value"),
	Input('proyectos_dropdown', 'value'),
	Input('datos_year_rangeslider', 'value'),
	Input('datos_month_rangeslider', 'value')
	]
)
def top_prod_negociados(inmueble, etapa, proyecto, year_values, month_values):
	if inmueble == 'Casa':
			top = dm.get_prod_mas_cotizado_persona('comp', proyecto, etapa, q=5)
	else:
			top = dm.get_prod_mas_cotizado_persona('comp', proyecto, q=5)
	
	columns = ['Numero Unidad', 'Nombre', 'Estado', 'Programa', 'Nro Personas']
	table = df_to_table(top[columns])
	return table

############################################################################################

@app.callback(
	Output("menor_prod_cotizados", 'children'),
	[Input("inmuebles_dropdown", "value"),
	Input("etapa_dropdown", "value"),
	Input('proyectos_dropdown', 'value'),
	Input('datos_year_rangeslider', 'value'),
	Input('datos_month_rangeslider', 'value')
	]
)
def menor_prod_cotizados(inmueble, etapa, proyecto, year_values, month_values):
	if inmueble == 'Casa':
			top = dm.get_prod_mas_cotizado_persona('cot', proyecto, etapa, q=5, ascending=True)
	else:
			top = dm.get_prod_mas_cotizado_persona('cot', proyecto, q=5, ascending=True)
	
	columns = ['Numero Unidad', 'Nombre', 'Estado', 'Programa', 'Nro Personas']
	table = df_to_table(top[columns])
	return table

@app.callback(
	Output("menor_prod_negociados", 'children'),
	[Input("inmuebles_dropdown", "value"),
	Input("etapa_dropdown", "value"),
	Input('proyectos_dropdown', 'value'),
	Input('datos_year_rangeslider', 'value'),
	Input('datos_month_rangeslider', 'value')
	]
)
def menor_prod_negociados(inmueble, etapa, proyecto, year_values, month_values):
	if inmueble == 'Casa':
			top = dm.get_prod_mas_cotizado_persona('neg', proyecto, etapa, q=5, ascending=True)
	else:
			top = dm.get_prod_mas_cotizado_persona('neg', proyecto, q=5, ascending=True)
	
	columns = ['Numero Unidad', 'Nombre', 'Estado', 'Programa', 'Nro Personas']
	table = df_to_table(top[columns])
	return table

@app.callback(
	Output("menor_prod_vendidos", 'children'),
	[Input("inmuebles_dropdown", "value"),
	Input("etapa_dropdown", "value"),
	Input('proyectos_dropdown', 'value'),
	Input('datos_year_rangeslider', 'value'),
	Input('datos_month_rangeslider', 'value')
	]
)
def menor_prod_negociados(inmueble, etapa, proyecto, year_values, month_values):
	if inmueble == 'Casa':
			top = dm.get_prod_mas_cotizado_persona('comp', proyecto, etapa, q=5, ascending=True)
	else:
			top = dm.get_prod_mas_cotizado_persona('comp', proyecto, q=5, ascending=True)
	
	columns = ['Numero Unidad', 'Nombre', 'Estado', 'Programa', 'Nro Personas']
	table = df_to_table(top[columns])
	return table