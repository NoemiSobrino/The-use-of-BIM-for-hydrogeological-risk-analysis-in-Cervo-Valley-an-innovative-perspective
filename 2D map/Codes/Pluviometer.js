// Function that obtain the precipitation data for a set day
async function getPtotDataForDate(fk_id_punto_misura_meteo, location) {
  // API call to Python virtual server by using fk_id_punto_misura_meteo and location with GET method
  try {
    const response = await fetch(
      `http://127.0.0.1:5000/get_pluviometer?` + // This is the server of the map
        new URLSearchParams({ // This is a JavaScript class able to work with URL links. In this case it considers the following two specific parameters
          fk_id_punto_misura_meteo, // Identification code of the pluviometer (Biella or Piedicavallo)
          location, // Name of the pluviometer location (Biella or Piedicavallo)
        }),
      { method: "GET" }
    );
    // Save the response and converts it into a JSON object. This conversion is necessary to make possible the interpretation of the data into the JS
    const res = JSON.parse((await response.text()).toString());
    if (res.data.results) { // res should have an attribute 'data' (that indicates the day) that should have an attribute 'results' (that indicates the value of ptot) in the API call
      // If a response is available, I give it to the function caller
      return res;
    } else {
      // No response = error
      console.log(`No data founded`);
      return null;
    }
  } catch (error) {
    // Service error = error 
    console.error("Error during the API call:", error);
    return null;
  }
}

// Function to plot the precipitation data ptot for a specific day
async function plotPtotDataForDate(res) { // res is the response provided by the API call from the previous function
  // Definition of which graph do I have to create
  // In the future with more cities it is possible to use a Switch (instruction to replace multiple if)
  var ctx =
    res.location === "BIELLA"
      ? document.getElementById("BIELLA").getContext("2d") // The context is necessary to draw the graph according to the Chart.js library
      : document.getElementById("PIEDICAVALLO").getContext("2d");
  // Graph realization with API data by using Chart.js library
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: res.data.results.map((x) => x.data),
      datasets: [
        {
          label: `RAINFALL in ${res.location} from ${res.dates.min_date} to ${res.dates.max_date} [mm]`, // min_date and max_date are the same of Python
          data: res.data.results.map((x) => x.ptot),
          backgroundColor: "blue",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}
