import pandas as pd
import numpy as np
import app as app

import dash_core_components as dcc
import copy

months = ['Ene', 'Feb', 'Mar', 'Abr',
'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dec']

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
    elif data == 'comp':
        df = neg_all[(neg_all['Estado'] == 'Escriturado') | (neg_all['Estado'] == 'Entregado')]
    return df

# Trae los proyectos que vende el inmbueble
def get_proyectos_in_inmueble(data, inmueble):
    tmp_data = get_data(data, inmueble)
    proyectos = tmp_data.Proyecto.unique()
    proyectos_options = [{'label': x, 'value':x} for x in proyectos]
    proyectos_options.append({'label':'Todos', 'value': 'TP'})
    return proyectos_options

def get_etapa_in_proyecto(data, inmbueble, proyecto):
    data = get_data(data, inmbueble, proyecto)
    etapas = data.Etapa.unique()
    etapas_options = [{'label': x, 'value':x} for x in etapas]
    etapas_options.append({'label':'Todos', 'value': 'TE'})
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

def get_filas_data(data, inmueble, proyecto, etapa=None):
    data = get_data(data, inmueble, proyecto, etapa)
    return data.shape[0]

def get_personas_cot_mean(data, inmueble, proyecto, etapa=None):
    data = get_data(data, inmueble, proyecto, etapa)
    num_cot = []
    for group, frame in data.groupby('RUT'):
        num_cot.append(frame.shape[0])
    
    try:
        return app.millify(np.mean(num_cot))
    except ValueError:
        return 'Error'

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

def get_reservas(data, inmueble,  proyecto, etapa=None):
    data = get_data(data, inmueble, proyecto, etapa)
    data = data[data['Estado'] == 'Reservado']
    return data.shape[0]

def get_promesas(data, inmueble,  proyecto, etapa=None):
    data = get_data(data, inmueble, proyecto, etapa)
    data = data[data['Estado'] == 'Promesado']
    return data.shape[0]

def get_escrituras(data, inmueble,  proyecto, etapa=None):
    data = get_data(data, inmueble, proyecto, etapa)
    data = data[data['Estado'] == 'Escriturado']
    return data.shape[0]

def get_entregas(data, inmueble,  proyecto, etapa=None):
    data = get_data(data, inmueble, proyecto, etapa)
    data = data[data['Estado'] == 'Entregado']
    return data.shape[0]

def get_data_whithin_dates(data, proyecto,inmueble, year_values, month_values, etapa=None,):
    fecha_ini = "" + str(year_values[0]) + "-" + str(month_values[0]) + "-1"
    fecha_fin = "" + str(year_values[1]) + "-" + str(month_values[1]) + "-31"

    date_check = pd.to_datetime(fecha_fin)

    fechas = copy.deepcopy(get_data(data, inmueble=inmueble,proyecto=proyecto, etapa=etapa))
    fechas = fechas.sort_values(by='Fecha Cotizacion')  
    fechas.set_index(pd.to_datetime(fechas['Fecha Cotizacion']), inplace=True)
    fechas = fechas.loc[fecha_ini : fecha_fin]
    return fechas

def get_productos(proyecto, etapa):
    if proyecto != 'TP' and proyecto != None:
        prod_sdv = productos[productos.Proyecto == proyecto]
        if etapa != 'TE' and etapa != None:
            prod_sdv = prod_sdv[prod_sdv.Etapa == etapa]
    else:
        prod_sdv = productos

    return prod_sdv

def get_prod_mas_cotizado_persona(data,  proyecto, etapa=None, ascending=False, q=1) :
    
    prod_sdv = get_productos(proyecto, etapa)
    
    if data == 'cot':
        data_tmp = cot_prod_info
    elif data == 'neg':
        data_tmp = neg_prod_info
    elif data == 'comp':
        data_tmp = comp_prod_info
    
    if proyecto != 'TP' and proyecto != None:
        data_tmp = data_tmp[(data_tmp.Proyecto == proyecto) ]
    if etapa != 'TE' and etapa != None:
            data_tmp = data_tmp[(data_tmp.Etapa == etapa)]

    if ascending == True:
        data_tmp = data_tmp.sort_values(by='Nro Personas', ascending=True)
    return data_tmp.head(q)

def calc_nro_cotizaciones(data):
    prod_sdv = productos
    cot_sdv = get_data(data)

    cot_prod = dict() # productos cotizados por etapa
    cot_prod['ID Cot'] = list()
    cot_prod['Producto'] = list()
    cot_prod['RUT'] = list()
    cot_prod['Fecha Cot'] = list()
    cot_prod['Etapa'] = list()
    cot_prod['Proyecto'] = list()
    drop = ['Nombre', 'SobrePrecio', 'Producto', 
                'Precio Lista', 'Precio Venta', 'Precio Esperado',
                'Baños', 'Dormitorios', 'Cod Proyecto', 'Cod Etapa']

    results = []
    for proyecto in cot_sdv.Proyecto.unique():
        cot_proy = cot_sdv[cot_sdv.Proyecto == proyecto]
        prod_proy = prod_sdv[prod_sdv.Proyecto == proyecto]
        for etapa in cot_proy.Etapa.unique():
            prod_etapa = prod_proy[prod_proy.Etapa == etapa]
            cot_etapa = cot_proy[cot_proy.Etapa == etapa]
            for index, row in cot_etapa.iterrows():
                prod = row['Productos']
                if isinstance(prod, int):
                    cot_prod['Producto'].append(prod)
                    cot_prod['RUT'].append(row['RUT'])
                    cot_prod['ID Cot'].append(row['ID'])
                    cot_prod['Fecha Cot'].append(row['Fecha Cotizacion'])
                    cot_prod['Etapa'].append(row['Etapa'])
                    cot_prod['Proyecto'].append(row['Proyecto'])
                elif isinstance(prod, str):
                    for p in prod.split(','):
                        cot_prod['Producto'].append(p)
                        cot_prod['RUT'].append(row['RUT'])
                        cot_prod['ID Cot'].append(row['ID'])
                        cot_prod['Fecha Cot'].append(row['Fecha Cotizacion'])
                        cot_prod['Etapa'].append(row['Etapa'])
                        cot_prod['Proyecto'].append(row['Proyecto'])
                elif isinstance(prod, float):
                    prod = str(prod)
                    for p in prod.split('.'):
                        cot_prod['Producto'].append(p)
                        cot_prod['RUT'].append(row['RUT'])
                        cot_prod['ID Cot'].append(row['ID'])
                        cot_prod['Fecha Cot'].append(row['Fecha Cotizacion'])
                        cot_prod['Etapa'].append(row['Etapa'])
                        cot_prod['Proyecto'].append(row['Proyecto'])
            

            tmp = pd.DataFrame(cot_prod)
            tmp.drop(['Etapa', 'Proyecto'], axis=1, inplace=True)
            cot_prod_merge = tmp.merge(prod_etapa, left_on='Producto', right_on='Numero Unidad',how='left')
            cotizacion_producto = cot_prod_merge.drop(drop, axis=1)
            results.append(cotizacion_producto)

    if len(results) > 1:
        cot_prod_info = pd.concat(results)
    else:
        cot_prod_info = results[0]

    cot_prod_info['count'] = 1
    # prod_nro_cot = dict()
    prod_nro_cot_persona = dict()

    # Numero de cotizaciones por persona por producto
    for group, frame in cot_prod_info.groupby(['Proyecto','Etapa','Numero Unidad' ]):
        prod_nro_cot_persona[group] = frame['RUT'].nunique()


    prod_sdv_cp = copy.deepcopy(prod_sdv)
    prod_sdv_cp['Nro Personas'] = 0

    prod_sdv_cp.set_index(['Proyecto','Etapa','Numero Unidad' ], inplace=True)
    
    for index, prod in prod_sdv_cp.iterrows():
        if index in prod_nro_cot_persona.keys():
            prod_sdv_cp.at[index, 'Nro Personas'] =  prod_nro_cot_persona[index]
    
    prod_sdv_cp=prod_sdv_cp.reset_index().sort_values(by='Nro Personas', ascending=False)
    
    return prod_sdv_cp

##########################################################################################################################
# cot_all = pd.read_excel('Data/cotizaciones_all.xlsx')
# cot_all = pd.read_csv('Data\\cotizaciones_all_new.csv', index_col=[0])
# # neg_all = pd.read_excel('Data\\negocios_all.xlsx')
# neg_all = pd.read_csv('Data\\negocios_all_new.csv', index_col=[0])

# cot_all = pd.read_excel('Data/cotizaciones_all.xlsx')
cot_all = pd.read_csv('Data/cotizaciones_all_new.csv', index_col=[0])
# neg_all = pd.read_excel('Data\\negocios_all.xlsx')
neg_all = pd.read_csv('Data/negocios_all_new.csv', index_col=[0])

productos = pd.read_csv('Data/productos.csv', index_col=[0], encoding = "ISO-8859-1")




cot_prod_info = calc_nro_cotizaciones('cot')
neg_prod_info = calc_nro_cotizaciones('neg')
comp_prod_info = calc_nro_cotizaciones('comp')


# Cuando se trabaja con csv
cot_all['Fecha Cotizacion'] =  pd.to_datetime(cot_all['Fecha Cotizacion'])
neg_all['Fecha Cotizacion'] =  pd.to_datetime(neg_all['Fecha Cotizacion'])

df = cot_all


date_min = cot_all['Fecha Cotizacion'].min().year
date_max =cot_all['Fecha Cotizacion'].max().year

data_years = list(range(date_min , date_max+1))
#Proyectos Options
proyectos = df.Proyecto.unique()
inmuebles = df.Inmueble.unique()

inmb_options = [{'label': x, 'value':x} for x in inmuebles]
inmb_options.append({'label':'Todos los Inmuebles', 'value': 'TI'})

proyects_options = [{'label': x, 'value':x} for x in proyectos]
proyects_options.append({'label':'Todos los Proyectos', 'value': 'TP'})

# Categorical Options
categorical_columns = get_categorical_columns(df)
cat_options = [{'label': col, 'value': col} for col in categorical_columns]


