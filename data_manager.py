import pandas as pd
import numpy as np
import app as app


def data_change(data):
    if data == 'cot':
        df = cot_all
    else:
        df = neg_all

def get_categorical_columns():
    return df.select_dtypes(include='object').columns.tolist()

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

def get_data(columns):
    map_aux = map_data.copy()
    if 'TP' not in columns:
        map_aux = map_aux[map_aux['Proyecto'].isin(columns)]
    return map_aux

def get_nro_cotizaciones():
    return df.shape[0]

def get_personas_cot_mean():
    num_cot = []
    for group, frame in df.groupby('RUT'):
        num_cot.append(frame.shape[0])
    return app.millify(np.mean(num_cot))

def get_personas_total():
    return df.RUT.nunique()

def get_col_group_description(df, col):
    num_cot = []
    info = dict()
    for group, frame in df.groupby(col):
        num_cot.append(len(frame))
    cot_serie = pd.Series(num_cot)
    info['count'] = cot_serie.count()
    info['max'] = cot_serie.max()
    info['mean'] = cot_serie.mean()
    info['std'] = cot_serie.std()
    return info

cot_all = pd.read_excel('cotizaciones_all.xlsx')
neg_all = pd.read_excel('negocios_all.xlsx')

df = cot_all

#Proyectos Options
proyectos = df.Proyecto.unique()
proyects_options = [{'label': x, 'value':x} for x in proyectos]
proyects_options.append({'label':'Todos los Proyectos', 'value': 'TP'})

#for p in proyectos:
#    proyects_options.append({'label':p, 'value': p})
#proyects_options.append({'label':'Todos los Proyectos', 'value': 'TP'})

# Categorical Options
categorical_columns = get_categorical_columns()
cat_options = [{'label': col, 'value': col} for col in categorical_columns]

#for col in categorical_columns:
#   cat_options.append({'label': col, 'value': col})

