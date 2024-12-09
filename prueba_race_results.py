from funcs_data_extraction import *


race_results = get_season_race_results(2023)
first_race_results_df = get_round_race_results(race_results, 1)
