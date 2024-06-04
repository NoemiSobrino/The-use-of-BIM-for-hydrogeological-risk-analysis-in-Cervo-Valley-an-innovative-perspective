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

    
# Funzione per creare il grafico -> Commentata perché il grafico lo creiamo con ChartJS
# In ingresso passo i dati restituiti dall'API di ARPA Piemonte
# def plot_data(data, location, reqDates):
#     print(location, reqDates)
#     # Imposto la dimensione del grafico
#     plt.figure(figsize=(70, 30))
#     # Inizializzo due array di date e valori di ptot
#     dates = []
#     ptot_values = []
#     # Esegui un ciclo per ottenere i dati di ptot
#     for entry in data['results']:
#         date = datetime.strptime(entry['data'], '%Y-%m-%d') # Salvo la data in 'entry' convertita nel formato 'YYYY-MM-DD'
#         ptot_value = entry.get('ptot') # Salvo il valore di ptot in 'entry'
#         # Controllo se ci sono dati di ptot trovati
#         if ptot_value is not None:
#             dates.append(date) # Aggiungo in fondo alla lista 'dates' il valore di 'date'
#             ptot_values.append(ptot_value) # Aggiungo in fondo alla lista 'ptot_values' il valore di 'ptot_value'
#     plt.bar(dates, ptot_values, color='blue')  # Plotta il grafico con tutte le date sull'asse x
#     plt.xlabel('Date', fontsize=50, fontweight='bold') # Imposto la labale dell'asse x
#     plt.ylabel('Total rainfall (mm)', fontsize=50, fontweight='bold') # Imposto la labale dell'asse y
#     plt.title(f"RAINFALL in {location} on {reqDates['min_date']} to {reqDates['max_date']}", fontsize=50, fontweight='bold') # Imposto il titolo nel grafico
#     plt.xticks(fontsize=50)  # Modifica la dimensione del testo sull'asse x
#     plt.yticks(fontsize=50)  # Modifica la dimensione del testo sull'asse y
#     plt.gca().xaxis.set_major_locator(DayLocator(interval=1)) # Imposta lo spaziamento tra le date sull'asse x
#     plt.grid(True) # Mostro la griglia
#     #plt.tight_layout() # Imposto il layout del grafico
#     #plt.show()
#     my_stringIObytes = io.BytesIO() # Creo un oggetto BytesIO che mi permette di lavorare in un sistema binario dentro la memoria del PC
#     plt.savefig(my_stringIObytes, format='jpg') # Salvo l'immagine nel file BytesIO come png
#     my_stringIObytes.seek(0) # Permette la lettura dei dati dalla prima posizione del base64
#     my_base64_jpgData = {'data': data, 'image_url': base64.b64encode(my_stringIObytes.read()).decode()} # Creo un dizionario Python con i dati dell'immagine e quello che mi restituisce l'API
#     return my_base64_jpgData # Restituisco il dizionario per JS