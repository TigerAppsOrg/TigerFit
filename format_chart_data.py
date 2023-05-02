# Returns object (twp datasets)
from sqlalchemy.sql.expression import true


def format_bodyweight_data(bodyweight_history, goal_bodyweight):
    # if bodyweight_history == []:
    #     # return []
    #     bodyweight_data = {
    #         "bw_dataset": [],
    #         "goal_dataset": [],
    #     }
    #     return bodyweight_data, 0, true

    # Formatting string to be in a readable format by chart.js
    FORMAT_STRING = "%Y-%m-%d"
    bw_dataset = []
    goal_dataset = []

    # For each bodyweight in database response
    for bw in bodyweight_history:
        weight = bw[1]
        date = bw[2].strftime(FORMAT_STRING)
        bw_dataset.append({"x": date, "y": weight})
        # Horizontal Line
        goal_dataset.append({"x": date, "y": goal_bodyweight})

    # Find change from 2nd most recent bodyweight to most recent
    bw_length = len(bw_dataset)
    if bw_length > 1:
        change = (
            bw_dataset[bw_length - 1]["y"]
            - bw_dataset[bw_length - 2]["y"]
        )
        # round to tenth
        change = round(10 * change) / 10
    else:
        change = 0

    most_recent_bodyweight = bw_dataset[bw_length - 1]["y"]
    good_change = False

    # Determines if change is a good_change (towards the goal bw direction)
    if most_recent_bodyweight > goal_bodyweight and change <= 0:
        good_change = True
    if most_recent_bodyweight < goal_bodyweight and change >= 0:
        good_change = True

    bodyweight_data = {
        "bw_dataset": bw_dataset,
        "goal_dataset": goal_dataset,
    }
    return bodyweight_data, change, good_change


# Returns object (multiple datasets)
def format_rep_range_data(equip_history):
    # If no data return immediately
    if equip_history == []:
        return {}

    # Formatting string to be in a readable format by chart.js
    FORMAT_STRING = "%Y-%m-%d"
    # rep_range_1 = []
    rep_range_1_6 = []
    rep_range_7_12 = []
    rep_range_13_plus = []

    # rep_range_1_avgs = []
    rep_range_1_6_avgs = []
    rep_range_7_12_avgs = []
    rep_range_13_plus_avgs = []

    # rep_range_1_failed = []
    rep_range_1_6_failed = []
    rep_range_7_12_failed = []
    rep_range_13_plus_failed = []

    # rep_range_1_num_reps = []
    rep_range_1_6_num_reps = []
    rep_range_7_12_num_reps = []
    rep_range_13_plus_num_reps = []

    # For each workout in database response
    for workout in equip_history:
        date = workout[1].date.strftime(FORMAT_STRING)
        sets = workout[2].sets
        num_sets = sets["num_sets"]

        # weights_1 = []
        weights_1_6 = []
        weights_7_12 = []
        weights_13_plus = []

        for i in range(num_sets):
            num_reps = sets["num_reps"][i]
            weight = sets["weight"][i]
            failed = sets["failed"][i]

            # Separate data into 4 groups based on selected rep ranges
            # Rep ranges: 1, 2-6, 7-12, 13+
            # if num_reps == 1:
            #     # x-y coordinates to be graphed
            #     rep_range_1.append({"x": date, "y": weight})
            #     # python T/F not defined in JS
            #     rep_range_1_failed.append(1 if failed else 0)
            #     rep_range_1_num_reps.append(num_reps)
            #     # weights used to calculate averages for each day
            #     if not failed:
            #         weights_1.append(weight)
            if num_reps <= 6:
                rep_range_1_6.append({"x": date, "y": weight})
                rep_range_1_6_failed.append(1 if failed else 0)
                rep_range_1_6_num_reps.append(num_reps)
                if not failed:
                    weights_1_6.append(weight)
            elif num_reps <= 12:
                rep_range_7_12.append({"x": date, "y": weight})
                rep_range_7_12_failed.append(1 if failed else 0)
                rep_range_7_12_num_reps.append(num_reps)
                if not failed:
                    weights_7_12.append(weight)
            else:
                rep_range_13_plus.append({"x": date, "y": weight})
                rep_range_13_plus_failed.append(1 if failed else 0)
                rep_range_13_plus_num_reps.append(num_reps)
                if not failed:
                    weights_13_plus.append(weight)

        # Calculates average y-val of a given list and returns x-y coord
        def list_avg(arr):
            if len(arr) == 0:
                return 0
            avg = sum(arr) / len(arr)
            return {"x": date, "y": avg}

        # Calculate and append averages (for line plots)
        avg_obj = list_avg(weights_1_6)
        # if avg_obj != 0:
        #     rep_range_1_6_avgs.append(list_avg(weights_1))
        # avg_obj = list_avg(weights_2_6)
        if avg_obj != 0:
            rep_range_1_6_avgs.append(list_avg(weights_1_6))
        avg_obj = list_avg(weights_7_12)
        if avg_obj != 0:
            rep_range_7_12_avgs.append(list_avg(weights_7_12))
        avg_obj = list_avg(weights_13_plus)
        if avg_obj != 0:
            rep_range_13_plus_avgs.append(list_avg(weights_13_plus))

    rep_range_data = {
        # "rep_range_1": rep_range_1,
        "rep_range_1_6": rep_range_1_6,
        "rep_range_7_12": rep_range_7_12,
        "rep_range_13_plus": rep_range_13_plus,
        # "rep_range_1_avgs": rep_range_1_avgs,
        "rep_range_1_6_avgs": rep_range_1_6_avgs,
        "rep_range_7_12_avgs": rep_range_7_12_avgs,
        "rep_range_13_plus_avgs": rep_range_13_plus_avgs,
        # "rep_range_1_failed": rep_range_1_failed,
        "rep_range_1_6_failed": rep_range_1_6_failed,
        "rep_range_7_12_failed": rep_range_7_12_failed,
        "rep_range_13_plus_failed": rep_range_13_plus_failed,
        # "rep_range_1_num_reps": rep_range_1_num_reps,
        "rep_range_1_6_num_reps": rep_range_1_6_num_reps,
        "rep_range_7_12_num_reps": rep_range_7_12_num_reps,
        "rep_range_13_plus_num_reps": rep_range_13_plus_num_reps,
    }

    return rep_range_data
