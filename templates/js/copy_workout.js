$(document).ready(() => {
  // * Fill structure and save to localstorage
  let title = localStorage.getItem("workout_title") + " (clone)";
  $("#workout_title").val(title);
  localStorage.setItem("title", title);

  num_sets = JSON.parse(localStorage.getItem("num_sets"));
  reps = JSON.parse(localStorage.getItem("reps"));
  weights = JSON.parse(localStorage.getItem("weights"));

  for (let [i, equip_name] of Object.entries(
    JSON.parse(localStorage.getItem("equipment_names"))
  )) {
    i = parseInt(i);
    addExercise(equip_name);
    // console.log(parseInt(num_sets[i]) - 1);
    for (let j = 0; j < parseInt(num_sets[i]); j++) {
      if (j != parseInt(num_sets[i]) - 1) {
        $(".add_set_button").last().trigger("click");
      }

      // Populate reps in input AND localstorage
      let name = `${i + 1}_${j + 1}_reps`;
      let val = reps[i][j];
      $(`#${name}`).val(val);
      localStorage.setItem(name, val);

      // Populate weight in input AND localstorage
      name = `${i + 1}_${j + 1}_weight`;
      val = weights[i][j];
      $(`#${name}`).val(val);
      localStorage.setItem(name, val);
    }
    // // Populate trailing reps/weights input
    // let name = `${i + 1}_${parseInt(num_sets[i])}_reps`;
    // let val = reps[i][parseInt(num_sets[i]) - 1];
    // $(`#${name}`).val(val);
    // localStorage.setItem(name, val);

    // console.log(a);
    // console.log(b);
  }
  //   location.search = "";

  //   selected_equip_name = "Back Squat";
  //   addExercise(selected_equip_name);

  //   $(".add_set_button").last().trigger("click");
  //   $(".add_set_button").last().trigger("click");
  //   $(".add_set_button").last().trigger("click");
});

function addExercise(selected_equip_name) {
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

  // Fixes bug with deleting exercises in middle
  // Take LAST ex_num + 1 to be new ex_num
  let ex_num = 1;
  if (parseInt($("ul#exercises>li").length) > 1) {
    ex_num =
      parseInt(
        $("ul#exercises>li:last-child").attr("id").split("_")[1]
      ) + 1;
    //   console.log(
    // "Last child id= " + $("ul#exercises>li:last-child").attr("id")
    //   );
  }

  // Append new exercise to exericses list
  let html = $(`ul#exercises>li`)
    .first()
    .clone()
    .prop("hidden", false)
    .data("ex_num", ex_num)
    .prop("outerHTML")
    .replaceAll("?ex_num?", ex_num);
  $(`ul#exercises`).append(html);

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
}
