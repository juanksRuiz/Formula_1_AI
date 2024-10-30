from urllib.request import urlopen
import json
import pandas as pd

# response = urlopen('https://api.openf1.org/v1/car_data?driver_number=55&session_key=9159&speed>=315')

# Busquemos la informacion de los pilotos cuyos numeros van del 1 al 10
driver_nums = [55]#[i for i in range(10)]
for i in driver_nums:
    url_str = 'https://api.openf1.org/v1/car_data?'
    response = urlopen(url_str + "driver_number=" + str(i) + "&session_key=9159")
    data = json.loads(response.read().decode('utf-8'))
    print(data)

# If you want, you can import the results in a DataFrame (you need to install the `pandas` package first)
df = pd.DataFrame(data)

