// Function that obtains the precipitation data for a set day
async function getPtotDataForDate(fk_id_punto_misura_meteo, location) {
  // API call to Python virtual server by using fk_id_punto_misura_meteo and location with GET method
  try {
    const response = await fetch(
      `http://127.0.0.1:5000/get_pluviometer?` +
        new URLSearchParams({
          fk_id_punto_misura_meteo,
          location,
        }),
      { method: "GET" }
    );
    // Response saving 
    const res = JSON.parse((await response.text()).toString());
    if (res.data.results) {
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
async function plotPtotDataForDate(res) {
  // Definition of which graph do I have to create
  // In the future with more cities it is possible to use a Switch (instruction to replace multiple if)
  var ctx =
    res.location === "BIELLA"
      ? document.getElementById("BIELLA").getContext("2d")
      : document.getElementById("PIEDICAVALLO").getContext("2d");
  // Graph realization with API data
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: res.data.results.map((x) => x.data),
      datasets: [
        {
          label: `RAINFALL in ${res.location} from ${res.dates.min_date} to ${res.dates.max_date} [mm]`,
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
