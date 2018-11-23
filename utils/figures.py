from plotly import graph_objs as go
import data_manager as dm
import pandas as pd

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
    #sacar de aca
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

def cases_by_period(df, period, priority, origin):
    df = dm.df
    stages = df["Proyecto"].unique()

    if period == "W-MON":
        df["CreatedDate"] = pd.to_datetime(df["CreatedDate"]) - pd.to_timedelta(7, unit="d")
    
    df = df.groupby([pd.Grouper(key="CreatedDate", freq=period), "Type"]).count() 
    
    dates = df.index.get_level_values("CreatedDate").unique()
    dates = [str(i) for i in dates]

    data = []
    for stage in stages:
        stage_rows = []
        for date in dates:
            try:
                row = df.loc[(date, stage)]
                stage_rows.append(row["IsDeleted"])
            except Exception as e:
                stage_rows.append(0)

        data_trace = go.Bar(
            x=dates, y=stage_rows, name=stage, marker=dict(color=co[stage])
        )
        data.append(data_trace)

    layout = go.Layout(
        # barmode="stack",
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
            col_values.append(df[(df[col1] == value1) & (df[col2] == value2)]['ID'].count())
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
            font=dict(size=16)
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1
    )
    return {'data':data, 'layout':layout}

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
