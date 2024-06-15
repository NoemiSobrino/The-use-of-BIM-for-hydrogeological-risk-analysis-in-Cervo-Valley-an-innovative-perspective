#requests makes https calls
import requests
#It allows to use dates
from datetime import datetime
#Creates a virtual server to make the API call to ARPA website
from flask import Flask, request
#Remove the CORS Origin mechanism for the API call made by the JS file
from flask_cors import cross_origin
#It calculates the minimum date time moving to the previous month without considering values = to 0
from dateutil.relativedelta import relativedelta


# Flask allows the communication between the virtual Python server and the web map with index.hatml
# Initialization of Flask class
app = Flask(__name__)

# Define the route for the API call in the JS file
@app.route("/get_pluviometer")
# Deactivate the CORS origin. In that way I have two different servers, one for the API call and one for the map and they can communicate because I deactivated the CORS mechanism
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
        response = requests.get(arpa_api_url) # take the response from the API call made in ARPA Piemonte website
        response.raise_for_status()  # create an error if the request has a negative result
        data = response.json()  # conversion of the JSON response into a Python dictionary
        # Plot the data
        if 'results' in data:
            location = request.args.get('location')
            return {'data': data, 'location': location, 'dates': reqDates}, 200
        else:
            # Create an error if no rainy days data are found
            print(f"No precipitation (ptot) data found from: {reqDates['min_date']} to: {reqDates['max_date']}")
    except requests.exceptions.RequestException as e:
        print("Request error:", e)

# Debug modality on. If some errors occur, they are visualized in the terminal
if __name__ == "__main__":
    app.run(debug=True)
