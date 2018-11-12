import math
import json

import pandas as pd
import numpy as np
import flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly import graph_objs as go

from app import app, indicator,vertical_indicator, small_indicator, millify, df_to_table
import data_manager as dm

from datetime import datetime as dt
import copy

def line_plot(fechas, periodo):

	entregado = fechas[(fechas['Estado'] == 'Entregado')]
	escriturado = fechas[(fechas['Estado'] == 'Escriturado')]
	reservado = fechas[(fechas['Estado'] == 'Reservado')]
	promesado = fechas[(fechas['Estado'] == 'Promesado')]
	anulado = fechas[(fechas['Estado'] == 'Anulada')]

	entregado = entregado['Total Productos'].resample(periodo).sum()
	escriturado = escriturado['Total Productos'].resample(periodo).sum()
	reservado = reservado['Total Productos'].resample(periodo).sum()
	promesado = promesado['Total Productos'].resample(periodo).sum()
	anulado = anulado['Total Productos'].resample(periodo).sum()
	
	months = fechas.asfreq(periodo).index.month
	years = fechas.asfreq(periodo).index.year
	index = ["{}-{}".format(x,y) for x,y in zip(years,months)]
	# index = pd.to_datetime(index)
	
	trace1 = go.Scatter(
	    x = index,
	    y = entregado,
	    mode = 'lines+markers',
	    name = 'Entregados'
	)

	trace2 = go.Scatter(
	    x = index,
	    y = reservado,
	    mode = 'lines+markers',
	    name = 'Resevado'
	)

	trace3 = go.Scatter(
	    x = index,
	    y = promesado,
	    mode = 'lines+markers',
	    name = 'Promesado'
	)

	trace4 = go.Scatter(
	    x = index,
	    y = escriturado,
	    mode = 'lines+markers',
	    name = 'Ecriturado'
	)

	trace5 = go.Scatter(
	    x = index,
	    y = anulado,
	    mode = 'lines+markers',
	    name = 'Anulado'
	)

	data = [trace1, trace2, trace3, trace4, trace5]

	# Edit the layout
	layout = dict(title = 'Total per {}'.format(periodo),
	              xaxis = dict(title = periodo),
	              yaxis = dict(title = 'Total (UF)'),
	              margin=dict(l=60, r=25, b=40, t=0, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
	              )

	fig = dict(data=data, layout=layout)
	return fig

def violin_plot(cot_all, neg_all):
	x = cot_all['Total Productos'].dropna()
	z = neg_all['Total Productos'].dropna()
	y = neg_all[(neg_all['Estado'] == 'Escriturado') | (neg_all['Estado'] == 'Entregado')]['Total Productos'].dropna()

	trace1 = {
	        "type": 'violin',
	        "y": x,
	        "name": 'Cotizaciones',
	        "box": {
	            "visible": True
	        },
	        "meanline": {
	            "visible": True
	        }
	        }

	trace2 = {
	        "type": 'violin',
	        "y": y,
	        "name": 'Negocios',
	        "box": {
	            "visible": True
	        },
	        "meanline": {
	            "visible": True
	        }
	        }

	trace3 = {
	        "type": 'violin',
	        "y": y,
	        "name": 'Ventas',
	        "box": {
	            "visible": True
	        },
	        "meanline": {
	            "visible": True
	        }
	        }
	
	data = [trace1, trace2, trace3]
	
	layout = go.Layout(
        xaxis=dict(showgrid=False),
        margin=dict(l=35, r=25, b=23, t=20, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
	
	fig = {
	    "data": data,
	    "layout" : layout
	 }
	return fig

layout = [
	# top controls
    html.Div(
            [
                #Proyecto
                html.Div(
                    html.Div(
                        html.Div(
                            [
                            html.P("Inmueble:"),
                            html.Div(
                                dcc.Dropdown(
                                    id="ventas_inmuebles_dropdown",
                                    options=dm.inmb_options,
                                    value="TI",
                                    clearable=False,
                                ),className=''),
                            html.P("Proyecto:"),
                            dcc.Dropdown(
                                id="ventas_proyectos_dropdown",
                                options=[{'label':'Todos', 'value':'TP'}],
                                value="TP",
                                clearable=False,
                            ),

                            ]
                            ,className='row')
                        ,className='three columns'
                    ),
                ),

                #Etapa
                html.Div(
                    html.Div(
                        html.Div(
                            [
                            html.P("Etapa:"),
                            html.Div([
                                dcc.Dropdown(
                                    id="ventas_etapa_dropdown",
                                    options=[{'label':'No disponible', 'value':None}],
                                    value=None,
                                    clearable=False,
                                ),
                                html.P("Unidad Tiempo:"),
	                            html.Div(
                                dcc.Dropdown(
                                    id="period_dropdown",
                                    options=[{'label': 'Anual', 'value': 'A'},
                                             {'label': 'Trimestral', 'value': 'Q'},
                                             {'label': 'Mensual', 'value': 'M'}],
                                    value="M",
                                    clearable=False,
                                ),
                            ), 
	                            ]
                            )
                            ]
                            ,className='row')
                        ,className='three columns'
                    ),
                ),

                html.Div([
                        html.Div(
                            [
                            	# html.P("Unidad Tiempo:"),
                            	html.Div(
                                    dcc.RangeSlider(
                                    id='ventas_year_rangeslider',
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
                            		id='ventas_month_rangeslider',
								    marks={i: '{}'.format(j) for i, j in zip(range(1, 13), dm.months)},
								    min=1,
								    max=12,
								    value=[1,12]
								)
                            	),                          	
                            ]
                            ,className='row', style={'padding':'30'})
                ],className='six columns'),
            ],
            className="row",
            style={"marginBottom": "5"},
    ),
	# Indicators
	html.Div(className="row", children=[
		html.Div(className='three columns',children=[
            vertical_indicator(
				"#00cc96",
                "Total Promesas",
                "total_promesa_indicator",
            ),
            vertical_indicator(
				"#00cc96",
                "Total Reservas",
                "total_reserva_indicator",
            ),
            vertical_indicator(
				"#00cc96",
                "Total Escrituras",
                "total_escritura_indicator",
            ),
            vertical_indicator(
				"#00cc96",
                "Total Entregas",
                "total_entrega_indicator",
            ),
		]),
		html.Div(className='three columns',children=[
			vertical_indicator(
				"#00cc96",
                "UF Promesas",
                "uf_promesa_indicator",
            ),
            vertical_indicator(
				"#00cc96",
                "UF Reservas",
                "uf_reserva_indicator",
            ),
            vertical_indicator(
				"#00cc96",
                "UF Escrituras",
                "uf_escritura_indicator",
            ),
            vertical_indicator(
				"#00cc96",
                "UF Entregas",
                "uf_entrega_indicator",
            ),
		]),
		html.Div(className='six columns',children=[
			html.Div(
           [
            dcc.Graph(
                id="total_uf",
                config=dict(displayModeBar=False),
                style={"height": "90%", "width": "98%"},
            ),
            
           ],className="twelve columns chart_div",
        ),
			
		]),
	]),

	html.Div(
        [
        # Single Column Chart
        html.Div(
           [
            # html.P("Pie Chart"),
            dcc.Graph(
                id="ventas_uf_graph",
                config=dict(displayModeBar=False),
                style={"height": "100%", "width": "98%"},
            ),
           ],className="twelve columns chart_div",
        ),
        #Double Column Chart
  		],
  		className="row",
   		style={"marginTop": "5px"},
    ),
]


@app.callback(
    Output('ventas_proyectos_dropdown', 'options'),
    [
    Input('ventas_inmuebles_dropdown', 'value')]
    )
def inmuebles_dropdown_callback(inmueble):
    proyectos = dm.get_proyectos_in_inmueble('neg', inmueble)
    return proyectos

# etapa depende de inmueble y data y proyecto para recuperar los datos
@app.callback(
    Output('ventas_etapa_dropdown', 'options'),
    [
    Input('ventas_inmuebles_dropdown', 'value'),
    Input('ventas_proyectos_dropdown', 'value')]
    )
def etapa_dropdown_callback(inmueble, proyecto):
    if inmueble == 'Casa':
        return dm.get_etapa_in_proyecto('neg', inmueble, proyecto) 
    else:
        return [{'label':'No disponible', 'value':None}] 


# #####################################################################################

@app.callback(
	Output("total_uf", 'figure'),
	[Input('ventas_proyectos_dropdown', 'value'),
	Input('ventas_inmuebles_dropdown', 'value'),
	Input('ventas_etapa_dropdown', 'value'),
	Input('ventas_year_rangeslider', 'value'),
	Input('ventas_month_rangeslider', 'value')]
)
def total_uf_callback(proyecto, inmueble, etapa, year_values, month_values):
	if inmueble == 'Casa':
		cot_all = dm.get_data_whithin_dates('cot', proyecto, inmueble, year_values, month_values, etapa)
		neg_all = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values, etapa)
	else:
		cot_all = dm.get_data_whithin_dates('cot', proyecto, inmueble, year_values, month_values)
		neg_all = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values)


	return violin_plot(cot_all, neg_all)


@app.callback(
	Output('ventas_uf_graph', 'figure'),
	[Input('ventas_proyectos_dropdown', 'value'),
	Input('ventas_inmuebles_dropdown', 'value'),
	Input('ventas_etapa_dropdown', 'value'),
	Input('period_dropdown', 'value'),
	Input('ventas_year_rangeslider', 'value'),
	Input('ventas_month_rangeslider', 'value')]
)
def ventas_uf_graph_callback(proyecto, inmueble, etapa, periodo, year_values, month_values):
	if inmueble == 'Casa':
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values, etapa)
	else:
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values)

	return line_plot(fechas, periodo)

####################################################################
@app.callback(
	Output('total_reserva_indicator', 'children'),
	[Input('ventas_proyectos_dropdown', 'value'),
	Input('ventas_inmuebles_dropdown', 'value'),
	Input('ventas_etapa_dropdown', 'value'),
	Input('ventas_year_rangeslider', 'value'),
	Input('ventas_month_rangeslider', 'value')]
)
def total_reserva_callback(proyecto, inmueble, etapa, year_values, month_values):
	
	if inmueble == 'Casa':
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values, etapa)
	else:
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values)

	# fechas = dm.get_data_whithin_dates('neg', proyecto, etapa, year_values, month_values)
	count = fechas[fechas['Estado']=='Reservado']['Estado'].count()
	return count

@app.callback(
	Output('total_entrega_indicator', 'children'),
	[Input('ventas_proyectos_dropdown', 'value'),
	Input('ventas_inmuebles_dropdown', 'value'),
	Input('ventas_etapa_dropdown', 'value'),
	Input('ventas_year_rangeslider', 'value'),
	Input('ventas_month_rangeslider', 'value')]
)
def total_entrega_callback(proyecto, inmueble, etapa, year_values, month_values):
	if inmueble == 'Casa':
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values, etapa)
	else:
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values)
	count = fechas[fechas['Estado']=='Entregado']['Estado'].count()
	return count

@app.callback(
	Output('total_escritura_indicator', 'children'),
	[Input('ventas_proyectos_dropdown', 'value'),
	Input('ventas_inmuebles_dropdown', 'value'),
	Input('ventas_etapa_dropdown', 'value'),
	Input('ventas_year_rangeslider', 'value'),
	Input('ventas_month_rangeslider', 'value')])
def total_escritura_callback(proyecto, inmueble, etapa, year_values, month_values):
	if inmueble == 'Casa':
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values, etapa)
	else:
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values)
	count = fechas[fechas['Estado']=='Escriturado']['Estado'].count()
	return count

@app.callback(
	Output('total_promesa_indicator', 'children'),
	[Input('ventas_proyectos_dropdown', 'value'),
	Input('ventas_inmuebles_dropdown', 'value'),
	Input('ventas_etapa_dropdown', 'value'),
	Input('ventas_year_rangeslider', 'value'),
	Input('ventas_month_rangeslider', 'value')])
def total_promesa_callback(proyecto, inmueble, etapa, year_values, month_values):
	if inmueble == 'Casa':
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values, etapa)
	else:
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values)
	count = fechas[fechas['Estado']=='Promesado']['Estado'].count()
	return count


# #######################################################################
@app.callback(
	Output('uf_reserva_indicator', 'children'),
	[Input('ventas_proyectos_dropdown', 'value'),
	Input('ventas_inmuebles_dropdown', 'value'),
	Input('ventas_etapa_dropdown', 'value'),
	Input('ventas_year_rangeslider', 'value'),
	Input('ventas_month_rangeslider', 'value')])
def uf_reserva_callback(proyecto, inmueble, etapa, year_values, month_values):
	if inmueble == 'Casa':
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values, etapa)
	else:
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values)
	count = fechas[fechas['Estado']=='Reservado']['Total Productos'].sum()
	count = np.round(count,2)
	return millify(count)

@app.callback(
	Output('uf_entrega_indicator', 'children'),
	[Input('ventas_proyectos_dropdown', 'value'),
	Input('ventas_inmuebles_dropdown', 'value'),
	Input('ventas_etapa_dropdown', 'value'),
	Input('ventas_year_rangeslider', 'value'),
	Input('ventas_month_rangeslider', 'value')])
def uf_entrega_callback(proyecto, inmueble, etapa, year_values, month_values):
	if inmueble == 'Casa':
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values, etapa)
	else:
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values)
	count = fechas[fechas['Estado']=='Entregado']['Total Productos'].sum()
	count = np.round(count,2)
	return millify(count)

@app.callback(
	Output('uf_escritura_indicator', 'children'),
	[Input('ventas_proyectos_dropdown', 'value'),
	Input('ventas_inmuebles_dropdown', 'value'),
	Input('ventas_etapa_dropdown', 'value'),
	Input('ventas_year_rangeslider', 'value'),
	Input('ventas_month_rangeslider', 'value')])
def uf_escritura_callback(proyecto, inmueble, etapa, year_values, month_values):
	if inmueble == 'Casa':
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values, etapa)
	else:
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values)
	count = fechas[fechas['Estado']=='Escriturado']['Total Productos'].sum()
	count = np.round(count,2)
	return millify(count)

@app.callback(
	Output('uf_promesa_indicator', 'children'),
	[Input('ventas_proyectos_dropdown', 'value'),
	Input('ventas_inmuebles_dropdown', 'value'),
	Input('ventas_etapa_dropdown', 'value'),
	Input('ventas_year_rangeslider', 'value'),
	Input('ventas_month_rangeslider', 'value')])
def uf_promesa_callback(proyecto, inmueble, etapa, year_values, month_values):
	if inmueble == 'Casa':
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values, etapa)
	else:
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values)
	count = fechas[fechas['Estado']=='Promesado']['Total Productos'].sum()
	count = np.round(count,2)
	return millify(count)

