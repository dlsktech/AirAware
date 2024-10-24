from flask import Flask, request, render_template
from requests import get
from json import loads as to_dictionary

app = Flask(__name__)

class Data():

    def raw(self):
        response = get("https://dev.omnihub.pl/api/infotechwidget/?format=json")
        data = to_dictionary(response.text)
        filtered_data = []
        
        for device in data:
            filtered_vars = []
            for var in device['vars']:
                if var['color'] != 'gray':
                    filtered_vars.append(var)
            
            if filtered_vars:
                filtered_data.append({'device': device['device'], 'vars': filtered_vars})
        
        return filtered_data

    def average(self):
        data = self.raw()
        parameters = ['Temperatura', 'Wilgotność', 'Ciśnienie', 'PM2.5', 'PM10', 'PM1']
        sums = {param: 0 for param in parameters}
        counts = {param: 0 for param in parameters}

        for device in data:
            for var in device['vars']:
                if var['var_name'] in parameters and isinstance(var['var_value'], (int, float)):
                    sums[var['var_name']] += var['var_value']
                    counts[var['var_name']] += 1

        averages = {}
        for param in parameters:
            if counts[param] > 0:
                averages[param] = round(sums[param] / counts[param], 1)
            else:
                averages[param] = None

        return averages


data = Data()

@app.route("/")
def index(data=data.average()):
    temp = data["Temperatura"]
    humidity = data["Wilgotność"]
    pressure = data["Ciśnienie"]
    pm1 = data["PM1"]
    pm25 = data["PM2.5"]
    pm10 = data["PM10"]

    # Logika dopasowania wiadomości do warunków atmosferycznych
    if pm25 < 25 and pm10 < 50:
        air_quality = "Dobra jakość powietrza"
    elif 25 <= pm25 < 50 or 50 <= pm10 < 100:
        air_quality = "Średnia jakość powietrza"
    else:
        air_quality = "Zła jakość powietrza"

    if temp < 0:
        temp_message = f"Jest mroźno, temperatura wynosi {temp} stopni. Ubierz się ciepło!"
    elif 0 <= temp < 15:
        temp_message = f"Temperatura wynosi {temp} stopni. Może być chłodno, więc załóż coś cieplejszego."
    elif 15 <= temp < 25:
        temp_message = f"Temperatura wynosi {temp} stopni. Jest przyjemnie, idealne warunki do wyjścia na zewnątrz."
    else:
        temp_message = f"Temperatura wynosi {temp} stopni. Jest gorąco, pamiętaj o nawadnianiu się!"


    if humidity > 80:
        humidity_message = f"Wilgotność wynosi {humidity}%. Może być duszno."
    elif humidity < 30:
        humidity_message = f"Wilgotność wynosi {humidity}%. Powietrze jest suche, pamiętaj o nawilżeniu."
    else:
        humidity_message = f"Wilgotność wynosi {humidity}%."

    if pressure < 1000:
        pressure_message = f"Ciśnienie wynosi {pressure} hPa. Możliwe, że odczujesz niskie ciśnienie."
    elif pressure > 1020:
        pressure_message = f"Ciśnienie wynosi {pressure} hPa. Może to wpływać na samopoczucie."
    else:
        pressure_message = f"Ciśnienie wynosi {pressure} hPa."

    return render_template(
        "index.html", 
        message=f"{temp_message} {humidity_message} {pressure_message}", 
        qual=air_quality
    )

if __name__ == "__main__":
    app.run(debug=True, port=80)