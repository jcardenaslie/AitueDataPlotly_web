from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_curve
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
from scipy.stats import randint
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn import metrics
from sklearn.preprocessing import MinMaxScaler

#Predictors
no_is_time_price = [
    'is_recontacto', 'is_remoto', 
    'loc_comuna',
    'loc_provincia', 'loc_region', 
    'mean_cot_bod',
    'mean_cot_depto', 'mean_cot_esta', 'mean_cot_estu', 'medio_inicial',
    'nro_cot_bod', 'nro_cot_depto', 'nro_cot_esta',
    'nro_cot_estu', 'nro_proyectos', 'precio_cotizacion_media',
    'precio_cotizacion_median', 'precio_cotizacion_std', 
    'sexo',
    'tiempo_cotizacion_media', 'tiempo_cotizacion_median',
    'tiempo_cotizacion_std', 'tipo_cliente', 'valid_rut', 
    'Altos del Valle',
    'Edificio Urban 1470', 
#     'San Andres Del Valle', 
    'Edificio Mil610',
       'Edificio Junge']

personas = pd.read_csv('personas_cotizacion8', encoding = "ISO-8859-1")
x_train = pd.read_csv('x_train', encoding = "ISO-8859-1")
y_train = pd.read_csv('y_train', encoding = "ISO-8859-1")
x_test = pd.read_csv('x_test', encoding = "ISO-8859-1")
y_test = pd.read_csv('y_test', encoding = "ISO-8859-1")


personas['loc_comuna'] = personas['loc_comuna'].astype('category')
personas['loc_provincia'] = personas['loc_provincia'].astype('category')
personas['loc_region'] = personas['loc_region'].astype('category')
personas['tipo_cliente'] = personas['tipo_cliente'].astype('category')
personas['sexo'] = personas['sexo'].astype('category')
personas['medio_inicial'] = personas['medio_inicial'].astype('category')

predictors = predictors_set[no_is_time_price]

from sklearn.externals import joblib
clf = joblib.load('filename.joblib')



