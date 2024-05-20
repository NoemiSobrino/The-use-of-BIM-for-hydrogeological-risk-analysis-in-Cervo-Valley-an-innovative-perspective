import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import cross_origin

# Flask permette di far comunicare il server python con la mappa in index.html
# Inizializzo la classe Flask
app = Flask(__name__)

# Definisco la rotta da contattare tramite JS
@app.route("/get_pluviometer")
# Disattivo il cross origin così da avere due server separati, uno per le APIs e l'altro per la mappa
@cross_origin()

# Make the API call to the ARPA Piemonte website
def call_API():
    # Take the today date
    today = datetime.now()
    # Refer the today date to a year before
    one_year_ago = today.replace(year=today.year - 1)
    # Dates format 'YYYY-MM-DD' to decide for how many days I want the rainy infromation
    reqDates = {
        'min_date': one_year_ago.replace(day=one_year_ago.day - 2).strftime('%Y-%m-%d'),
        'max_date': one_year_ago.strftime('%Y-%m-%d')
    }

    # URL API ARPA Piemonte website
    # By using ‘f’ I can create a binding and make the call dynamic in function of the dates parameters
    arpa_api_url = f"https://utility.arpa.piemonte.it/meteoidro/dati_giornalieri_meteo/?fk_id_punto_misura_meteo={request.args.get('fk_id_punto_misura_meteo')}&data_min={reqDates['min_date']}&data_max={reqDates['max_date']}"

    # Make the GET request to the ARPA Piemonte API documentation
    try:
        response = requests.get(arpa_api_url)
        response.raise_for_status()  # create an exception is the request has a negative result
        data = response.json()  # conversion of the JSON response into a Python dictionary
        # Plot the data
        if 'results' in data:
            location = request.args.get('location')
            return {'data': data, 'location': location, 'dates': reqDates}, 200
        else:
            # Create an error is no rainy days data are found
            print(f"Nessun dato di ptot trovato dalla data: {reqDates['min_date']} alla data: {reqDates['max_date']}")
    except requests.exceptions.RequestException as e:
        print("Errore durante la richiesta:", e)

# Attivo la modalità di debug
if __name__ == "__main__":
    app.run(debug=True)