#requests serve per effettuare chiamate http
import requests
#serve per creare il grafico (attualmente commentato perché ursto chartJs)
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator
#Permette di utilizzare le date
from datetime import datetime
#Crea un server virtuale per eseguire la chiamata ad ARPA
from flask import Flask, request
#Permette di bypassare il cors origin del server per la chiamata esguita dal js
from flask_cors import cross_origin
#Permette di calcolare una data inferiore passando al mese precedente e non accetta valori = a 0
from dateutil.relativedelta import relativedelta
import io
import base64
import json

# Flask permette di far comunicare il server python con la mappa in index.html
# Inizialisso la classe Flask
app = Flask(__name__)

# Definisco la rotta da contattare tramite JS
@app.route("/get_pluviometer")
# Disattivo il cross origin così da avere due server separati, uno per le APIs e l'altro per la mappa
@cross_origin()

# Make the API call to the ARPA Piemonte website
def call_API():
    # Take today's date
    today = datetime.now()
    # Refer today's date to a year before. Relativedelta avoids values = 0. Use 'yearS' and not 'year' otherwise the year is defined as 1. 
    one_year_ago = today - relativedelta(years= 1)
    # Dates format 'YYYY-MM-DD' to decide for how many days I want the rain information ans use relativedelta to come back to the previous month in case of values <= 0. 
    reqDates = {
        'min_date': (one_year_ago - relativedelta(days=2)).strftime('%Y-%m-%d'),
        'max_date': one_year_ago.strftime('%Y-%m-%d')
    }

    # URL API ARPA Piemonte website
    # By using ‘f’ I can create a binding and make the call dynamic based on the date parameters
    arpa_api_url = f"https://utility.arpa.piemonte.it/meteoidro/dati_giornalieri_meteo/?fk_id_punto_misura_meteo={request.args.get('fk_id_punto_misura_meteo')}&data_min={reqDates['min_date']}&data_max={reqDates['max_date']}"

    # Make the GET request to the ARPA Piemonte API documentation
    try:
        response = requests.get(arpa_api_url)
        response.raise_for_status()  # create an exception if the request has a negative result
        data = response.json()  # conversion of the JSON response into a Python dictionary
        # Plot the data
        if 'results' in data:
            location = request.args.get('location')
            return {'data': data, 'location': location, 'dates': reqDates}, 200
        else:
            # Create an error if no rainy days data are found
            print(f"Nessun dato di ptot trovato dalla data: {reqDates['min_date']} alla data: {reqDates['max_date']}")
    except requests.exceptions.RequestException as e:
        print("Errore durante la richiesta:", e)

# Debug modality on
if __name__ == "__main__":
    app.run(debug=True)
