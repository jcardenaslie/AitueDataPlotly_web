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
from utils.figures import line_plot, violin_plot

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

    html.Div(className='row',style={"margin-bottom":'5px'}, children=[
    	    html.Div(
		    	html.Div(
		    		className='six columns',
			    	style={
						    "border":"1px solid #C8D4E3",
						    "border-radius": "3px",
						    "background-color": "white",
						    "height":"100px",
						    "vertical-align":"middle",
						    "text-align":"center",
			    	},
		    		children=[
		    			html.P("Total Ventas (Unidades)", style={"font-size":"18px"}),
		    			html.P("0", id='total_ventas_unidades', style={"color": "#2a3f5f","font-size": "40px"}),
		    		],
		    	),
    		),
    	    html.Div(
		    	html.Div(
		    		className='six columns',
			    	style={
						    "border":"1px solid #C8D4E3",
						    "border-radius": "3px",
						    "background-color": "white",
						    "height":"100px",
						    "vertical-align":"middle",
						    "text-align":"center",
			    	},
		    		children=[
		    			html.P("Total Ventas (UF)", style={"font-size":"18px"}),
		    			html.P("0", id='total_ventas_uf', style={"color": "#2a3f5f","font-size": "40px"}),
		    		],
		    	),
    		),
    		
   	]),


	# Indicators
	html.Div(className="row", children=[
		html.Div(className='two columns',children=[
            vertical_indicator(
				"#00cc96",
                "Total Entregas",
                "total_entrega_indicator",
                bg_color='#CAFFD8'
            ),
            vertical_indicator(
				"#00cc96",
                "Total Escrituras",
                "total_escritura_indicator",
                bg_color='#CFFEF0'
            ),
            vertical_indicator(
				"#00cc96",
                "Total Reservas",
                "total_reserva_indicator",
                bg_color='#E1FFFE'
            ),
            vertical_indicator(
				"#00cc96",
                "Total Promesas",
                "total_promesa_indicator",
                bg_color='#E6FCFF'
            ),
		]),
		html.Div(className='two columns',children=[
			vertical_indicator(
				"#00cc96",
                "UF Entregas",
                "uf_entrega_indicator",
                bg_color='#CAFFD8'
            ),
            vertical_indicator(
				"#00cc96",
                "UF Escrituras",
                "uf_escritura_indicator",
                bg_color='#CFFEF0'
            ),
            vertical_indicator(
				"#00cc96",
                "UF Reservas",
                "uf_reserva_indicator",
                bg_color='#E1FFFE'
            ),
			vertical_indicator(
				"#00cc96",
                "UF Promesas",
                "uf_promesa_indicator",
                bg_color='#E6FCFF'
            ),

            
            
		]),

		html.Div(className='eight columns',children=[
			html.Div(
           [
            dcc.Graph(
                id="total_uf",
                config=dict(displayModeBar=False),
                style={"height": "90%", "width": "98%"},
            ),
            
           ],className="row chart_div",
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



###################################################################################################
#CONTROLES
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
# VIOLIN
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

#LINE
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
# UNIDADES
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

#######################################################################################################
@app.callback(
	Output("total_ventas_unidades", "children"),
	[Input('ventas_proyectos_dropdown', 'value'),
	Input('ventas_inmuebles_dropdown', 'value'),
	Input('ventas_etapa_dropdown', 'value'),
	Input('ventas_year_rangeslider', 'value'),
	Input('ventas_month_rangeslider', 'value')]
	)
def total_ventas_uf(proyecto, inmueble, etapa, year_values, month_values):
	if inmueble == 'Casa':
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values, etapa)
	else:
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values)
	escriturados_q = fechas[fechas['Estado']=='Escriturado']['Estado'].count()
	entregados_q = fechas[fechas['Estado']=='Entregado']['Estado'].count()
	count = escriturados_q + entregados_q 
	return count

@app.callback(
	Output("total_ventas_uf", "children"),
	[Input('ventas_proyectos_dropdown', 'value'),
	Input('ventas_inmuebles_dropdown', 'value'),
	Input('ventas_etapa_dropdown', 'value'),
	Input('ventas_year_rangeslider', 'value'),
	Input('ventas_month_rangeslider', 'value')]
	)
def total_ventas_uf(proyecto, inmueble, etapa, year_values, month_values):
	if inmueble == 'Casa':
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values, etapa)
	else:
		fechas = dm.get_data_whithin_dates('neg', proyecto, inmueble, year_values, month_values)
	
	escriturados_q = fechas[fechas['Estado']=='Escriturado']['Total Productos'].sum()
	entregados_q = fechas[fechas['Estado']=='Entregado']['Total Productos'].sum()
	count = escriturados_q + entregados_q 
	print(count)
	return round(count,0)

# #######################################################################
# UF
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

