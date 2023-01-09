// Let local storage be current contents of form
let set_local_storage = () => {
  let storage = $("#add_workout_form").prop("outerHTML");
  localStorage.setItem("html", storage);
};

// Adds "required" attribute to non-hidden, number inputs
let add_required_attribute = () => {
  $("#add_workout_form input").each(function () {
    let this_element = $(this);
    let name = this_element.attr("name");
    if (
      name != undefined &&
      !name.includes("?") &&
      this_element.attr("type") === "number"
    ) {
      console.log(this_element);
      this_element.prop("required", true);
    }
  });
};

// Restore attributes for inputs from localStorage
let restore_local_storage = (storage) => {
  $("#add_workout_form_content").html(storage);

  $(".save_value").each(function () {
    // console.log($(this).attr("name"));
    let element_name = $(this).attr("name");
    if (!element_name.includes("?")) {
      if ($(this).attr("type") == "checkbox") {
        $(this).prop("checked", localStorage.getItem(element_name));
      } else {
        console.log("ELEMENT NAME", element_name);
        $(this).val(localStorage.getItem(element_name));

        if (
          element_name.includes("weight") ||
          element_name.includes("reps")
        ) {
          $(this).attr(
            "placeholder",
            localStorage.getItem(`${element_name}_ph`)
          );
        }
      }
    }
  });
  $("#datalistInput").val(localStorage.getItem("datalistInput"));
  $("#main_muscle_group_select").val(
    localStorage.getItem("main_muscle_group_select")
  );
};

// Load current date automatically in the date input form item
// This runs once
$(document).ready(() => {
  var todayDate = new Date();
  var day = todayDate.getDate();
  var month = todayDate.getMonth() + 1;
  var year = todayDate.getFullYear();
  if (month < 10) {
    month = "0" + month;
  }
  if (day < 10) {
    day = "0" + day;
  }
  var date = year + "-" + month + "-" + day;
  $("#workout_date").attr("value", date);
});

// On page load
$(document).ready(() => {
  // Activates if form is in progress:
  let storage = localStorage.getItem("html");
  console.log("storage", storage);
  console.log("type", typeof storage);
  if (storage !== null && storage !== "undefined") {
    console.log("A");
    // Restore attributes for inputs from localStorage
    restore_local_storage(storage);
    return;
  }
  console.log("B");

  // Activates on first load of new form:
  // Create set as clone of "blueprint" set
  let clone = $(`.hidden_set`).clone();

  // Remove delete button for first set only
  // clone.find(".delete_set_button").remove();

  // Exercise 1 and set 1 instantiated
  let html = clone
    .prop("hidden", false)
    .prop("outerHTML")
    .replaceAll("?set_num?", 1);
  $(`#exercises>li>table>tbody`).append(html);

  // html = $(`.hidden_exercise`).clone().prop("hidden", false).prop("outerHTML").replaceAll("?ex_num?", 1);
  // $(`#exercises`).append(html);

  // Adds "required" attribute to non-hidden, number inputs
  add_required_attribute();
});

// On Input change of value
$(document).ready(() => {
  $(document).on("input", ".save_value", function () {
    // Used when user writes inputs but hasn't changed
    // form yet
    if (localStorage.getItem("html") === null) {
      // Let local storage be current contents of form
      set_local_storage();
    }

    // Store attributes for inputs into localStorage
    if (!$(this).attr("name").includes("?")) {
      if ($(this).attr("type") == "checkbox") {
        localStorage.setItem(
          $(this).attr("name"),
          $("this").prop("checked")
        );
      } else {
        localStorage.setItem($(this).attr("name"), $(this).val());
      }
    }
  });
});

// On .add_set_button click
$(document).ready(() => {
  $(document).on("click", ".add_set_button", function () {
    let ex_num = $(this).data("id");
    let set_num = $(`table#exercise_${ex_num}_sets>tbody>tr`).length;
    console.log(`EXNUM ${ex_num}, SETNUM ${set_num}`);

    // Append new set to correct exercise
    let html = $(`#exercise_${ex_num}_sets>tbody>tr`)
      .first()
      .clone()
      .prop("hidden", false)
      .prop("outerHTML")
      .replaceAll("?set_num?", set_num);

    $(`#exercise_${ex_num}_sets`).append(html);

    // Copy data from previous set
    if (set_num > 1) {
      // Get data from previous set
      let prev_reps = $(`input#${ex_num}_${set_num - 1}_reps`).val();
      let prev_weight = $(
        `input#${ex_num}_${set_num - 1}_weight`
      ).val();
      // Set info for newly created set
      $(`input#${ex_num}_${set_num}_reps`).val(prev_reps);
      $(`input#${ex_num}_${set_num}_weight`).val(prev_weight);

      localStorage.setItem(`${ex_num}_${set_num}_reps`, prev_reps);
      localStorage.setItem(`${ex_num}_${set_num}_weight`, prev_weight);

      //   // Store attributes for inputs into localStorage
      //   if (!$(this).attr("name").includes("?")) {
      //     if ($(this).attr("type") == "checkbox") {
      //       localStorage.setItem(
      //         $(this).attr("name"),
      //         $("this").prop("checked")
      //       );
      //     } else {
      //       localStorage.setItem($(this).attr("name"), $(this).val());
      //     }
      //   }
    }

    // Adds "required" attribute to non-hidden, number inputs
    add_required_attribute();

    // Let local storage be current contents of form
    set_local_storage();
  });
});

// On .delete_set_button click
// <button type="button" class="delete_set_button" data-ex="?ex_num" data-set="?set_num?">Delete</button>
$(document).ready(() => {
  $(document).on("click", ".delete_set_button", function () {
    let ex_num = $(this).data("ex_num");
    let set_num = $(this).data("set_num"); // set to be deleted

    // Remove deleted set
    $(`#${ex_num}_${set_num}_set`).remove();

    let num_sets_remaining =
      $(`table#exercise_${ex_num}_sets>tbody>tr`).length - 1;
    console.log("num_sets left", num_sets_remaining);
    if (num_sets_remaining === 0) {
      delete_exercise(ex_num);
    }

    // Adjust set numbers after deleting any set (excluding the last)
    if (set_num != num_sets_remaining + 1) {
      let adjusted_set_number = 1;
      $(`#exercise_${ex_num}_sets>tbody`)
        .children()
        .each(function () {
          if ($(this).prop("hidden")) {
            return;
          } else {
            $(this).attr("id", `${ex_num}_${adjusted_set_number}_set`);
            let tds = $(this).children();
            for (let i = 0; i < 4; i++) {
              switch (i) {
                case 0:
                  $(tds[i])
                    .children("input")
                    .attr(
                      "name",
                      `${ex_num}_${adjusted_set_number}_reps`
                    );
                  $(tds[i])
                    .children("input")
                    .attr(
                      "id",
                      `${ex_num}_${adjusted_set_number}_reps`
                    );
                  break;
                case 1:
                  $(tds[i])
                    .children("input")
                    .attr(
                      "name",
                      `${ex_num}_${adjusted_set_number}_weight`
                    );
                  $(tds[i])
                    .children("input")
                    .attr(
                      "id",
                      `${ex_num}_${adjusted_set_number}_weight`
                    );
                  break;
                case 2:
                  $(tds[i])
                    .children("input")
                    .attr(
                      "name",
                      `${ex_num}_${adjusted_set_number}_failed`
                    );
                  $(tds[i])
                    .children("input")
                    .attr(
                      "id",
                      `${ex_num}_${adjusted_set_number}_failed`
                    );
                  break;
                case 3:
                  $(tds[i])
                    .children("button")
                    .data("set_num", adjusted_set_number);
                  break;
              }
            }

            adjusted_set_number++;
          }
        });
    }

    // Let local storage be current contents of form
    set_local_storage();
  });
});

function delete_exercise(ex_num) {
  console.log(`Deleting exercise ${ex_num}...`);
  $(`ul#exercises>li#exercise_${ex_num}`).remove();
}

// // On .add_exercise_button click
// $(document).ready(() => {
// 	$(document).on("click", ".add_exercise_button", function () {
// 		let ex_num = $("ul#exercises>li").length;

// 		// Append new exercise to exericses list
// 		let html = $(`ul#exercises>li`)
// 			.first()
// 			.clone()
// 			.prop("hidden", false)
// 			.prop("outerHTML")
// 			.replaceAll("?ex_num?", ex_num);
// 		$(`ul#exercises`).append(html);

// 		// Adds "required" attribute to non-hidden, number inputs
// 		add_required_attribute();

// 		// Let local storage be current contents of form
// 		set_local_storage();
// 	});
// });

// On form clear
$(document).ready(() => {
  $(document).on("click", ".form_clear_button", function () {
    localStorage.clear();
    location.reload(); // Refresh page to take effect
  });
});

// On form submit
$(document).ready(() => {
  // On form submit, clear local storage
  $(document).on("submit", "#add_workout_form", function (event) {
    let num_exercises = $(`ul#exercises>li`).length - 1;
    console.log("num exercises", num_exercises);
    if (num_exercises <= 0) {
      $(`#alerts`).html(
        generateAlert(
          "warning",
          "Please add at least one exercise",
          "#664d03"
        )
      );
      event.preventDefault();
      return;
    }

    localStorage.clear();
    console.log("Redirected to success page...");
  });
});
// $(document).on("submit", "#bodyweight_chart_form", function (event) {
// 	//if (!isNaN($(this).val()) && Number.isInteger(parseFloat($(this).val())) && $(this).val() !== "") {
// 	// <!-- ? all cases work ? -->
// 	console.log("Handling update...");
// 	handleBodyweightChartUpdate($("#bodyweight_input").val());

// 	event.preventDefault();
// });

// * jQuery used for Add Exercise Modal

function oldtitleCase(str) {
  return str
    .toLowerCase()
    .split(" ")
    .map(function (word) {
      return word.charAt(0).toUpperCase() + word.slice(1);
    })
    .join(" ");
}
function titleCase(str) {
  let spaceCapitalized = str
    .toLowerCase()
    .split(" ")
    .map(function (word) {
      return word.charAt(0).toUpperCase() + word.slice(1);
    })
    .join(" ");
  let hyphenCapitalized = spaceCapitalized
    .split("-")
    .map(function (word) {
      return word.charAt(0).toUpperCase() + word.slice(1);
    })
    .join("-");
  let parenCapitalized = hyphenCapitalized
    .split("(")
    .map(function (word) {
      return word.charAt(0).toUpperCase() + word.slice(1);
    })
    .join("(");
  return parenCapitalized;
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
    if (main_group === "All" || main_group === "") {
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
    console.log("MAIN GROUP", main_group);

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
    let selected_equip_name = $(
      'input[name="equipment_list_radios"]:checked'
    ).data("equipment_name");
    console.log("selected equip", selected_equip_name);

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

    // // ! Mistake line
    // let ex_num = 100;

    let ex_num = 1;
    if (parseInt($("ul#exercises>li").length) > 1) {
      ex_num =
        parseInt(
          $("ul#exercises>li:last-child").attr("id").split("_")[1]
        ) + 1;
      console.log(
        "Last child id= " + $("ul#exercises>li:last-child").attr("id")
      );
    }
    console.log("************* new ex num = " + ex_num);

    // if ($("ul#exercises>li").length > 1) {
    //   ex_num =
    //     parseInt($("ul#exercises>li").last().data("ex_num")) + 10;
    // }
    // console.log("EX NUM = " + ex_num);

    // Append new exercise to exericses list
    let html = $(`ul#exercises>li`)
      .first()
      .clone()
      .prop("hidden", false)
      .data("ex_num", ex_num)
      .prop("outerHTML")
      .replaceAll("?ex_num?", ex_num);
    $(`ul#exercises`).append(html);

    // Append correct .data() attribute
    // $(`ul#exercises`).last().data("ex_num", ex_num);

    // Adds "required" attribute to non-hidden, number inputs
    add_required_attribute();

    // Set values to be sent over form / displayed, and hide modal
    $(`#${ex_num}_equipment_name`).val(selected_equip_name);
    $(`#${ex_num}_equipment_name`).trigger("input");
    $(`#${ex_num}_equipment_name_header`).text(selected_equip_name);
    $(`#${ex_num}_equipment_name_header`).trigger("input");
    $("#equipment-modal").modal("hide");

    // Let local storage be current contents of form
    set_local_storage();

    console.log(
      `Selected ${selected_equip_name} for Exercise ${ex_num}`
    );
  });
});

// Disable select_equipment_button when not clickable
$(document).ready(() => {
  $(document).on(
    "change",
    'input[name="equipment_list_radios"]',
    function () {
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
$(document).on("focus", "#custom-equipment-input", function () {
  $("input[data-equipment_name='custom-equipment-placeholder']").prop(
    "checked",
    true
  );
  let custom_text = $(this).val();
  console.log("custom text", custom_text);
  if (custom_text !== "") {
    enableButton("select_equipment_button");
  }
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
  $(document).on("click", ".add_exercise_button", function () {
    $("#equipment-modal").modal("show");

    $(".badge").each(function () {
      $(this).css(
        "background",
        `#${intToRGB(hashCode($(this).html()))}55`
      );
    });

    // ! testing - not sure if it has worked yet
    // Fix case where #main_muscle_group_select shows as empty
    if ($("#main_muscle_group_select").val() === "") {
      // Set val to "All" for cases where its ""
      $("#main_muscle_group_select").val("All");
    }

    let selected_equip_name = $(this).data("equipment_name");
    if (selected_equip_name === undefined) {
      disableButton("select_equipment_button");
    }
  });
});

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

function generateAlert(type, message, color) {
  return `<div class="alert alert-${type} alert-dismissible fade show
    text-center px-0" id="successful_save" role="alert">
        <strong>${message}</strong>

        <button type="button" class="close transparent-background" data-bs-dismiss="alert" aria-label="Close" style="color: ${color};" id="add-workout-alert-close">
            <span aria-hidden="true">
                <i class="fa fa-times"></i>
            </span>
        </button>
    </div>`;
}

var submusc = {
  Biceps:
    "one of three muscles in the anterior compartment of the upper arm. The Biceps has two heads, the short head and the long head",
  Forearms:
    "the region of the upper limb between the elbow and the wrist. The forearm contains many muscles, including the flexors and extensors of the digits",
  Pecs: "the muscles that connect the front of the human chest with the bones of the upper arm and shoulder",
  Triceps:
    "a large muscle on the back of the upper limb of many vertebrates. It consists of 3 parts: the medial, lateral, and long head",
  Lats: "is a large, flat muscle on the back that stretches to the sides, behind the arm. The latissimus dorsi is the largest muscle in the upper body",
  Traps:
    "The trapezius has three functional parts: an upper (descending) part which supports the weight of the arm; a middle region (transverse), which retracts the scapula; and a lower (ascending) part which medially rotates and depresses the scapula",
  Abdominals:
    " a paired muscle running vertically on each side of the anterior wall of the human abdomen",
  Obliques:
    "group of muscles of the abdomen (belly) acting together forming a firm wall.The oblique muscles consist of external oblique muscle and internal oblique muscle",
  Quads:
    "a large muscle group that includes the four prevailing muscles on the front of the thigh: rectus femoris, vastus lateralis, vastus medialis , and the vistas intermedium muscle",
  Hamstrings:
    "any one of the three posterior thigh muscles in between the hip and the knee. From medial to lateral: semimembranosus, semitendinosus and biceps femoris",
  Glutes:
    "the main extensor muscle of the hip. It is the largest and outermost of the three gluteal muscles and makes up a large part of the shape and appearance of each side of the hips",
  Calves:
    "the back portion of the lower leg in human anatomy. The calf is composed of the muscles of the posterior compartment of the leg: The gastrocnemius/soleus and the tibialis posterior",
  Delts:
    "the muscle forming the rounded contour of the human shoulder.the deltoid muscle appears to be made up of three distinct sets of muscle fibers:  the anterior part, posterior part, and intermediate part",
};
$(document).ready(() => {
  $(document).on("mouseover", ".Badge", function () {
    let id = $(this).attr("id");
    description = submusc["id"];

    $(".Badge").popover({
      title: description,
      placement: "top",
    });
  });
});
