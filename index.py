import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from app import app

from apps import cotizaciones, semaforo


app.layout = html.Div(children=[
        # header
        html.Div([

            html.Span("AITUE DASH", className='app-title'),
            
            html.Div(
                html.Img(src='https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe-inverted.png',height="100%")
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
                    dcc.Tab(id="cot_tab",label="Cotizaciones", value="cot_tab"),
                    dcc.Tab(label="Negocios", value="leads_tab"),
                    dcc.Tab(label="Semaforo", value="sem_tab"),
                    dcc.Tab(label="Listas", value="lista_tab"),
                ],
                value="cot_tab",
            )

            ],className="row tabs_div"
        ),
        
        html.Div(id="tab_content", className="row", style={"margin": "2% 3%"}),
        html.Link(href="https://use.fontawesome.com/releases/v5.2.0/css/all.css",rel="stylesheet"),
        html.Link(href="https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css",rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Dosis", rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Open+Sans", rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Ubuntu", rel="stylesheet"),
        html.Link(href="https://cdn.rawgit.com/amadoukane96/8a8cfdac5d2cecad866952c52a70a50e/raw/cd5a9bf0b30856f4fc7e3812162c74bfc0ebe011/dash_crm.css", rel="stylesheet")  
    ],className="row",
    style={"margin": "0%"},
)

@app.callback(Output("tab_content", "children"), [Input("tabs", "value")])
def render_content(tab):
    if tab == "cot_tab":
        return cotizaciones.layout
    elif tab == "cases_tab":
        pass
        # return cases.layout
    elif tab == "sem_tab":
        return semaforo.layout
        pass
        # return leads.layout
    else:
        pass
        # return opportunities.layout

if __name__ == '__main__':
    app.run_server(debug=True)