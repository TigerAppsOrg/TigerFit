$(document).ready(() => {
  // Weight recommendation jQuery
  $(document).on(
    "input",
    'input[type="number"][name$="reps"]',
    function () {
      if (
        !isNaN($(this).val()) &&
        Number.isInteger(parseFloat($(this).val())) &&
        $(this).val() !== ""
      ) {
        recommendWeight($(this));
      } else {
        handleWeightRecommendation({
          element_name: $(this).prop("name"),
          weight_recommendation: 0,
        });
      }
    }
  );

  // Rep recommendation jQuery
  $(document).on(
    "input",
    'input[type="number"][name$="weight"]',
    function () {
      console.log("A");
      if (!isNaN($(this).val()) && $(this).val() !== "") {
        console.log("REP REC");
        recommendReps($(this));
      } else {
        handleRepsRecommendation({
          element_name: $(this).prop("name"),
          reps_recommendation: 0,
        });
      }
    }
  );
});

// Weight Recommendation Functions
function handleWeightRecommendation(response) {
  console.log("handling weight...");
  console.log("response", response);
  console.log(
    "insert ph",
    response.element_name.slice(0, -4) + "weight"
  );

  // Return "Weight" placeholder for invalid inputs
  let weight_recommendation = response.weight_recommendation;
  if (
    weight_recommendation === 0 ||
    response.element_name === undefined
  ) {
    let insert_id = `#${response.element_name.slice(0, -4)}weight`;
    $(insert_id).prop("placeholder", `Weight`);
    return;
  }

  let weight_90percent =
    Math.round(2 * 0.9 * response.weight_recommendation) / 2;
  let weight_max = Math.round(2 * response.weight_recommendation) / 2;

  let insert_id = `#${response.element_name.slice(0, -4)}weight`;
  let ph = `${weight_90percent}-${weight_max} lbs`;
  $(insert_id).prop("placeholder", ph);

  // Add placeholder to localstorage
  localStorage.setItem(
    `${response.element_name.slice(0, -4)}weight_ph`,
    ph
  );
}

function recommendWeight(element) {
  let user_name = "{{ user_name }}"; // <!-- * good? -->
  let element_name = element.prop("name");
  let equipment_dropdown_id = `#${
    element_name.split("_")[0]
  }_equipment_name`;
  let equipment_name = $(equipment_dropdown_id).val();
  let reps = element.val();

  // No equipment selected
  if (equipment_name === "") {
    handleWeightRecommendation({
      element_name: element_name,
      weight_recommendation: 0,
    });
    return;
  }
  console.log("equip name", $(equipment_dropdown_id).val());

  let url =
    "/recommend_weight?user_name=" +
    encodeURIComponent(user_name) +
    "&equipment_name=" +
    encodeURIComponent(equipment_name) +
    "&reps=" +
    encodeURIComponent(reps) +
    "&element_name=" +
    encodeURIComponent(element_name);
  console.log("url", url);

  console.log("Recommending...");
  console.log("val", element.val());

  // if (request != null) request.abort()

  let request = $.ajax({
    type: "GET",
    url: url,
    success: handleWeightRecommendation,
  });
}

// Rep Recommendation Functions
function handleRepsRecommendation(response) {
  console.log("handling reps...");
  console.log("response", response);
  console.log("insert ph", response.element_name.slice(0, -6) + "reps");

  // Return "Reps" placeholder for invalid inputs
  let reps_recommendation = response.reps_recommendation;
  if (
    reps_recommendation === 0 ||
    response.element_name === undefined
  ) {
    let insert_id = `#${response.element_name.slice(0, -6)}reps`;
    $(insert_id).prop("placeholder", `Reps`);
    return;
  }

  let reps_80percent = Math.round(0.8 * response.reps_recommendation);
  let reps_max = Math.round(response.reps_recommendation);
  let ph = "";
  console.log("REPS MAX = ", reps_max);

  let insert_id = `#${response.element_name.slice(0, -6)}reps`;
  if (reps_max < 1) {
    ph = "Reps";
  } else if (reps_max === reps_80percent) {
    ph = `${reps_max} reps`;
  } else if (reps_80percent >= 20) {
    ph = `20+ reps`;
  } else {
    ph = `${reps_80percent}-${reps_max} reps`;
  }

  // Insert correct placeholder into input
  $(insert_id).prop("placeholder", ph);

  // Add placeholder to localstorage
  localStorage.setItem(
    response.element_name.slice(0, -6) + "reps_ph",
    ph
  );
}

function recommendReps(element) {
  let user_name = "{{ user_name }}"; // <!-- * good? -->
  let element_name = element.prop("name");
  let equipment_dropdown_id = `#${
    element_name.split("_")[0]
  }_equipment_name`;
  let equipment_name = $(equipment_dropdown_id).val();
  let weight = element.val();

  // No equipment selected
  if (equipment_name === "") {
    handleRepsRecommendation({
      element_name: element_name,
      reps_recommendation: 0,
    });
    return;
  }
  console.log("equip name", $(equipment_dropdown_id).val());

  let url =
    "/recommend_reps?user_name=" +
    encodeURIComponent(user_name) +
    "&equipment_name=" +
    encodeURIComponent(equipment_name) +
    "&weight=" +
    encodeURIComponent(weight) +
    "&element_name=" +
    encodeURIComponent(element_name);
  console.log("url", url);

  console.log("Recommending...");
  console.log("val", element.val());

  // if (request != null) request.abort()

  let request = $.ajax({
    type: "GET",
    url: url,
    success: handleRepsRecommendation,
  });
}
