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

def bar_period_chart(period, proyecto):
	cot_all = dm.data_change('cot')
	neg_all = dm.data_change('neg')

	if proyecto != 'TP':
		cot_all = cot_all[cot_all['Proyecto'] == proyecto]
		neg_all = neg_all[neg_all['Proyecto'] == proyecto]

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
                        id="chart_type_dropdown",
                        options=[{'label': 'Pie Chart', 'value': 'pie'},
                                 {'label': 'Bar Chart', 'value': 'bar'}],
                        value="pie",
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
    # Headers
	html.Div(
    [
    	html.H3(children='Cotizaciones',className="six columns" ),
    	html.H3(children='Negocios',className="six columns" ),
    ],className="row",
            style={"marginBottom": "5"},
    ),
	
    # First Compare Figure
    html.Div(
        [
        # Single Column Chart
        html.Div(
           [
            html.P("Pie Chart"),
            dcc.Graph(
                id="cot_graph1",
                config=dict(displayModeBar=False),
                style={"height": "89%", "width": "98%"},
            ),
           ],className="six columns chart_div",
        ),
        #Double Column Chart
        html.Div(
            [
            html.P("Pie Chart"),
            dcc.Graph(
                id="neg_graph1",
                config=dict(displayModeBar=False),
                style={"height": "89%", "width": "98%"},
            ),
            ],className="six columns chart_div"
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
            html.P("Bar Chart"),
            dcc.Graph(
                id="cot_graph2",
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
                id="neg_graph2",
                config=dict(displayModeBar=False),
                style={"height": "89%", "width": "98%"},
            ),
            ],className="six columns chart_div"
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



@app.callback(
    Output("cot_graph1", "figure"),
    [
    	Input("proyectos_dropdown", "children"),
        Input("proyectos_dropdown", "value"),
        Input("column1_dropdown", "value"),
    ],
)
def cot_graph1_callback(children, proyecto, col1):
    tmp_data = dm.data_change('cot')
    if proyecto != 'TP':
        tmp_data = tmp_data[tmp_data['Proyecto'] == proyecto]
    return pie_chart(tmp_data, col1)

@app.callback(
    Output('cot_graph2', 'figure'),
    [
	Input("proyectos_dropdown", "children"),
    Input("column1_dropdown", 'value'),
     Input("column2_dropdown", 'value'),
     Input("proyectos_dropdown", "value")
     ]
)
def cot_graph2_callback(children, column1, column2, proyecto):
    tmp_data = dm.data_change('cot')
    if proyecto != 'TP':
        tmp_data = tmp_data[tmp_data['Proyecto'] == proyecto]
    return categorical_columnbycolumn(column1, column2, tmp_data)

@app.callback(
    Output("neg_graph1", "figure"),
    [
    	Input("proyectos_dropdown", "children"),
        Input("proyectos_dropdown", "value"),
        Input("column1_dropdown", "value"),
    ],
)
def neg_graph1_callback(children, proyecto, col1):
    tmp_data = dm.data_change('neg')
    if proyecto != 'TP':
        tmp_data = tmp_data[tmp_data['Proyecto'] == proyecto]
    return pie_chart(tmp_data, col1)

@app.callback(
    Output('neg_graph2', 'figure'),
    [
	Input("proyectos_dropdown", "children"),
    Input("column1_dropdown", 'value'),
     Input("column2_dropdown", 'value'),
     Input("proyectos_dropdown", "value")
     ]
)
def neg_graph2_callback(children, column1, column2, proyecto):
    tmp_data = dm.data_change('neg')
    if proyecto != 'TP':
        tmp_data = tmp_data[tmp_data['Proyecto'] == proyecto]
    return categorical_columnbycolumn(column1, column2, tmp_data)

@app.callback(
    Output("cot_neg_period", "figure"),
    [
        Input("proyectos_dropdown", "value"),
        Input("period_dropdown", "value"),
    ],
)
def cases_period_callback(proyecto, periodo):
    return bar_period_chart(periodo, proyecto)