function titleCase(str) {
  return str
    .toLowerCase()
    .split(" ")
    .map(function (word) {
      return word.charAt(0).toUpperCase() + word.slice(1);
    })
    .join(" ");
}

// Filters list of equipment, given selected main muscle group
$(document).ready(() => {
  $(document).on("change", "#main_muscle_group_select", function () {
    if ($(this).data("options") === undefined) {
      // Array of all options
      $(this).data("options", $("#equipment_card_list label").clone());
    }

    let main_group = $(this).val();
    let options = "";

    // Filter options with only correct main_group
    if (main_group === "All") {
      options = $(this)
        .data("options")
        .filter(function () {
          if ($("#modal-equipment-search-bar").val() === "") {
            return true;
          }
          if ($(this).hasClass("custom-equipment")) {
            return false;
          }
          return $(this)
            .data("equipment_name")
            .toLowerCase()
            .includes(
              $("#modal-equipment-search-bar").val().toLowerCase()
            );
        });
    } else {
      options = $(this)
        .data("options")
        .filter("[data-main_group=" + main_group + "]")
        .filter(function () {
          if ($("#modal-equipment-search-bar").val() === "") {
            return true;
          }
          if ($(this).hasClass("custom-equipment")) {
            return false;
          }
          return $(this)
            .data("equipment_name")
            .toLowerCase()
            .includes(
              $("#modal-equipment-search-bar").val().toLowerCase()
            );
        });
    }
    $("#equipment_card_list").html(options);
  });
  $(document).on("input", "#modal-equipment-search-bar", function () {
    if ($("#main_muscle_group_select").data("options") === undefined) {
      // Array of all options
      $("#main_muscle_group_select").data(
        "options",
        $("#equipment_card_list label").clone()
      );
    }

    let main_group = $("#main_muscle_group_select").val();
    let options = "";

    // Filter options with only correct main_group
    if (main_group === "All") {
      options = $("#main_muscle_group_select")
        .data("options")
        .filter(function () {
          if ($("#modal-equipment-search-bar").val() === "") {
            return true;
          }
          if ($(this).hasClass("custom-equipment")) {
            return false;
          }
          return $(this)
            .data("equipment_name")
            .toLowerCase()
            .includes(
              $("#modal-equipment-search-bar").val().toLowerCase()
            );
        });
    } else {
      options = $("#main_muscle_group_select")
        .data("options")
        .filter("[data-main_group=" + main_group + "]")
        .filter(function () {
          if ($("#modal-equipment-search-bar").val() === "") {
            return true;
          }
          if ($(this).hasClass("custom-equipment")) {
            return false;
          }
          return $(this)
            .data("equipment_name")
            .toLowerCase()
            .includes(
              $("#modal-equipment-search-bar").val().toLowerCase()
            );
        });
    }

    // Filter options based on search query
    // options = options.data("options").filter(":contains('ben')");

    $("#equipment_card_list").html(options);
  });
});

// Populates selected equipment piece in form input
$(document).ready(() => {
  $(document).on("click", "#select_equipment_button", function () {
    console.log("clicked button");
    let selected_equip_name = $(
      'input[name="equipment_list_radios"]:checked'
    ).data("equipment_name");
    if (selected_equip_name === "custom-equipment-placeholder") {
      selected_equip_name = $("#custom-equipment-input").val();
      if (selected_equip_name === "") {
        return;
      }
    }
    if (selected_equip_name === undefined) return;

    // Uncheck all radio buttons
    $(".checkbox").prop("checked", false);

    selected_equip_name = titleCase(selected_equip_name);

    // Set values to be sent sent back to input, and hide modal
    $(`#hidden-chart-equipment-name`).val(selected_equip_name);
    $(`#hidden-chart-equipment-name`).trigger("change");
    $(`#chart-equipment-name-header`).html(selected_equip_name);
    $(`#chart-equipment-name-header`).css("color", "orange");
    $("#equipment-modal").modal("hide");

    console.log(`Selected ${selected_equip_name}`);
  });
});

// Disable select_equipment_button when not clickable
$(document).ready(() => {
  $(document).on(
    "change",
    'input[name="equipment_list_radios"]',
    function () {
      // alert($(this).data("equipment_name"));
      let selected_equip_name = $(this).data("equipment_name");

      if (selected_equip_name === undefined) {
        disableButton("select_equipment_button");
      } else if (
        selected_equip_name === "custom-equipment-placeholder" &&
        $("#custom-equipment-input").val() === ""
      ) {
        disableButton("select_equipment_button");
      } else {
        selected_equip_name = titleCase(selected_equip_name);
        enableButton("select_equipment_button");
      }
    }
  );
  $(document).on("input", "#custom-equipment-input", function () {
    let selected_equip_name = $(
      'input[name="equipment_list_radios"]:checked'
    ).data("equipment_name");
    console.log("On input: ", selected_equip_name);
    if (selected_equip_name === undefined) {
      disableButton("select_equipment_button");
    } else if (
      selected_equip_name === "custom-equipment-placeholder" &&
      $(this).val() === ""
    ) {
      disableButton("select_equipment_button");
    } else {
      selected_equip_name = titleCase(selected_equip_name);
      enableButton("select_equipment_button");
    }
  });
});

function disableButton(id) {
  $(`#${id}`).prop("disabled", true);
  $(`#${id}`).removeClass("btn-green");
  $(`#${id}`).addClass("btn-grey");
}
function enableButton(id) {
  $(`#${id}`).prop("disabled", false);
  $(`#${id}`).removeClass("btn-grey");
  $(`#${id}`).addClass("btn-green");
}

// Two functions used to hash a string to a random color
function hashCode(str) {
  var hash = 0;
  for (var i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  return hash;
}
function intToRGB(i) {
  var c = (i & 0x00ffffff).toString(16).toUpperCase();
  console.log("test");
  return "00000".substring(0, 6 - c.length) + c;
}

// Runs onclick of add_exercise_button (at start of modal popup)
$(document).ready(() => {
  $(document).on("click", "#equipment-chart-button", function () {
    $(".badge").each(function () {
      $(this).css(
        "background",
        `#${intToRGB(hashCode($(this).html()))}55`
      );
    });

    let selected_equip_name = $(this).data("equipment_name");
    if (selected_equip_name === undefined) {
      disableButton("select_equipment_button");
    }
  });
});

// START OF WACKY COPY PASTE
// Opens modal on click of "more info" button
$(document).ready(() => {
  $(document).on("click", "#more_ex_info_button", function () {
    // retrieve data from data container div element
    let data_mule = $(this).siblings(".data-mule");

    // ! test
    //install using 'npm install utf8'
    // const utf8 = require("utf8");
    // utf8.encode(string);

    // set contents of each div dynamically
    $("#more-ex-info-header").text(
      data_mule.attr("data-equipment_name")
    );
    $("#more-ex-info-gif").attr("src", data_mule.attr("data-gif_path"));
    $("#more-ex-info-body").text(
      data_mule.attr("data-equipment_description")
    );

    // hide/show modal
    console.log(
      "Additional info modal button clicked. Toggling modal..."
    );
    $("#more-ex-info-modal").modal("toggle");
  });
});

// Closes (toggles) the nested modal after clicking the "info" icon
$(document).ready(() => {
  $(document).on("click", "#close-modal-btn", function () {
    // close outer modal on 'close button' click
    $("#more-ex-info-modal").modal("toggle");
  });
});

// Opens modal of QR scanner
$(document).ready(() => {
  $(document).on("click", "#qr-btn", function () {
    $("#qr-modal").modal("toggle");
  });
});

// CLoses qr
$(document).ready(() => {
  $(document).on("click", "#close-qr-btn", function () {
    $("#qr-modal").modal("toggle");
  });
});

// END OF WACKY COPY PASTE

// Inserted scripts to generate chart
function setup_equipment() {
  //default_equip_name = "Back Squat"
  let default_equip_name = "{{first_used_equipment}}";
  if (default_equip_name != "") {
    $(`#chart-equipment-name-header`).html(default_equip_name);
    $(`#chart-equipment-name-header`).css("color", "orange");
  }

  let default_date_range = "All Time";
  handleEquipmentChartUpdate(default_equip_name, default_date_range);
}
$(document).ready(() => {
  setup_equipment();
});

$(document).ready(() => {
  // On change of main muscle group, filter options for equipment
  //$(document).on('change', '#equipment_main_muscle_group_select', function () {
  //    if ($(this).data('options') === undefined) {
  //        // Array of all options
  //        $(this).data('options', $('#datalist_options option').clone());
  //    }
  //    console.log("Main group changed...")
  //
  //    //$('#equipment_chart_form').submit()
  //    let main_group = $(this).val();
  //    localStorage.setItem('equipment_main_muscle_group_select', main_group)
  //
  //    // Filter options with only correct main_group
  //    let options = $(this).data('options').filter('[data-main_group=' + main_group + ']');
  //    $('#datalist_options').html(options);
  //});

  // On change of equipment name, set localstorage and submit form
  $(document).on("change", "#hidden-chart-equipment-name", function () {
    //localStorage.setItem('equipment_name', $('#equipment_name').val())
    //$('#equipment_chart_form').submit()
    console.log("Handling change...");
    console.log("VAL", $(this).val());

    handleEquipmentChartUpdate($(this).val(), $("#date_range").val());
  });

  // On change of date range, set localstorage and submit form
  $(document).on("change", "#date_range", function () {
    //localStorage.setItem('date_range', $('#date_range').val())
    //$('#equipment_chart_form').submit()

    handleEquipmentChartUpdate(
      $("#hidden-chart-equipment-name").val(),
      $(this).val()
    );
  });
});

function handleEquipmentChartUpdate(equipment_name, date_range) {
  let user_name = "{{ user_name }}";
  let url =
    "/update_equipment_chart?user_name=" +
    encodeURIComponent(user_name) +
    "&equipment_name=" +
    encodeURIComponent(equipment_name) +
    "&date_range=" +
    encodeURIComponent(date_range);
  console.log("url", url);

  console.log("Updating...");

  // if (request != null) request.abort() // ? confused about this

  let request = $.ajax({
    type: "GET",
    url: url,
    success: updateEquipmentChart,
  });
}

function updateEquipmentChart(response) {
  let rep_range_data = response.rep_range_data;
  let chartData = response.data;
  console.log("chart data", rep_range_data);

  let isEmptyChart = false;
  if (Object.keys(rep_range_data).length === 0) {
    isEmptyChart = true;
  }

  // let equipment_name = chartData.equipment_name;
  // let date_range = chartData.date_range;
  let data = []; // to be sent to chart data

  // Hard-coded rep-ranges and constants (in agreement with python file)
  let chart_constants = [
    {
      label: "1",
      rep_range: "1",
      color: "#FF000055",
    },
    {
      label: "2-6",
      rep_range: "2_6",
      color: "#FFA50055",
    },
    {
      label: "7-12",
      rep_range: "7_12",
      color: "#0000FF55",
    },
    {
      label: "13+",
      rep_range: "13_plus",
      color: "#00FF0055",
    },
  ];

  if (!isEmptyChart) {
    // Push given dataset to line plot
    let push_line_data = (label, rep_range, color) => {
      data.push({
        showLine: true,
        label: `${label} Rep Trend`,
        borderColor: color,
        data: rep_range_data[`rep_range_${rep_range}_avgs`],
        fill: false,
        pointRadius: 0,
        order: 1,
      });
    };
    // Push given dataset to scatter plot
    let push_scatter_data = (label, rep_range, color) => {
      data.push({
        label: `${label} Reps`,
        borderColor: color,
        multiTooltipTemplate: "label : lbs",
        data: rep_range_data[`rep_range_${rep_range}`],
        pointBackgroundColor: rep_range_data[
          `rep_range_${rep_range}_failed`
        ].map((failed) => (failed ? "white" : color)),
        order: 0,
      });
    };

    // Push all rep-range data sets to both scatter and line plots
    for (let set of chart_constants) {
      let { label, rep_range, color } = set;
      push_line_data(label, rep_range, color);
      push_scatter_data(label, rep_range, color);
    }
  }

  let ctx = document
    .getElementById("equipment_chart_canvas")
    .getContext("2d");
  let chart = new Chart(ctx, {
    type: "scatter",
    data: { datasets: data },
    options: {
      title: {
        display: isEmptyChart,
        text: `No Data to Display`,
      },
      maintainAspectRatio: false,
      scales: {
        xAxes: [
          {
            type: "time",
            time: {
              unit: "day",
            },
          },
        ],
        yAxes: [
          {
            scaleLabel: {
              display: true,
              labelString: "Lifted Weight (lbs)",
            },
          },
        ],
      },
      tooltips: {
        enabled: true,
        mode: "single",
        callbacks: {
          label: function (tooltipItems, data) {
            // Add 1 when even (to catch error when you click on the
            // line below the dataset)
            if (tooltipItems.datasetIndex % 2 === 0) {
              tooltipItems.datasetIndex += 1;
            }

            // Provide advanced tooltip descriptions
            let dataset_index = tooltipItems.datasetIndex;
            let rep_range = "13_plus";
            if (dataset_index === 1) rep_range = "1";
            else if (dataset_index === 3) rep_range = "2_6";
            else if (dataset_index === 5) rep_range = "7_12";

            let num_reps =
              rep_range_data[`rep_range_${rep_range}_num_reps`][
                tooltipItems.index
              ];

            let failed =
              data.datasets[tooltipItems.datasetIndex]
                .pointBackgroundColor[tooltipItems.index] === "white";
            let tooltip = `${tooltipItems.xLabel}: ${num_reps} reps, ${tooltipItems.yLabel} lbs`;
            if (failed) tooltip += " [Failed]";
            return tooltip;
          },
        },
      },
      legend: {
        position: "top",
        // Remove labels that include "Rep Trend" string
        labels: {
          filter: function (item, chart) {
            return !item.text.includes("Rep Trend");
          },
        },
        // Disables rep ranges OTHER than one clicked on in legend
        onClick: function (e, legendItem) {
          let index = legendItem.datasetIndex;
          let ci = this.chart;
          let alreadyHidden =
            ci.getDatasetMeta(index).hidden === null
              ? false
              : ci.getDatasetMeta(index).hidden;

          ci.data.datasets.forEach(function (e, i) {
            let meta = ci.getDatasetMeta(i);

            if (i !== index) {
              if (!alreadyHidden) {
                meta.hidden =
                  meta.hidden === null ? !meta.hidden : null;
              } else if (meta.hidden === null) {
                meta.hidden = true;
                meta = ci.getDatasetMeta(i - 1);
                meta.hidden = true;
              }
            } else if (i === index) {
              meta.hidden = null;
              meta = ci.getDatasetMeta(i - 1);
              meta.hidden = null;
            }
          });

          ci.update();
        },
      },
    },
  });
}

$(document).ready(() => {
  $('[data-toggle="tooltip"]').tooltip({
    placement: "top",
  });
});
