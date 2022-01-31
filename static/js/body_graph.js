function resetColor() {
$(".Chest").css("fill", "white");
$(".Arms").css("fill", "white");
$(".Shoulders").css("fill", "white");
$(".Back").css("fill", "white");
$(".Legs").css("fill", "white");
$(".Core").css("fill", "white");
}

var muscle_groups = {
"Core": ["Abdominals", "Obliques"],
"Chest": ["Pecs"],
"Back": ["Lats", "Traps", "Lower Back"],
"Arms": ["Biceps", "Triceps", "Forearms"],
"Legs": ["Quads", "Hamstrings", "Glutes","Calves"],
"Shoulders": ["Delts"]
}

$(document).ready(function () {
$(document).on('change', '#main_muscle_group_select', function () {
if ($(this).data('options') === undefined) {
// Array of all options
$(this).data('options', $('#datalist_options option').clone());
}
$("#sub_muscle_group_select").css("display", "inline")
// $("#sub_muscle").not('first').empty();
$("#sub_muscle_group_select").find('option').not(':first').remove();

let main_group = $(this).val();

resetColor()
$("." + main_group).css("fill", "pink");

var selected_sub = muscle_groups[main_group]

Array.from(selected_sub).forEach(function (sub) {
let option = new Option(sub, sub)
$("#sub_muscle_group_select").append(option)
})

let options = $(this)
.data("options")
.filter("[data-main_group=" + main_group + "]");

$("#datalist_options").html(options);

});


$(document).on('change', '#sub_muscle_group_select', function () {
let sub_group = $(this).val();

if (sub_group != "Select Sub-Muscle Group") {

if(sub_group=="Lower Back"){
sub_group="Lower_Back"
console.log("This is the lower back")
}

resetColor()
$("#" + sub_group).css("fill", "pink");
}
else {
main_group = $("#main_muscle_group_select").val()
$("." + main_group).css("fill", "pink");
}
});
});



$(document).ready(() => {
$(document).on("click", "#more_ex_info_button", function () {
// retrieve data from data container div element
let data_mule = $(this).siblings(".data-mule");

// set contents of each div dynamically
$("#more-ex-info-header").text(data_mule.attr("data-equipment_name"));
$("#more-ex-info-gif").attr("src", data_mule.attr("data-gif_path"));
$("#more-ex-info-body").text(data_mule.attr("data-equipment_description"));

// hide/show modal
$("#more-ex-info-modal").modal("toggle");
});

// Closes (toggles) the nested modal after clicking the "info" icon
$(document).on("click", "#close-modal-btn", function () {
// close outer modal on 'close button' click
$("#more-ex-info-modal").modal("toggle");

});
var currentcol=""
var currentid=""

// Arms
$(document).on("mouseover",".Back", function () {
currentcol=$(this).css( "fill" );
// close outer modal on 'close button' click
currentid= $(this).attr('id')
$("#"+currentid).css("fill", "red");
$("#"+currentid).popover({
placement: 'bottom',
trigger: 'hover'
}).popover("show");
});

$(document).on("mouseout", ".Back", function () {
// close outer modal on 'close button' click
$("#"+currentid).css("fill", currentcol);
});


$(document).on("mouseover",".Arms", function () {
currentcol=$(this).css( "fill" );
// close outer modal on 'close button' click
currentid= $(this).attr('id')
$("#"+currentid).css("fill", "red");
$("#"+currentid).popover({
placement: 'bottom',
trigger: 'hover'
}).popover("show");

});

$(document).on("mouseout", ".Arms", function () {
// close outer modal on 'close button' click
$("#"+currentid).css("fill", currentcol);
});

$(document).on("mouseover",".Core", function () {
currentcol=$(this).css( "fill" );
// close outer modal on 'close button' click
currentid= $(this).attr('id')
$("#"+currentid).css("fill", "red");
$("#"+currentid).popover({
placement: 'bottom',
trigger: 'hover'
}).popover("show");
});

$(document).on("mouseout", ".Core", function () {
// close outer modal on 'close button' click
$("#"+currentid).css("fill", currentcol);
});

$(document).on("mouseover",".Legs", function () {
currentcol=$(this).css( "fill" );
// close outer modal on 'close button' click
currentid= $(this).attr('id')
$("#"+currentid).css("fill", "red");
$("#"+currentid).popover({
placement: 'bottom',
trigger: 'hover'
}).popover("show");
});

$(document).on("mouseout", ".Legs", function () {
// close outer modal on 'close button' click
$("#"+currentid).css("fill", currentcol);
});
$(document).on("mouseover",".Chest", function () {
currentcol=$(this).css( "fill" );
// close outer modal on 'close button' click
currentid= $(this).attr('id')
$("#"+currentid).css("fill", "red");
$("#"+currentid).popover({
placement: 'bottom',
trigger: 'hover'
}).popover("show");
});

$(document).on("mouseout", ".Chest", function () {
// close outer modal on 'close button' click
$("#"+currentid).css("fill", currentcol);
});
$(document).on("mouseover",".Shoulders", function () {
currentcol=$(this).css( "fill" );
// close outer modal on 'close button' click
currentid= $(this).attr('id')
$("#"+currentid).css("fill", "red");
$("#"+currentid).popover({
placement: 'bottom',
trigger: 'hover'
}).popover("show");
});

$(document).on("mouseout", ".Shoulders", function () {
// close outer modal on 'close button' click
$("#"+currentid).css("fill", currentcol);
});


});
