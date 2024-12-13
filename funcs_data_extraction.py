import requests
import pandas as pd
import numpy as np



def get_season_race_results(season):
    """
    Obtiene los datos de carreras de todos los eventos de una temporada de la Formula 1
    
    ARGS:
        season (int): año de la temporada de la cual se descargan los datos
        
    RETURNS:
        lista con datos de carreras como diccionarios de cada ronda
    """
    races = []
    offset = 0
    limit = 30  # Número de resultados por página

    while True:
        url = f"http://api.jolpi.ca/ergast/f1/{season}/results/?limit={limit}&offset={offset}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            new_races = data['MRData']['RaceTable']['Races']
            if not new_races:
                break
            races.extend(new_races)
            offset += limit
        else:
            print(f"Error: {response.status_code}")
            break

    # Eliminar duplicados basados en el nombre de la carrera
    unique_races = []
    seen_race_names = set()
    for race in races:
        if race['raceName'] not in seen_race_names:
            unique_races.append(race)
            seen_race_names.add(race['raceName'])

    return unique_races
# ----------------------------------------------------------------------------
def get_round_race_results(season_data, round_id):
    """
    Obtiene los resultados de una carrera con los datos de una temporada específica.
    
    ARGS:
        season_data (list): datos de una temporada.
        round_id (int): número de la ronda de la temporada.
    
    RETURNS:
        DataFrame de pandas con los resultados de carrera.
    """
    if round_id <= 0 or round_id > len(season_data):
        print('ERROR: número de ronda incorrecto')
        return None
    
    round_data = season_data[round_id - 1]
    
    num_of_drivers = []
    drivers_race_pos = []
    driver_ids = []
    driver_codes = []
    drivers_fullname = []
    finished_race_flags = []
    fastest_lap_ranks = []
    
    for driver_results in round_data['Results']:
        num_of_drivers.append(driver_results['number'])
        drivers_race_pos.append(driver_results['position'])
        driver_ids.append(driver_results['Driver']['driverId'])
        driver_codes.append(driver_results['Driver']['code'])
        drivers_fullname.append(driver_results['Driver']['givenName'] + ' ' + driver_results['Driver']['familyName'])
        finished_race_flags.append(driver_results['status'])
        fastest_lap_ranks.append(driver_results['FastestLap']['rank'] if 'FastestLap' in driver_results else None)
    
    result = {
        'driver_number': num_of_drivers,
        'final_position': drivers_race_pos,
        'driver_id': driver_ids,
        'code': driver_codes,
        'fullname': drivers_fullname,
        'race_ending_status': finished_race_flags,
        'fastest_lap_rank': fastest_lap_ranks
    }
    
    return pd.DataFrame(result)
# ----------------------------------------------------------------------------
def get_season_qualifying_results(season):
    """
    Obtiene los datos de qualifyers de todos los eventos de una temporada de la Formula 1
    
    ARGS:
        season (int): año de la temporada de la cual se descargan los datos
        
    RETURNS:
        lista con datos de qualifiers como diccionarios de cada ronda
    """
    qualifying_results = []
    offset = 0
    limit = 30  # Número de resultados por página

    while True:
        url = f"https://api.jolpi.ca/ergast/f1/{season}/qualifying/?limit={limit}&offset={offset}"
        response = requests.get(url)
        
        if response.status_code != 200:
            break  # Termina si no hay más rondas
        
        data = response.json()
        
        # Extrae y guarda los resultados de clasificación de la ronda actual
        races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
        if races:
            qualifying_results.extend(races)
            offset += limit
        else:
            break

    return qualifying_results

# Ejemplo de uso:
#season_data = get_season_qualifying_results(2023)
#print(season_data)
# ----------------------------------------------------------------------------
# Funcion para ordenar los datos de una ronda en una tabla
def get_round_qualifying_results(season_data, round_id):
    """
    Obtiene los tiempos de Q1, Q2 y Q3 de una ronda con los datos de una temporada específica.
    
    ARGS:
        season_data (list): datos de una temporada.
        round_id (int): número de la ronda de la temporada.
    
    RETURNS:
        DataFrame de pandas con los tiempos de Q1, Q2 y Q3.
    """
    if round_id <= 0 or round_id > len(season_data):
        print('ERROR: número de ronda incorrecto')
        return None
    
    round_data = season_data[round_id - 1]
    
    num_of_drivers = []
    driver_ids = []
    driver_codes = []
    drivers_fullname = []
    drivers_Q1 = []
    drivers_Q2 = []
    drivers_Q3 = []
    
    for driver_results in round_data['QualifyingResults']:
        num_of_drivers.append(driver_results['number'])
        driver_ids.append(driver_results['Driver']['driverId'])
        driver_codes.append(driver_results['Driver']['code'])
        drivers_fullname.append(driver_results['Driver']['givenName'] + ' ' + driver_results['Driver']['familyName'])
        
        drivers_Q1.append(driver_results.get('Q1', None))
        drivers_Q2.append(driver_results.get('Q2', None))
        drivers_Q3.append(driver_results.get('Q3', None))
    
    result = {
        'driver_number': num_of_drivers,
        'driver_id': driver_ids,
        'code': driver_codes,
        'fullname': drivers_fullname,
        'best_time_Q1': drivers_Q1,
        'best_time_Q2': drivers_Q2,
        'best_time_Q3': drivers_Q3
    }
    
    return pd.DataFrame(result)

# ----------------------------------------------------------------------------
def calculate_qualifying_variables(df):
    """
    Calcula variables derivadas a partir de los tiempos de Q1, Q2 y Q3.
    
    ARGS:
        df (DataFrame): DataFrame con los tiempos de Q1, Q2 y Q3.
    
    RETURNS:
        DataFrame de pandas con las variables derivadas.
    """
    # Convertir tiempos a Timedelta
    df['best_time_Q1'] = df['best_time_Q1'].apply(convert_time_to_timedelta)
    df['best_time_Q2'] = df['best_time_Q2'].apply(convert_time_to_timedelta)
    df['best_time_Q3'] = df['best_time_Q3'].apply(convert_time_to_timedelta)
    
    # Calcular variables derivadas
    df['best_time'] = df[['best_time_Q1', 'best_time_Q2', 'best_time_Q3']].min(axis=1)
    df['avg_time'] = df[['best_time_Q1', 'best_time_Q2', 'best_time_Q3']].mean(axis=1)
    df['std_dev_time'] = df[['best_time_Q1', 'best_time_Q2', 'best_time_Q3']].std(axis=1)
    df['total_time'] = df[['best_time_Q1', 'best_time_Q2', 'best_time_Q3']].sum(axis=1)
    
    return df
# ----------------------------------------------------------------------------
# Utility function
def convert_time_to_timedelta(time_str):
    """
    Convierte una cadena de tiempo en el formato 'M:SS.SSS' a un Timedelta de pandas.
    
    Parámetros:
    time_str (str): Cadena de tiempo en el formato 'M:SS.SSS'
    
    Retorna:
    pandas.Timedelta: Representación de Timedelta del tiempo de entrada
    """
    # Se ignora en caso de que el campo venga vacío o con None por no haber clasificado
    if pd.isna(time_str) or time_str.strip() == '':
        return np.nan
    else:
        parts = time_str.split(':')
        minutes = int(parts[0])
        seconds = float(parts[1])
        
        return pd.Timedelta(minutes=minutes, seconds=seconds)

# ----------------------------------------------------------------------------
def add_time_in_milliseconds(df):
    """
    Agrega variables representando los tiempos en milisegundos a partir de los tiempos de Q1, Q2 y Q3.
    
    ARGS:
        df (DataFrame): DataFrame con los tiempos de Q1, Q2 y Q3 en formato Timedelta.
    
    RETURNS:
        DataFrame de pandas con las variables de tiempos en milisegundos.
    """
    # Agregar variables en milisegundos
    df['best_time_Q1_ms'] = df['best_time_Q1'].dt.total_seconds() * 1000
    df['best_time_Q2_ms'] = df['best_time_Q2'].dt.total_seconds() * 1000
    df['best_time_Q3_ms'] = df['best_time_Q3'].dt.total_seconds() * 1000
    
    return df

# Ejemplo de uso
# df_qualifying = get_round_qualifying_results(resultados_qualifying_2023, 1)
# df_qualifying_with_ms = add_time_in_milliseconds(df_qualifying)
# print(df_qualifying_with_ms)
