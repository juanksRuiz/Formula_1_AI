from funcs_data_extraction import *


# Ejemplo de uso
resultados_qualifying_2023 = get_season_qualifying_results(2023)

df_qualifying = get_round_qualifying_results(resultados_qualifying_2023, 1)
df_qualifying_variables = calculate_qualifying_variables(df_qualifying)
print(df_qualifying_variables)
