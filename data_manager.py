import pandas as pd
import numpy as np
import app as app

import dash_core_components as dcc



def get_data(data, inmueble=None, proyecto=None, etapa=None):
    data = data_change(data)

    if inmueble != 'TI' and inmueble != None:
        data = data[(data.Inmueble == inmueble)]

    if proyecto != 'TP' and proyecto != None :
        data = data[(data.Proyecto == proyecto)]

    if etapa != 'TE' and etapa != None:
        data = data[data.Etapa == etapa]

    return data

#cambia el set de datos
def data_change(data):
    if data == 'cot':
        df = cot_all
    elif data=='neg':
        df = neg_all
    return df

# Trae los proyectos que vende el inmbueble
def get_proyectos_in_inmueble(data, inmueble):
    tmp_data = get_data(data, inmueble)
    proyectos = tmp_data.Proyecto.unique()
    proyectos_options = [{'label': x, 'value':x} for x in proyectos]
    proyectos_options.append({'label':'Todos', 'value': 'TP'})
    return proyectos_options

def get_etapa_in_proyecto(data, inmbueble, proyecto):
    data = get_data(data, inmueble=inmbueble, proyecto=proyecto)
    etapas = data.Etapa.unique()
    etapas_options = [{'label': x, 'value':x} for x in etapas]
    etapas_options.append({'label':'Todos las Etapas', 'value': 'TE'})
    return etapas_options

def get_categorical_columns(df):
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

# def get_data(columns):
#     map_aux = map_data.copy()
#     if 'TP' not in columns:
#         map_aux = map_aux[map_aux['Proyecto'].isin(columns)]
#     return map_aux

def get_filas_data(data, inmueble, proyecto, etapa=None):
    data = get_data(data, inmueble, proyecto, etapa)
    return data.shape[0]

def get_personas_cot_mean(data, inmueble, proyecto, etapa=None):
    data = get_data(data, inmueble, proyecto, etapa)
    num_cot = []
    for group, frame in data.groupby('RUT'):
        num_cot.append(frame.shape[0])
    return app.millify(np.mean(num_cot))

def get_personas_total(data, inmueble, proyecto, etapa=None):
    data = get_data(data, inmueble, proyecto, etapa)
    return data.RUT.nunique()

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



# cot_all = pd.read_excel('Data/cotizaciones_all.xlsx')
# cot_all = pd.read_csv('Data\\cotizaciones_all_new.csv', index_col=[0])
# # neg_all = pd.read_excel('Data\\negocios_all.xlsx')
# neg_all = pd.read_csv('Data\\negocios_all_new.csv', index_col=[0])

# cot_all = pd.read_excel('Data/cotizaciones_all.xlsx')
cot_all = pd.read_csv('Data/cotizaciones_all_new.csv', index_col=[0])
# neg_all = pd.read_excel('Data\\negocios_all.xlsx')
neg_all = pd.read_csv('Data/negocios_all_new.csv', index_col=[0])

# Cuando se trabaja con csv
cot_all['Fecha Cotizacion'] =  pd.to_datetime(cot_all['Fecha Cotizacion'])
neg_all['Fecha Cotizacion'] =  pd.to_datetime(neg_all['Fecha Cotizacion'])

df = cot_all

#Proyectos Options
proyectos = df.Proyecto.unique()
inmuebles = df.Inmueble.unique()

# print('Inmuebles', inmuebles)
inmb_options = [{'label': x, 'value':x} for x in inmuebles]
inmb_options.append({'label':'Todos los Inmuebles', 'value': 'TI'})

# print('Proyectos',proyectos)
proyects_options = [{'label': x, 'value':x} for x in proyectos]
proyects_options.append({'label':'Todos los Proyectos', 'value': 'TP'})

# Categorical Options
categorical_columns = get_categorical_columns(df)
cat_options = [{'label': col, 'value': col} for col in categorical_columns]


