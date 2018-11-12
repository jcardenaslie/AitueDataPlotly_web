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

def bar_period_chart(period, proyecto):
    cot_all = dm.data_change('cot')
    neg_all = dm.data_change('neg')
    comp_all = dm.data_change('comp')

    if proyecto != 'TP':
        cot_all = cot_all[cot_all['Proyecto'] == proyecto]
        neg_all = neg_all[neg_all['Proyecto'] == proyecto]
        comp_all = comp_all[comp_all['Proyecto'] == proyecto]

    data = []
    cot_all['count'] = 1
    cot_all.set_index(pd.to_datetime(cot_all['Fecha Cotizacion']), inplace=True)
    cot_fecha = cot_all.resample(period).sum()

    y = cot_fecha['count'].tolist()
    x = cot_fecha.index.tolist()

    trace = go.Bar(
	    x=x,
	    y=y,
	    name='Cotizaciones',
	    marker=dict(
	        color='rgb(55, 83, 109)'
	    )
    )

    data.append(trace)

    neg_all['count'] = 1
    neg_all.set_index(pd.to_datetime(neg_all['Fecha Cotizacion']), inplace=True)
    neg_fecha = neg_all.resample(period).sum()

    y = neg_fecha['count'].tolist()
    x = neg_fecha.index.tolist()

    trace = go.Bar(
	    x=x,
	    y=y,
	    name='Negocios',
	    marker=dict(
	        color='rgb(26, 118, 255)'
	    )
    )

    data.append(trace)

    comp_all['count'] = 1
    comp_all.set_index(pd.to_datetime(comp_all['Fecha Cotizacion']), inplace=True)
    comp_fecha = comp_all.resample(period).sum()

    y = comp_fecha['count'].tolist()
    x = comp_fecha.index.tolist()

    trace = go.Bar(
        x=x,
        y=y,
        name='Negocios',
        marker=dict(
            color='rgb(122, 234, 255)'
        )
    )

    data.append(trace)

    layout = go.Layout(
	#         barmode="stack",
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
                size=10,
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
            x=1.2,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)',
            font=dict(size=12)
        ),
        barmode='stack',
        bargap=0.15,
        bargroupgap=0.1
    )
    return {'data':data, 'layout':layout}


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