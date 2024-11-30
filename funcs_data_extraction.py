import requests
import pandas as pd
import numpy as np

def get_season_qualifying_results(season):
    """
    Obtiene  los datos de todos los eventos de una temporada de la Formula 1
    
    ARGS:
        season (int): anio de la temporada de la cual se descaargan los datos
        
    RETURNS:
        lista con datos como diccionarios de cada ronda
    """
    qualifying_results = []
    round_number = 1

    while True:
        url = f"http://ergast.com/api/f1/{season}/{round_number}/qualifying.json"
        response = requests.get(url)
        
        if response.status_code != 200:
            break  # Termina si no hay más rondas
        
        data = response.json()
        
        # Extrae y guarda los resultados de clasificación de la ronda actual
        races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
        if races:
            qualifying_results.extend(races)
            round_number += 1
        else:
            break

    return qualifying_results

# Ejemplo de uso:
#season_data = get_season_qualifying_results(2023)
#print(season_data)
# ----------------------------------------------------------------------------
# Funcion para ordenar los datos de una ronda en una tabla
def get_round_results(season_data, round_id):
    """
    Obtiene los resultados de una ronda con los datos de una temporada
    especifica
    ARGS:
        season_data (X): datos de una temporada
        round_id (string): numero de la ronda de la temporada
    
    RETURNS:
        Dataframe de pandas con los datos. Incluye el numero y codigo de cada
        piloto, y los mejores tiempos en Q1, Q2 y Q3
    """
    # Se toma el id de la ronda, el nombre de la carrera, la date, time
    # y los resultados en Q1, Q2, y Q3
    round_data = season_data[int(round_id)]
    #round_num = round_data['round']
    #race_name = round_data['raceName']
    #race_date = round_data['date']
    #race_time = round_data['time']
    num_of_drivers = []
    drivers_final_pos = []
    driver_ids = []
    driver_codes = []
    drivers_fullname = []
    drivers_Q1 = []
    drivers_Q2 = []
    drivers_Q3 = []
    
    for driver_results in round_data['QualifyingResults']:
        num_of_drivers.append(driver_results['number'])
        drivers_final_pos.append(driver_results['position'])
        driver_ids.append(driver_results['Driver']['driverId'])
        driver_codes.append(driver_results['Driver']['code'])
        drivers_fullname.append(driver_results['Driver']['givenName'] + \
                                ' ' + driver_results['Driver']['familyName'])
            
        
        try:
            q1_data = driver_results['Q1']
        except:
            q1_data = None
        finally:
            drivers_Q1.append(q1_data)
         
        
        try:
            q2_data = driver_results['Q2']
        except:
            q2_data = None
        finally:
            drivers_Q2.append(q2_data)
        
        try:
            q3_data = driver_results['Q3']
        except:
            q3_data = None
        finally:
            drivers_Q3.append(q3_data)
        
        
    
    result = {'driver_number': num_of_drivers
              ,'final_position': drivers_final_pos
              ,'driver_id': driver_ids
              ,'code': driver_codes
              ,'fullname': drivers_fullname
              ,'best_time_Q1': drivers_Q1
              ,'best_time_Q2': drivers_Q2
              ,'best_time_Q3': drivers_Q3
              }
    return pd.DataFrame(result)


# ----------------------------------------------------------------------------
# Utility function
def convert_time_to_timedelta(time_str):
    """
    Convert a string time in the format 'M:SS.SSS' to a pandas Timedelta.
    
    Parameters:
    time_str (str): Time string in the format 'M:SS.SSS'
    
    Returns:
    pandas.Timedelta: Timedelta representation of the input time string
    """
    # Se ignora en caso de que el campo venga vacio o con None por
    # no haber clasificado
    if pd.isna(time_str) or time_str.strip() == '':
        return np.nan
        # return pd.Timedelta(0)
    else:
        parts = time_str.split(':')
        minutes = int(parts[0])
        seconds = float(parts[1])
        
        return pd.Timedelta(minutes=minutes, seconds=seconds)

# ----------------------------------------------------------------------------
# Utility method for lammbda  function
def compute_time_diffs(row):
        q1_value = row['best_time_Q1'] if pd.notna(row['best_time_Q1']) and \
                        not isinstance(row['best_time_Q1'], str) else np.nan
        q2_value = row['best_time_Q2'] if pd.notna(row['best_time_Q2']) and \
                        not isinstance(row['best_time_Q2'], str) else np.nan
                        
        return q2_value  - q1_value 
# ----------------------------------------------------------------------------
# Ahora queremos preprocesar cada tabla de cada ronda  y crear las columnas
# de mejora de Q1 a Q3
def preprocess_round_data(round_df):
    """
    Calcula la mejora en segundos de Q1 a Q2, Q2 a Q3 y Q1 a Q3 como nuevas
    columnas de un dataset inicial
    
    ARGS:
        round_df (pandas.DataFrame): dataframe con datos crudos de una ronda de
            una temporada
    
    RETURNS:
        Un dataframe con las columnas de mejora de tiempos de Q1 a Q3
    """
    # Paso 1: transformar las columnas de tiempos Qualis a time_delta
    df = round_df.copy()
    df['best_time_Q1'] = df['best_time_Q1'].apply(convert_time_to_timedelta)
    df['best_time_Q2'] = df['best_time_Q2'].apply(convert_time_to_timedelta)
    df['best_time_Q3'] = df['best_time_Q3'].apply(convert_time_to_timedelta)
    
    # Paso 2: calcular diferencia entre Qualis
    df['time_diff_Q1_Q2_s'] = df.apply(compute_time_diffs, axis=1).dt.\
                                            total_seconds()
    '''df['time_diff_Q1_Q2_s'] = (df['best_time_Q2'] - \
                                           df['best_time_Q1']).dt.\
                                    total_seconds()
                                    
    df['time_diff_Q2_Q3_s'] = (df['best_time_Q3'] - \
                                           df['best_time_Q2']).dt.\
                                    total_seconds()
                                    
    df['time_diff_Q1_Q3_s'] = df['time_diff_Q1_Q2_s'] + \
                                    df['time_diff_Q2_Q3_s']'''
                                    
    return df
