#!/usr/bin/env python

# ----------
# flask_database_methods.py
# Author: Ian Murray, Adam Gamba & Darren Zheng
# ----------

import json
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
)
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from flask.helpers import make_response
from database_methods import (
    create_session,
    create_local_session,
    get_all_custom_equipment,
    get_all_used_equipment,
    get_all_equipment,
    get_past_workout_by_id,
    get_past_workouts,
    get_equipment_data,
    create_new_workout,
    create_new_exercise,
    get_goal_bodyweight,
    get_preferred_name,
    create_new_bodyweight,
    get_bodyweight_data,
    get_weight_estimation,
    get_rep_estimation,
    equipment_in_database,
    create_custom_equipment,
    get_workout_title_by_id,
    update_profile_settings,
    has_agreed_to_liability,
    agree_to_liability,
    delete_workout_and_exercises,
    has_watched_tutorial,
    watch_tutorial,
    unwatch_tutorial,
    get_all_1rms,
    insert_1RM,
    delete_custom_equipment,
)

from casclient import CasClient
from format_chart_data import (
    format_rep_range_data,
    format_bodyweight_data,
)
import html
import os


# ! Production
# session, engine = create_session()

# ! Local testing
session, engine = create_local_session()

# Begin App

app = Flask(__name__, template_folder="./templates")
app.secret_key = os.environ["APP_SECRET_KEY"]
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql" + os.environ["DATABASE_URL"][8:]
)

# Helper function to map date_range string to date object
def get_earliest_date(date_range):
    if date_range == "1 Month":
        return datetime.today() - relativedelta(months=1)
    elif date_range == "3 Months":
        return datetime.today() - relativedelta(months=3)
    elif date_range == "6 Months":
        return datetime.today() - relativedelta(months=6)
    elif date_range == "12 Months":
        return datetime.today() - relativedelta(months=12)
    else:
        return datetime.min + timedelta(days=1)


# Runs before every request to redirect http to https (if not localhost)
@app.before_request
def https_only_heroku():
    if "localhost" not in request.url and not request.is_secure:
        print("Redirecting to HTTPS")
        url = request.url.replace("http://", "https://", 1)
        code = 301
        return redirect(url, code=code)


# Ajax function to agree to liability agreement
@app.route("/agree_liability")
def agree_liability():
    # Get parameters from GET request
    print("Handling agree_liability...")
    user_name = request.args.get("user_name")

    # Contact database
    success = agree_to_liability(session, user_name)
    print("successful agreement?", success)

    response = make_response(
        {
            "success": success,
        }
    )
    return response


# Ajax function to update that user has watched tutorial
@app.route("/watched_tutorial")
def watched_tutorial():
    # Get parameters from GET request
    print("Handling watched_tutorial...")
    user_name = request.args.get("user_name")

    # Contact database
    success = watch_tutorial(session, user_name)
    print("successful watch tutorial?", success)

    response = make_response(
        {
            "success": success,
        }
    )
    return response


# Ajax function to update that user wants to unwatch tutorial
@app.route("/unwatched_tutorial")
def unwatched_tutorial():
    # Get parameters from GET request
    print("Handling unwatched_tutorial...")
    user_name = request.args.get("user_name")

    # Contact database
    success = unwatch_tutorial(session, user_name)
    print("successful unwatch tutorial?", success)

    response = make_response(
        {
            "success": success,
        }
    )
    return response


# Index/landing page
@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def landing():
    # authentic = CasClient().is_authenticated() != None
    authentic = True
    print("is authentic?", authentic)
    return render_template("tigerfit.html", is_authenticated=authentic)


# About us page
@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


# History page
@app.route("/history", methods=["GET", "POST"])
def history():
    user_name = CasClient().authenticate(session).strip()
    has_agreed_liability = has_agreed_to_liability(session, user_name)

    past_workouts = get_past_workouts(session, user_name)
    print("past_workouts: ", len(past_workouts))

    workouts = []
    length = len(past_workouts)
    if length == 0:
        return render_template(
            "workout_history.html",
            past_workouts=workouts,
            user_name=user_name,
            has_agreed_liability=has_agreed_liability,
        )
    curr_exercise_list = []
    for i in range(length):
        past_workouts[i] = dict(past_workouts[i])
        curr_workout = past_workouts[i]["UserWorkouts"].to_dict()
        curr_id = curr_workout["id"]
        exercise = past_workouts[i]["UserExercises"].to_dict()
        curr_exercise_list.append(exercise)
        if i == (length - 1):  # at the end of the workout list
            workouts.append(
                {
                    "workoutinfo": curr_workout,
                    "exerciseinfo": curr_exercise_list,
                }
            )
            return render_template(
                "workout_history.html",
                past_workouts=workouts,
                user_name=user_name,
                has_agreed_liability=has_agreed_liability,
            )
        next_id = dict(past_workouts[i + 1])["UserWorkouts"].to_dict()[
            "id"
        ]
        if curr_id != next_id:
            workouts.append(
                {
                    "workoutinfo": curr_workout,
                    "exerciseinfo": curr_exercise_list,
                }
            )
            curr_exercise_list = []


# Ajax function for deleting workout from history
@app.route("/delete_workout")
def delete_workout():
    # Get parameters from GET request
    print("Handling delete_workout...")
    user_name = request.args.get("user_name")
    workout_id = int(request.args.get("workout_id"))

    # Contact database
    success = delete_workout_and_exercises(
        session, user_name, workout_id
    )
    print("successful deletion?", success)

    response = make_response(
        {
            "success": success,
        }
    )
    return response


# Data analytics page
@app.route("/data", methods=["GET", "POST"])
def data():
    print("GET request for /index")

    user_name = CasClient().authenticate(session).strip()
    has_agreed_liability = has_agreed_to_liability(session, user_name)

    equipment_list = list(
        map(lambda row: row.__dict__, get_all_equipment(session))
    )
    equipment_list = sorted(
        equipment_list, key=lambda x: x["equipment_name"]
    )
    custom_equipment_list = get_all_custom_equipment(session, user_name)
    custom_equipment_list = [
        html.escape(customex) for customex in custom_equipment_list
    ]
    used_equipment_list = get_all_used_equipment(session, user_name)
    if len(used_equipment_list) > 0:
        first_used_equipment = used_equipment_list[0]
    else:
        first_used_equipment = ""
    print("*first used equip", first_used_equipment)

    return render_template(
        "data.html",
        user_name=user_name,
        equipment_list=equipment_list,
        custom_equipment_list=custom_equipment_list,
        used_equipment_list=used_equipment_list,
        first_used_equipment=html.escape(first_used_equipment),
        is_add_workout_page=False,
        has_agreed_liability=has_agreed_liability,
    )


# Ajax function for /data equipment manager table
@app.route("/equipment_manager", methods=["POST"])
def equipment_manager():
    print("Handling /equipment_manager...")
    all_equip = get_all_equipment(session)
    user_name = request.json["user_name"]
    custom_equip = get_all_custom_equipment(session, user_name)
    one_rms = get_all_1rms(session, user_name)

    data = []
    for row in all_equip:
        row = row.__dict__
        # print("entry:", row)
        name = row["equipment_name"]
        one_rm = one_rms[name] if name in one_rms else 0
        main = row["main_muscle_group"]
        sub = sorted(row["sub_muscle_groups"]["tags"])
        sub = ", ".join(sub)

        data.append(
            {
                "name": name,
                "1rm": round(one_rm, 1),
                "main_group": main,
                "sub_groups": sub,
                "is_custom": False,  # False
            }
        )

    for name in custom_equip:
        one_rm = one_rms[name] if name in one_rms else 0
        # main = row["main_muscle_group"]
        # sub = row["sub_muscle_groups"]["tags"]
        # sub = ", ".join(sub)

        data.append(
            {
                "name": name,
                "1rm": round(one_rm, 1),
                "main_group": "",
                "sub_groups": "",
                "is_custom": True,  # True
            }
        )

    # print("***ALL", all_equip)
    data = sorted(data, key=lambda x: x["name"])

    return {"data": data}


# def sort_equipment_by_name


# Ajax function for /data/equipment_manager update 1rm
@app.route("/update_1rm", methods=["POST"])
def update_1rm():
    user_name = request.args.get("user_name")
    equipment_name = request.args.get("equipment_name")
    new_1rm = float(request.args.get("new_1rm"))

    print("new 1rm", new_1rm)

    insert_1RM(session, user_name, equipment_name, new_1rm)

    response = make_response(
        {
            "success": True,
        }
    )
    return response


# Ajax function for /data/equipment_manager delete custom equipment
@app.route("/delete_custom", methods=["POST"])
def delete_custom():
    user_name = request.args.get("user_name")
    equipment_name = request.args.get("equipment_name")

    delete_custom_equipment(session, equipment_name, user_name)

    response = make_response(
        {
            "success": True,
        }
    )
    return response


# Ajax function for /data bodyweight chart
@app.route("/update_bodyweight_chart", methods=["GET"])
def update_bodyweight_chart():
    # Get parameters from GET request
    print("Handling update_bodyweight_chart...")
    user_name = request.args.get("user_name")
    bodyweight = request.args.get("bodyweight")

    print("GET request for /update_bodyweight_chart")
    print("*bodyweight", bodyweight)
    if bodyweight == "null":
        goal_bodyweight = get_goal_bodyweight(session, user_name)

        bodyweight_history = get_bodyweight_data(session, user_name)
        if bodyweight_history == []:
            response = make_response(
                {
                    "is_empty": True,
                }
            )
            return response

        (
            bodyweight_data,
            change,
            good_change,
        ) = format_bodyweight_data(bodyweight_history, goal_bodyweight)
        # print("***bodyweight data", bodyweight_data)
        response = make_response(
            {
                "bodyweight_data": bodyweight_data,
                "change": change,
                "good_change": good_change,
                "is_empty": False,
            }
        )
        return response

    bodyweight = float(bodyweight)

    # Retrieves goal bodyweight from DB (for horizontal line)
    goal_bodyweight = get_goal_bodyweight(session, user_name)

    # If user inputted a bodyweight, add new bodyweight to database
    create_new_bodyweight(session, user_name, bodyweight, date.today())

    # Formats data for chart.js plot
    bodyweight_history = get_bodyweight_data(session, user_name)
    (
        bodyweight_data,
        change,
        good_change,
    ) = format_bodyweight_data(bodyweight_history, goal_bodyweight)
    # print("***bodyweight data", bodyweight_data)
    response = make_response(
        {
            "bodyweight_data": bodyweight_data,
            "change": change,
            "good_change": good_change,
        }
    )
    return response


# Ajax function for /data equipment data chart
@app.route("/update_equipment_chart", methods=["GET"])
def update_equipment_chart():
    # Get parameters from GET request
    print("Handling update_equipment_chart...")
    user_name = request.args.get("user_name")
    equipment_name = request.args.get("equipment_name")
    date_range = request.args.get("date_range")
    start_date = get_earliest_date(date_range)

    print("GET request for /update_equipment_chart")

    equip_history = get_equipment_data(
        session, user_name, equipment_name, start_date
    )

    # Formats data for chart.js plot
    rep_range_data = format_rep_range_data(equip_history)

    response = make_response(
        {
            "rep_range_data": rep_range_data,
            "data": {
                "equipment_name": equipment_name,
                "date_range": date_range,
            },
        }
    )
    return response


# Activated when user accesses /add page
@app.route("/add", methods=["GET"])
def add():
    user_name = CasClient().authenticate(session).strip()
    has_agreed_liability = has_agreed_to_liability(session, user_name)
    has_watched = has_watched_tutorial(session, user_name)
    # print("*has watched tutorial?", has_watched)
    # print("*has agreed liability?", has_agreed_liability)

    # * Handle case for copying workout from existing id
    copying_past_workout = False
    past_workout = {}
    if "id" in request.args:
        copying_past_workout = True
        copy_id = request.args.get("id")

        # Contact database
        past_workout = get_past_workout_by_id(
            session, user_name, copy_id
        )

        if past_workout == False:
            print("no past workout")
            copying_past_workout = False
        # print(
        #     "title = ",
        #     get_workout_title_by_id(session, user_name, copy_id),
        # )
        print("past workout: ", past_workout)
        # for set in past_workout:
        #     print(set)
        #     print(set["sets"])

    # @app.route("/copy_workout", methods=["GET"])
    # def copy_workout():
    #     # Get parameters from GET request
    #     print("Handling copy_workout...")
    #     user_name = request.args.get("user_name")
    #     workout_id = int(request.args.get("workout_id"))

    #     # Contact database
    #     workout = get_past_workout_by_id(session, user_name, workout_id)
    #     print("**** * * * * retrieved workout:", workout)

    #     return add()
    #     # return response

    # * END

    pref_name = get_preferred_name(session, user_name)

    # retrieve equipment data from database
    equipment_list = list(
        map(lambda row: row.__dict__, get_all_equipment(session))
    )
    equipment_list = sorted(
        equipment_list, key=lambda x: x["equipment_name"]
    )

    custom_equipment_list = sorted(
        get_all_custom_equipment(session, user_name)
    )

    if copying_past_workout:
        return render_template(
            "add_workout.html",
            equipment_list=equipment_list,
            custom_equipment_list=custom_equipment_list,
            user_name=user_name,
            pref_name=pref_name,
            is_add_workout_page=True,
            has_agreed_liability=has_agreed_liability,
            has_watched_tutorial=has_watched,
            copying_past_workout=copying_past_workout,
            past_workout=past_workout,
        )
    else:
        return render_template(
            "add_workout.html",
            equipment_list=equipment_list,
            custom_equipment_list=custom_equipment_list,
            user_name=user_name,
            pref_name=pref_name,
            is_add_workout_page=True,
            has_agreed_liability=has_agreed_liability,
            has_watched_tutorial=has_watched,
            copying_past_workout=copying_past_workout,
        )


# Activated when user submits workout via /add page
@app.route("/add", methods=["POST"])
def add_workout():

    user_name = CasClient().authenticate(session).strip()

    form = request.form.to_dict(flat=False)

    # new workout id that is created
    # workoutid needs to be connected to a certain complete workout
    workout_title = form["title"][0]
    workout_date = form["date"][0]
    workout_start_time = form["start_time"][0]
    workout_end_time = datetime.now().strftime("%H:%M")

    # Default start time is 1 hour before end
    if workout_start_time == "":
        workout_start_time = (
            datetime.now() - timedelta(hours=1)
        ).strftime("%H:%M")

    # Finds minutes diff between two strings of format xx:xx (%H:%M)
    def find_minutes_difference(start, end):
        hours = int(end[0:2]) - int(start[0:2])
        if hours > 12:
            hours = 24 - hours
        print("hours", hours)
        minutes = int(end[3:5]) - int(start[3:5])
        print("minutes", minutes)

        if minutes >= 0:
            diff = hours * 60 + minutes
            if diff < 0:
                return 0
            else:
                return diff
        else:
            diff = (hours - 1) * 60 + (minutes + 60)
            if diff < 0:
                return 0
            else:
                return diff

    workout_time_minutes = find_minutes_difference(
        workout_start_time, workout_end_time
    )
    # print("Total minutes", workout_time_minutes)

    if workout_date == "":
        FORMAT_STRING = "%Y-%m-%d"
        workout_date = datetime.today().strftime(FORMAT_STRING)

    if workout_title.strip() is None or workout_title.strip() == "":
        workout_title = workout_date + " Workout"

    workout_id = create_new_workout(
        session,
        user_name,
        workout_date,
        workout_title,
        minutes_taken=workout_time_minutes,
    )
    print("New workout ID", workout_id)

    num_sets = 0
    num_reps_list = []
    weights_list = []
    failed_list = []
    weight_volume = 0
    total_reps = 0

    # Trim 1RMs by only taking the MAXIMUM per equipment
    trimmed_1RMs = {}

    def dot_product(a, b):
        assert len(a) == len(b)
        res = 0
        for i in range(len(a)):
            res += a[i] * b[i]
        return res

    # Arbitrary limits
    MAX_EXERCISES = 100
    MAX_SETS = 100

    # Structure of example request
    # {'title': ['fail 3'], 'date': ['2023-01-09'], 'start_time': [''], '?ex_num?_equipment_name': [''], '?ex_num?_?set_num?_reps': [''], '?ex_num?_?set_num?_weight': [''], '?ex_num?_1_reps': [''], '?ex_num?_1_weight': [''], 'exercise_?ex_num?_notes': [''], '1_equipment_name': ['Back Squat'], '1_?set_num?_reps': [''], '1_?set_num?_weight': [''], '1_1_reps': ['1'], '1_1_weight': ['1'], '1_2_reps': ['1'], '1_2_weight': ['1'], '1_3_reps': ['1'], '1_3_weight': ['1'], '1_3_failed': ['on'], '1_4_reps': ['1'], '1_4_weight': ['1'], 'exercise_1_notes': ['']}
    for ex in range(1, MAX_EXERCISES):
        # If equipment name in form, reps/weight must be as well
        if f"{ex}_equipment_name" in form:
            # Find equipment name
            equipment_name = form[f"{ex}_equipment_name"][0].title()

            # Find notes (if exists)
            if f"exercise_{ex}_notes" in form:
                notes = form[f"exercise_{ex}_notes"][0]
        else:
            continue

        for set in range(1, MAX_SETS):
            if f"{ex}_{set}_reps" not in form:
                break

            # Append reps
            reps_str = form[f"{ex}_{set}_reps"][0]
            if "." in reps_str:
                num_reps_list.append(int(reps_str.split(".")[0]))
            else:
                num_reps_list.append(int(reps_str))

            # Append weight
            weights_list.append(float(form[f"{ex}_{set}_weight"][0]))

            # Append failed (if exists)
            if f"{ex}_{set}_failed" in form:
                failed_list.append(True)
            else:
                failed_list.append(False)

            num_sets += 1

        # Done parsing sets for this exercise
        sets = {
            "num_sets": num_sets,
            "num_reps": num_reps_list,
            "weight": weights_list,
            "failed": failed_list,
            "was_pr": [],
        }
        weight_volume += dot_product(num_reps_list, weights_list)
        total_reps += sum(num_reps_list)

        num_sets = 0
        num_reps_list = []
        weights_list = []
        failed_list = []

        if not equipment_in_database(
            session, equipment_name, user_name
        ):
            create_custom_equipment(session, equipment_name, user_name)

        _, new_1RMs = create_new_exercise(
            session,
            user_name,
            workout_id,
            equipment_name,
            sets,
            notes,
        )

        # 1 or more new 1RMs added
        if len(new_1RMs) > 0:
            # Dict Format: {"equipment_name": "x",
            # "one_rep_estimation": 1.0}
            for dict in new_1RMs:
                dict_equip_name = dict["equipment_name"]
                dict_estimation = dict["one_rep_estimation"]
                if dict_equip_name in trimmed_1RMs:
                    if dict_estimation > trimmed_1RMs[dict_equip_name]:
                        trimmed_1RMs[dict_equip_name] = dict_estimation
                else:
                    trimmed_1RMs[dict_equip_name] = dict_estimation

    # * Calculate unique 1RMs

    # Format: [{"equipment_name": "x",
    # "one_rep_estimation": 1.0}]
    all_new_1RMs = []

    for k in trimmed_1RMs:
        all_new_1RMs.append(
            {
                "equipment_name": k,
                "one_rep_estimation": round(trimmed_1RMs[k], 1),
            }
        )
    print("***result", all_new_1RMs)

    # * Calculate some workout summary stats
    volume_per_minute = 0
    reps_per_minute = 0
    if workout_time_minutes > 0:
        volume_per_minute = round(
            weight_volume / workout_time_minutes, 1
        )
        reps_per_minute = round(total_reps / workout_time_minutes, 1)

    return render_template(
        "add_workout_success.html",
        workout_title=workout_title,
        workout_date=workout_date,
        weight_volume=weight_volume,
        all_new_1RMs=all_new_1RMs,
        workout_time_minutes=workout_time_minutes,
        volume_per_minute=volume_per_minute,
        reps_per_minute=reps_per_minute,
    )


# Ajax function to recommend weight for /add page
@app.route("/recommend_weight", methods=["GET"])
def recommend_weight():
    # Get parameters from GET request
    print("Handling recommend_weight...")
    user_name = request.args.get("user_name")
    equipment_name = request.args.get("equipment_name")
    print("***********equip name = ", equipment_name)
    reps = int(request.args.get("reps"))
    element_name = request.args.get("element_name")

    # Contact database
    weight_recommendation = get_weight_estimation(
        session, user_name, equipment_name, reps
    )

    response = make_response(
        {
            "element_name": element_name,
            "weight_recommendation": weight_recommendation,
        }
    )
    return response


# Ajax function to recommend reps for /add page
@app.route("/recommend_reps", methods=["GET"])
def recommend_reps():
    # Get parameters from GET request
    print("Handling recommend_reps...")
    user_name = request.args.get("user_name")
    equipment_name = request.args.get("equipment_name")
    weight = float(request.args.get("weight"))
    element_name = request.args.get("element_name")

    # Contact database
    reps_recommendation = get_rep_estimation(
        session, user_name, equipment_name, weight
    )

    response = make_response(
        {
            "element_name": element_name,
            "reps_recommendation": reps_recommendation,
        }
    )
    return response


@app.route("/fitness", methods=["GET"])
def graph():
    user_name = CasClient().authenticate(session).strip()
    has_agreed_liability = has_agreed_to_liability(session, user_name)
    # retrieve equipment data from database

    return render_template(
        "body_graph.html",
        user_name=user_name,
        has_agreed_liability=has_agreed_liability,
    )


# Ajax function for /fitness
@app.route("/exerciseresults", methods=["GET"])
def results():
    equipment_list = list(
        map(lambda row: row.__dict__, get_all_equipment(session))
    )

    main = request.args.get("main")
    sub = request.args.get("sub")

    # if sub is not none or "select a submuscle group" then i want to

    html = '<table class="table table-dark"><tbody><tr>'
    for equip in equipment_list:
        if sub == "Select Sub-Muscle Group":
            if equip["main_muscle_group"] == main:
                html += (
                    '<tr><td style="padding: 12px;"> <button type="button"\
                    style="color: orange; background-color: transparent; border: none; width: 100%;" id="more_ex_info_button"\
                    data-toggle="modal data-target="#more-ex-info-modal">'
                    + equip["equipment_name"]
                    + '</button><div class="data-mule" data-equipment_name="'
                    + equip["equipment_name"]
                    + '"data-gif_path="'
                    + equip["gif_path"]
                    + '"data-equipment_description="'
                    + equip["equipment_description"]
                    + '"></div>'
                    + "</td></tr>"
                )
        elif sub in equip["sub_muscle_groups"]["tags"]:
            html += (
                '<tr><td style="padding: 12px;"> <button type="button"\
                    style="color: orange; background-color: transparent;border: none; width: 100%;" id="more_ex_info_button"\
                    data-toggle="modal data-target="#more-ex-info-modal"><center>'
                + equip["equipment_name"]
                + '</button><div class="data-mule" data-equipment_name="'
                + equip["equipment_name"]
                + '"data-gif_path="'
                + equip["gif_path"]
                + '"data-equipment_description="'
                + equip["equipment_description"]
                + '"></div>'
                + "</td></tr>"
            )

    html += "</tbody></table>"
    response = make_response(html)

    return response


# Profile page
@app.route("/profile", methods=["GET", "POST"])
def profile():
    user_name = CasClient().authenticate(session).strip()
    has_agreed_liability = has_agreed_to_liability(session, user_name)

    if request.method == "POST":
        form = request.form.to_dict(flat=True)

        # check that form fields are populated
        print("FORM is", form)
        pref_name = form.get("pref_name", "")
        goal_bw = form.get("goal_weight", "")
        print("pref name", pref_name)
        print("goal_bw", goal_bw)

        update_profile_settings(session, user_name, pref_name, goal_bw)

        new_pref_name = get_preferred_name(session, user_name)
        new_goal_bw = get_goal_bodyweight(session, user_name)

        print("Handled profile update...")
        # print(f"Is updated: {is_updated}")
        return render_template(
            "profile_page.html",
            is_updated=True,
            pref_name=new_pref_name,
            goal_bodyweight=new_goal_bw,
            user_name=user_name,
            has_agreed_liability=has_agreed_liability,
        )
    else:
        pref_name = get_preferred_name(session, user_name)
        goal_bw = get_goal_bodyweight(session, user_name)

        print("GET request for \profile")
        return render_template(
            "profile_page.html",
            is_updated=False,
            pref_name=pref_name,
            goal_bodyweight=goal_bw,
            user_name=user_name,
            has_agreed_liability=has_agreed_liability,
        )


# CAS function to login user
@app.route("/login", methods=["GET"])
def login():
    cas_client = CasClient()
    cas_client.authenticate(session)
    cas_client.login("index")


# CAS function to logout user
@app.route("/logout", methods=["GET"])
def logout():
    cas_client = CasClient()
    cas_client.authenticate(session)
    cas_client.logout("index")


# Displays error page for all errors
@app.errorhandler(Exception)
def internal_server_error(e):  # need this e to work
    print("Displaying error page...")
    print("Error msg", e)
    if "localhost" not in request.url:
        return render_template("error.html")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


# ? needed
# @app.route("/qr", methods=["GET", "POST"])
# def test_qr_codes():
#     print("testing qrs")
#     # return render_template("test-qrcodes.html")
#     return render_template("other_qr_scripts.html")


if __name__ == "__main__":
    # Run App
    # debug option reloads server on save
    app.run(
        host="localhost", port="5000", debug=True
    )  # , ssl_context="adhoc")
