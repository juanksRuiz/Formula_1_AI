import requests
import pandas as pd

def get_season_qualifying_results(season):
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
              ,'best_time_Q1_s': drivers_Q1
              ,'best_time_Q2_s': drivers_Q2
              ,'best_time_Q3_s': drivers_Q3
              }
    return pd.DataFrame(result)


