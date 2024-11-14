# Module imports
from jolpica_connection import *
import numpy as np
import pandas as pd

# La idea de este archivo es probar el flujo de las funciones creadas
# Para traer los datos de la API, preprocesarlos y tener una tabla final
# consolidada con las distintas de funetes de datos

# Cargue de librerias
# PASO 1: definicion de parametros como la temporada y ronda de la cual
# Se calculara los resultados con las 10 carreras anteriores.
season_years = [2022, 2023]
round_wdw = 10
prediction_round = 11 # si es inferior a 10, crear flujo para las carreras
# de la ronda anterior

# PASO 2.1: obtener la tabla preprocesada de los tiempos de Qualis
if prediction_round > round_wdw:
    max_season = max(season_years)
    print('Collecting data from season {temp}...'.format(temp=max_season))
    season_data = get_season_qualifying_results(max_season)
    print('Data collection from season {temp} successful!'.format(temp=max_season))
    print('Concatenating data...')
    for i in range(prediction_round-round_wdw, prediction_round):
        round_df = get_round_results(season_data, i)
        if i == prediction_round-round_wdw:
            all_qualis_df = round_df
        else:
            all_qualis_df = pd.concat([all_qualis_df, round_df], axis=0)
    print('Data from all rounds concatenated!')
    
print('Preprocessing all rounds data...')
qualis_df = preprocess_round_data(all_qualis_df)
print('Preprocessing successful')
