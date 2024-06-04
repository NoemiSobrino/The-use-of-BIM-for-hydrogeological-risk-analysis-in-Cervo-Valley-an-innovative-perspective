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

# Esegue la chiamata effettiva verso l'API di ARPA Piemonte
def call_API():
    # Ottieni la data di oggi
    today = datetime.now()
    # Sottrai a today un anno con relativedelta che non accetta valori = a 0. Usare years e non year, altrimenti l'anno viene riportato a 1
    one_year_ago = today - relativedelta(years= 1)
    # Creo un oggetto di date formattate in 'YYYY-MM-DD' in modo da poter decidere dinamicamente per quanti giorni ottenere i dati di ptot e uso sempre il metodo relativedelta per tornare indietro al mese precedente in caso di valore = o inferiore a 0 
    reqDates = {
        'min_date': (one_year_ago - relativedelta(days=2)).strftime('%Y-%m-%d'),
        'max_date': one_year_ago.strftime('%Y-%m-%d')
    }

    # URL dell'API di ARPA Piemonte
    # Tramite 'f'posso eseguire un binding e rendere dinamica la chiamata in base ai parameti dates
    arpa_api_url = f"https://utility.arpa.piemonte.it/meteoidro/dati_giornalieri_meteo/?fk_id_punto_misura_meteo={request.args.get('fk_id_punto_misura_meteo')}&data_min={reqDates['min_date']}&data_max={reqDates['max_date']}"

    # Effettua la richiesta GET all'API di ARPA Piemonte
    try:
        response = requests.get(arpa_api_url)
        response.raise_for_status()  # solleva un'eccezione se la richiesta ha avuto esito negativo
        data = response.json()  # converte la risposta JSON in un dizionario Python
        # Stampa i dati
        if 'results' in data:
            location = request.args.get('location')
            return {'data': data, 'location': location, 'dates': reqDates}, 200
        else:
            # Sollevo un'eccezione se non ci sono dati di ptot trovati
            print(f"Nessun dato di ptot trovato dalla data: {reqDates['min_date']} alla data: {reqDates['max_date']}")
    except requests.exceptions.RequestException as e:
        print("Errore durante la richiesta:", e)

# Attivo la modalità di debug
if __name__ == "__main__":
    app.run(debug=True)
