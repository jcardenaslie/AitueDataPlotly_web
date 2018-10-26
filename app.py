import dash
import math
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import plotly.graph_objs as go

app = dash.Dash(__name__)

app.config.suppress_callback_exceptions = True

server = app.server

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

millnames = ["", " K", " M", " B", " T"] # used to convert numbers

# map_data = df


# return html Table with dataframe values  
def df_to_table(df):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +
        
        # Body
        [
            html.Tr(
                [
                    html.Td(df.iloc[i][col])
                    for col in df.columns
                ]
            )
            for i in range(len(df))
        ]
    )
#returns most significant part of a number
def millify(n):
    n = float(n)
    millidx = max(
        0,
        min(
            len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))
        ),
    )

    return "{:.0f}{}".format(n / 10 ** (3 * millidx), millnames[millidx])
#returns top indicator div
def indicator(color, text, id_value):
    return html.Div(
        [
            html.P(
                text,
                className="twelve columns indicator_text"
            ),
            html.P(
                id = id_value,
                className="indicator_value"
            ),
        ],
        className="four columns indicator", 
    )

def small_indicator(color, text, id_value):
    return html.Div(
        [
            html.P(
                text,
                className="twelve columns ma_indicator_text"
            ),
            html.P(
                id = id_value,
                className="ma_indicator_value"
            ),
        ],
        className="row ma_indicator",
        
    )

def vertical_indicator(color, text, id_value):
    return html.Div(
        className='indicator',children=[
                html.P( text, className='twelve columns indicator_text'),
                html.P(id=id_value, className='indicator_value')
    ]
    )

# if __name__ == '__main__':
#     app.run_server(debug=True)