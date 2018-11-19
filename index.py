import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from app import app

from apps import data, versus, ventas, productos


app.layout = html.Div(children=[
        # header
        html.Div([

            html.Span("AITUE DASH", className='app-title'),
            
            html.Div(
                html.Img(src='data:image/png;base64,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',height="100%")
                # html.Img(src='aitue.png',height="100%")
                ,style={"float":"right","height":"100%"})
            ],className="row header"
        ),

        # tabs
        html.Div([
            dcc.Tabs(
                id="tabs",
                style={"height":"20","verticalAlign":"middle"},
                children=[
                    dcc.Tab(label="Ventas", value="ventas_tab"),
                    dcc.Tab(label="Productos", value="prod_tab"),
                    dcc.Tab(id="data_tab", label="Datos", value="data_tab"),
                    dcc.Tab(label="Cotización vs Negocios", value="versus_tab"),
                    
                ],
                value="ventas_tab",
            )

            ],className="row tabs_div"
        ),
        
        html.Div(id="tab_content", className="row", style={"margin": "2% 3%"}),
        html.Link(href="/static/s4.css", rel="stylesheet"),
        html.Link(href="https://use.fontawesome.com/releases/v5.2.0/css/all.css",rel="stylesheet"),
        html.Link(href="https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css",rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Dosis", rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Open+Sans", rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Ubuntu", rel="stylesheet"),
        html.Link(href="https://cdn.rawgit.com/amadoukane96/8a8cfdac5d2cecad866952c52a70a50e/raw/cd5a9bf0b30856f4fc7e3812162c74bfc0ebe011/dash_crm.css", rel="stylesheet")  
    ],className="row",
    style={"margin": "0%"},
)


@app.callback(
    Output("tab_content", "children"), 
    [Input("tabs", "value")]
)

def render_content(tab):
    if tab == "data_tab":
        return data.layout
        pass
    elif tab == "versus_tab":
        pass
        return versus.layout
    elif tab == "ventas_tab":
        return ventas.layout
        pass
    elif tab == "prod_tab":
        return productos.layout
        pass
    else:
        pass
        # return opportunities.layout

if __name__ == '__main__':
    app.run_server(debug=True)