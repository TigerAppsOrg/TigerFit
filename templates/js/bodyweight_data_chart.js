function setup_bodyweight() {
  handleBodyweightChartUpdate(null);
}
$(document).ready(() => {
  setup_bodyweight();
});

$(document).ready(() => {
  // Weight recommendation jQuery
  $(document).on("submit", "#bodyweight_chart_form", function (event) {
    //if (!isNaN($(this).val()) && Number.isInteger(parseFloat($(this).val())) && $(this).val() !== "") {
    // <!-- ? all cases work ? -->
    console.log("Handling update...");
    handleBodyweightChartUpdate($("#bodyweight_input").val());

    event.preventDefault();
  });
});
$(document).ready(() => {
  $('[data-toggle="tooltip"]').tooltip({
    placement: "top",
  });
});

function handleBodyweightChartUpdate(bodyweight) {
  let user_name = "{{ user_name }}";
  let url =
    "/update_bodyweight_chart?user_name=" +
    encodeURIComponent(user_name) +
    "&bodyweight=" +
    encodeURIComponent(bodyweight);
  console.log("url", url);

  console.log("Updating...");

  // if (request != null) request.abort() // ? confused about this

  let request = $.ajax({
    type: "GET",
    url: url,
    success: updateBodyweightChart,
  });
}

function updateBodyweightChart(response) {
  console.log("reached the response function");

  if (response.is_empty) {
    console.log("reponse is empty");
    $(`#bodyweight_chart_canvas_container`).css("display", "none");
    return;
  }
  $(`#bodyweight_chart_canvas_container`).css("display", "block");

  // Create daily change text
  let fragment = "";
  if (response.good_change) {
    fragment = "<strong style='color: lime'>";
  } else {
    fragment = "<strong style='color: red'>";
  }
  fragment += "Daily Change: ";
  if (response.change > 0) {
    fragment += "+";
  }
  fragment += response.change;
  fragment += " lbs</strong>";
  $("#bodyweight_change_container").html(fragment);

  // Graph data on chart canvas
  let bodyweight_data = response.bodyweight_data;
  data = []; // to be sent to chart data

  if (Object.keys(bodyweight_data).length > 0) {
    // Push bodyweight dataset to line plot
    data.push({
      showLine: true,
      label: `Weight (lbs)`,
      borderColor: "#FFA500",
      backgroundColor: "#FFA50055",
      data: bodyweight_data["bw_dataset"],
      fill: true,
      pointBackgroundColor: "#FFA500",
      pointRadius: 2,
      tension: 0.01,
    });
    // Push goal dataset to dotted line plot
    data.push({
      showLine: true,
      label: `Goal Weight (lbs)`,
      borderColor: "lime",
      backgroundColor: "#0000",
      // Take first and last data point from goal
      data: [
        bodyweight_data["goal_dataset"][0],
        bodyweight_data["goal_dataset"][
          bodyweight_data["goal_dataset"].length - 1
        ],
      ],
      fill: false,
      pointRadius: 2,
      borderDash: [10, 5],
    });

    let ctx = document
      .getElementById("bodyweight_chart_canvas")
      .getContext("2d");
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

    let darkMode = localStorage.getItem("theme") === "dark";

    let chart = new Chart(ctx, {
      type: "scatter",
      data: { datasets: data },
      options: {
        aspectRatio: 3,
        responsive: true,
        maintainAspectRatio: false,
        //title: {
        //    display: true,
        //    text: `Bodyweight - Past Data`
        //},
        reponsive: true,
        scales: {
          xAxes: [
            {
              type: "time",
              ticks: {
                fontColor: darkMode ? "white" : "grey",
                color: darkMode ? "white" : "grey",
              },
              gridLines: {
                color: darkMode ? "grey" : "grey", // Change the color of the gridlines
              },
              time: {
                unit: "month",
              },
            },
          ],
          yAxes: [
            {
              scaleLabel: {
                display: true,
                labelString: "Body Weight (lbs)",
                fontColor: darkMode ? "white" : "grey",
              },
              ticks: {
                beginAtZero: false,
                fontColor: darkMode ? "white" : "grey",
              },
              gridLines: {
                color: darkMode ? "grey" : "grey", // Change the color of the gridlines
              },
            },
          ],
        },
        legend: {
          labels: {
            fontColor: darkMode ? "white" : "grey", // Change the font color of the legend labels
          },
        },
        tooltips: {
          enabled: true,
          mode: "single",
          callbacks: {
            label: function (tooltipItems, data) {
              console.log("items", tooltipItems);
              let tooltip = "";
              if (tooltipItems.datasetIndex === 0) {
                tooltip = `${tooltipItems.xLabel}: ${tooltipItems.yLabel} lbs`;
              } else {
                tooltip = `Goal Bodyweight: ${tooltipItems.yLabel} lbs`;
              }
              return tooltip;
            },
          },
        },
      },
    });
  }
}
