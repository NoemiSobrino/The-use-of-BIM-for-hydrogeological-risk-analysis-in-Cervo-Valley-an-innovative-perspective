import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import cross_origin

# Flask allows the Python server to communicate with the map in index.html
# Initialize the Flask class
app = Flask(__name__)

# Define the route to be contacted via JS
@app.route("/get_pluviometer")
# Disable cross origin to have two separate servers, one for the APIs and the other for the map
@cross_origin()

# Make the API call to the ARPA Piemonte website
def call_API():
    # Take today's date
    today = datetime.now()
    # Refer today's date to a year before
    one_year_ago = today.replace(year=today.year - 1)
    # Dates format 'YYYY-MM-DD' to decide for how many days I want the rain information
    reqDates = {
        'min_date': one_year_ago.replace(day=one_year_ago.day - 2).strftime('%Y-%m-%d'),
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
            print(f"No data found from date: {reqDates['min_date']} to date: {reqDates['max_date']}")
    except requests.exceptions.RequestException as e:
        print("Error during the request:", e)

# Activate debug mode
if __name__ == "__main__":
    app.run(debug=True)
