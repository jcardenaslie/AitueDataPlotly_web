import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import plotly.graph_objs as go

app = dash.Dash()
# Boostrap CSS.
app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})
# app.css.append_css({
#     "external_url": "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
# })

# app.css.append_css({
#     "external_url": 'https://codepen.io/chriddyp/pen/bWLwgP.css'
# })

# app.scripts.append_script({
#     "external_url": "https://code.jquery.com/jquery-3.2.1.min.js"
# })

# app.scripts.append_script({
#     "external_url": "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"
# })

df = pd.read_excel('cotizaciones_all.xlsx')

def generate_table(dataframe, proyecto='Todos los Proyectos', max_rows=10):
    if filter != 'Todos los Proyectos':
            dataframe = dataframe[dataframe['Proyecto'] == proyecto]

    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr(
            [
                html.Td(dataframe.iloc[i][col]) 
                for col in dataframe.columns
            ]) 
        for i in range(min(len(dataframe), max_rows))]
    )


#  Layouts
layout_table = dict(
    autosize=True,
    height=500,
    font=dict(color="#191A1A"),
    titlefont=dict(color="#191A1A", size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor='#fffcfc',
    paper_bgcolor='#fffcfc',
    legend=dict(font=dict(size=10), orientation='h'),
)

proyectos = df.Proyecto.unique()
options = []

map_data = df

for p in proyectos:
    options.append({'label':p, 'value': p})
options.append({'label':'Todos los Proyectos', 'value': 'TP'})



app.layout = html.Div(children=[
    #Upload
    html.Div([
        html.Div([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=True
            ),
        ], className=" twelve columns"),
    ], className="row"),
    #Data Controllers
    html.Div([
        html.Div(id='output-data-upload'),
        html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),

        html.Label('Proyectos'),
        dcc.Dropdown(
            id='proyectos_dropdown',
            options=options,
            value='TP',
            multi=True,
        ),
       
        html.Div(id='proyectos_dropdown_label'),
        
        html.Div(id='filas_cantidad'),
        html.Label('Cantidad de Filas a ver'),

        dcc.Slider(
            id='slider_filas',
            min=10,
            max=map_data.shape[0],
            step=50,
            # marks={i: 'Label {}'.format(i) if i == 1 else str(i) for i in range(1, 6)},
            value=5,
        ),
        html.Div(id='slider_output'),
    ], className="row"),
    #Visualizacion Tabla
    html.Div([
        html.H4(children='Cotizaciones'),
        html.Div(
            [
                dt.DataTable(
                        rows=map_data[:10].to_dict('records'),
                        columns=map_data.columns,
                        row_selectable=True,
                        filterable=True,
                        sortable=True,
                        selected_row_indices=[],
                        id='datatable'),
            ],
            style = layout_table,
            className="twelve columns"
        ),
    ], className="row"),
    
    html.Div([
        html.H1('Dash Tabs component demo'),
        dcc.Tabs(id="tabs-example", value='tab-1-example', children=[
            dcc.Tab(label='Tab One', value='tab-1-example'),
            dcc.Tab(label='Tab Two', value='tab-2-example'),
        ]),
        html.Div(id='tabs-content-example')
    ], className="row"),

])

def get_data(columns):
    map_aux = map_data.copy()
    if 'TP' not in columns:
        map_aux = map_aux[map_aux['Proyecto'].isin(columns)]
    return map_aux


@app.callback(Output('tabs-content-example', 'children'),
              [Input('tabs-example', 'value')])
def render_content(tab):
    if tab == 'tab-1-example':
        return html.Div([
            html.H3('Tab content 1'),
            dcc.Graph(
                id='graph-1-tabs',
                figure={
                    'data': [{
                        'x': [1, 2, 3],
                        'y': [3, 1, 2],
                        'type': 'bar'
                    }]
                }
            )
        ])
    elif tab == 'tab-2-example':
        return html.Div([
            html.H3('Tab content 2'),
            dcc.Graph(
                id='graph-2-tabs',
                figure={
                    'data': [{
                        'x': [1, 2, 3],
                        'y': [5, 10, 6],
                        'type': 'bar'
                    }]
                }
            )
        ])

#Callback Proyectos Dropdown
@app.callback(
    Output('proyectos_dropdown_label', 'children'),
    [Input('proyectos_dropdown', 'value')])
def callback_proyecto_selected(dropdown_value):
    if dropdown_value:
        return 'Proyectos seleccionados "{}"'.format(dropdown_value)
    else:
        return 'Proyectos seleccionados "{}"'.format([{}])

# #Callback Cantidad Filas
@app.callback(
    Output('filas_cantidad', 'children'),
    [dash.dependencies.Input('proyectos_dropdown', 'value')])
def callback_cantidad_filas(dropdown_value):
    data_aux = get_data(dropdown_value)
    q = data_aux.shape[0]
    return 'Filas: {}'.format(q)

# Callback a Label Slider "Viendo....
@app.callback(
    Output('slider_output', 'children'),
    [Input('slider_filas', 'value'),
    Input('proyectos_dropdown', 'value')])
def callback_slider_cantidad_filas(slider_value, dropdown_b):
    data_aux = get_data(dropdown_b)
    total_rows = data_aux.shape[0]
    print(slider_value)
    return 'Viendo {} filas de {}'.format(slider_value, total_rows)
    # return 'Proyectos seleccionados "{}"'.format(dropdown_value)

# Callback a Slider
@app.callback(
    Output('slider_filas', 'max'),
    [Input('proyectos_dropdown', 'value')])
def callback_slider_max(proyectos_dropdown):
    data_aux = get_data(proyectos_dropdown)
    total_rows = data_aux.shape[0]
    return total_rows

# Callback a Slider
@app.callback(
    Output('slider_filas', 'value'),
    [Input('proyectos_dropdown', 'value')])
def callback_slider_min(proyectos_dropdown):
    return 10

# #Callback a elemento: datatable
@app.callback(
   Output('datatable', 'rows'),
    [Input('proyectos_dropdown', 'value'),
    Input('slider_filas', 'value')
    ])
def update_selected_row_indices(dropdown_b, slider):
    data_aux = get_data(dropdown_b)
    rows = data_aux[:slider].to_dict('records')
    return rows

if __name__ == '__main__':
    app.run_server(debug=True)