#!/usr/bin/env python

# ----------------------------------------------------------------------
# database_methods.py
# Author: Adam Gamba & Ian Murray
# ----------------------------------------------------------------------

from sys import argv, stderr, exit
from sqlalchemy import create_engine, desc, exc, func
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.expression import insert
import random
from database import (
    Base,
    Users,
    UserWorkouts,
    UserExercises,
    EquipmentList,
    UserBodyweights,
)
from datetime import datetime, date, timedelta

# from one_rep_estimation import OneRepEstimation
import json
import os


# ----------------------------------------------------------------------
# * CONSTRUCTOR METHODS

# Creates blank user with given field values (or default)
# Returns user_id of new user
# ! case sensitive rn
def create_new_user(session, user_name, age=0, goal_bodyweight=0):
    assert session is not None

    # zero one rep estimations (for all equipment)
    equipment_json = get_equipment_as_blank_json(session)

    # blank json object for custom equipment and used equipment
    custom_equipment = {"names": []}
    used_equipment = {"names": []}

    new = Users(
        user_name=user_name,
        pref_name=user_name,
        goal_bodyweight=goal_bodyweight,
        one_rep_estimation=equipment_json,
        custom_equipment=custom_equipment,
        used_equipment=used_equipment,
        has_agreed_liability=False,
        has_watched_tutorial=False,
    )
    session.add(new)
    try:
        session.commit()
        return new.user_name
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


# Creates blank workout with given field values (or default)
# Returns workout_id of new workout
def create_new_workout(
    session,
    user_name,
    workout_date=datetime.today(),
    workout_title=None,
    minutes_taken=60,
):
    assert session is not None
    FORMAT_STRING = "%Y-%m-%d"

    if workout_date == "":
        workout_date = datetime.today().strftime(FORMAT_STRING)

    if (
        workout_title is None
        or workout_title.strip() is None
        or workout_title.strip() == ""
    ):
        workout_title = str(workout_date) + " Workout"

    new = UserWorkouts(
        user_name=user_name,
        date=workout_date,
        workout_title=workout_title,
        minutes_taken=minutes_taken,
    )
    session.add(new)
    try:
        session.commit()
        return new.workout_id
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


# Creates blank exercise with given field values (or default)
# Returns exercise_id of new exercise
def create_new_exercise(
    session, user_name, workout_id, equipment_name, sets=None, notes=""
):
    # assert session is not None
    # assert workout_id > 0
    # assert equipment_name is not None

    # Add to used equipment list for specific user
    add_to_used_equipment(session, equipment_name, user_name)

    if sets is None:
        sets = {
            "num_sets": 0,
            "num_reps": [],
            "weight": [],
            "failed": [],
            "was_pr": [],
        }

    new_1RMs = []

    # Update one rep estimations based on newly inserted exercise
    for i in range(sets["num_sets"]):
        if not sets["failed"][i]:
            weight = sets["weight"][i]
            reps = sets["num_reps"][i]
            print("w,r", weight, reps)

            if is_bodyweight_exercise(session, equipment_name):
                one_rep_estimation = (
                    OneRepEstimation.bodyweight_estimate_one_rep_max(
                        session, user_name, weight, reps
                    )
                )
            else:
                one_rep_estimation = (
                    OneRepEstimation.estimate_one_rep_max(weight, reps)
                )

            new_1RM = insert_1RM_if_greater(
                session, user_name, equipment_name, one_rep_estimation
            )
            # New 1RM added
            print("NEW 1RM for %s = %d" % (equipment_name, new_1RM))
            if new_1RM >= 0:
                new_1RMs.append(
                    {
                        "equipment_name": equipment_name,
                        "one_rep_estimation": new_1RM,
                    }
                )
                sets["was_pr"].append(True)
            else:
                sets["was_pr"].append(False)

            print(
                "1RM estimation for %d weight and %d reps = %d"
                % (weight, reps, one_rep_estimation)
            )
        else:
            sets["was_pr"].append(False)

    new = UserExercises(
        workout_id=workout_id,
        equipment_name=equipment_name,
        sets=sets,
        notes=notes,
    )
    session.add(new)
    try:
        session.commit()
        return new.exercise_id, new_1RMs
    except exc.SQLAlchemyError as err:
        print("create_new_exercise() failed", err)
        session.rollback()
        return err


# Inserts 1RM for given user only if one_rep_estimation is greater than
# their previously saved 1RM
def insert_1RM_if_greater(
    session, user_name, equipment_name, one_rep_estimation
):

    previous_one_rep_dict = (
        session.query(Users.one_rep_estimation)
        .filter(Users.user_name == user_name)
        .one()[0]
    )
    previous_one_rep_estimation = previous_one_rep_dict[equipment_name]

    # New 1RM inserted
    if one_rep_estimation > previous_one_rep_estimation:
        result = insert_1RM(
            session, user_name, equipment_name, one_rep_estimation
        )
        return result
        # user = (
        #     session.query(Users)
        #     .filter(Users.user_name == user_name)
        #     .one()
        # )
        # new_dict = user.one_rep_estimation
        # new_dict[equipment_name] = one_rep_estimation
        # user.one_rep_estimation = new_dict

        # try:
        #     session.commit()
        #     return one_rep_estimation
        # except exc.SQLAlchemyError as err:
        #     session.rollback()
        #     return err
    # No 1RM inserted
    else:
        return -1


# Inserts 1RM for given user and given equipment
# Dangerous - Doesn't check if greater than previous
def insert_1RM(session, user_name, equipment_name, one_rep_estimation):
    user = (
        session.query(Users).filter(Users.user_name == user_name).one()
    )
    new_dict = user.one_rep_estimation
    new_dict[equipment_name] = one_rep_estimation
    user.one_rep_estimation = new_dict

    try:
        session.commit()
        return one_rep_estimation
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


# Resets 1RM for given user and given equipment to 0
# Dangerous - Doesn't check if greater than previous
def reset_1RM(session, user_name, equipment_name):
    result = insert_1RM(session, user_name, equipment_name, 0)
    return result


# Creates blank equipment with given field values (or default)
# Returns equipment_id of new equipment
def create_new_equipment(
    session,
    equipment_name,
    main_muscle_group,
    sub_muscle_groups=[],
    is_bodyweight=False,
):
    # ! ignore asserts for now
    # assert session is not None
    # assert equipment_name != ""
    # assert main_muscle_group != ""
    # assert isinstance(sub_muscle_groups, list)
    # assert isinstance(youtube_link, str)

    # If not yt link is provided, create yt search query as link
    # if youtube_link == "":
    #     youtube_link = (
    #         "https://www.youtube.com/results?search_query=%s"
    #         % quote(equipment_name)
    #     )

    # Sub_muscle_groups is JSON object with list of tags as only prop
    sub_muscle_groups = {"tags": sub_muscle_groups}

    new = EquipmentList(
        equipment_name=equipment_name,
        main_muscle_group=main_muscle_group,
        sub_muscle_groups=sub_muscle_groups,
        is_bodyweight=is_bodyweight
        # youtube_link=youtube_link,
    )
    session.add(new)
    try:
        session.commit()
        return new.equipment_name
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


# Creates blank bodyweight with given field values (or default).
# Only keeps track of most recent bodyweight for a given day
def create_new_bodyweight(
    session, user_name, bodyweight, date=date.today()
):
    # Deletes rows of today's date before adding newest entry
    query = session.query(UserBodyweights).filter(
        and_(
            UserBodyweights.date == date,
            UserBodyweights.user_name == user_name,
        )
    )
    if query.first() is not None:
        query.delete()

    new = UserBodyweights(
        user_name=user_name, bodyweight=bodyweight, date=date
    )
    session.add(new)
    session.commit()


# Adds a new set with given parameters to selected exercise
def add_new_set(session, exercise_id, num_reps, weight, failed):
    assert session is not None
    assert exercise_id > 0
    assert num_reps > 0, "Reps must be > 0"
    assert weight > 0, "Weight must be > 0"
    assert isinstance(failed, bool), "Failed must be boolean"

    exercise = (
        session.query(UserExercises)
        .filter(UserExercises.exercise_id == exercise_id)
        .one()
    )

    new_dict = exercise.sets
    # Number of sets currently in the selected exercise
    num_sets = new_dict["num_sets"]
    if num_sets == 0:
        assert len(new_dict["num_reps"]) == 0
        assert len(new_dict["weight"]) == 0
        assert len(new_dict["failed"]) == 0
        print("assert passed")

    new_dict["num_sets"] += 1
    new_dict["num_reps"].append(num_reps)
    new_dict["weight"].append(weight)
    new_dict["failed"].append(failed)
    try:
        session.commit()
        return exercise_id
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


def create_custom_equipment(session, equipment_name, user_name):
    assert session is not None

    # custom_equipment_list = (
    #     session.query(Users.custom_equipment)
    #     .filter(Users.user_name == user_name)
    #     .one()[0]["names"]
    # )
    user = (
        session.query(Users).filter(Users.user_name == user_name).one()
    )
    print("user", user)
    print("user dict", user.__dict__)

    # Append to custom_equipment in DB if not in list
    custom_equipment_list = user.custom_equipment["names"]
    print("old list", custom_equipment_list)

    if equipment_name not in custom_equipment_list:
        custom_equipment_list.append(equipment_name)
        user.custom_equipment["names"] = custom_equipment_list
        print("new list", custom_equipment_list)
        print(
            "new queried list",
            (
                session.query(Users.custom_equipment)
                .filter(Users.user_name == user_name)
                .one()[0]["names"]
            ),
        )

        print("* Appended to custom equip list")

    # ! STILL NEED TO ADD TO 1RMs JSON OBJ in users
    previous_one_rep_dict = (
        session.query(Users.one_rep_estimation)
        .filter(Users.user_name == user_name)
        .one()[0]
    )
    previous_one_rep_dict[equipment_name] = 0
    print("prev", previous_one_rep_dict)
    user.one_rep_estimation = previous_one_rep_dict
    print("* Created new 1RM")
    # !

    try:
        session.commit()
        return equipment_name
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


# Add to user-specific list of equipment they have used in the past
# Only adds if new equipment_name is unique in list
def add_to_used_equipment(session, equipment_name, user_name):
    assert session is not None

    user = (
        session.query(Users).filter(Users.user_name == user_name).one()
    )
    print("user", user)
    print("user dict", user.__dict__)

    # Append to used_equipment in DB if not in list
    used_equipment_list = user.used_equipment["names"]
    print("old list", used_equipment_list)

    if equipment_name not in used_equipment_list:
        used_equipment_list.append(equipment_name)
        user.used_equipment["names"] = used_equipment_list
    try:
        session.commit()
        return equipment_name
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


# Updates a user row with preferred name and their goal bodyweight
def update_profile_settings(
    session, user_name, pref_name, goal_bodyweight
):
    assert session is not None
    session_query = (
        session.query(Users)
        .filter(Users.user_name == user_name)
        .first()
    )
    if pref_name.strip() != "":
        session_query.pref_name = pref_name.strip()
    else:
        print("Pref name empty")
    if goal_bodyweight != "":
        session_query.goal_bodyweight = goal_bodyweight
    else:
        print("Goal bodyweight empty")

    try:
        session.commit()
        return True
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


# Populates the EquipmentList table with paths to their gifs
def populate_equipment_gifs(session):
    assert session is not None
    all_equipment = get_all_equipment(session)
    total_number_of_equipment = len(all_equipment)
    count = 0

    with open(
        r"./static/json/equipment_descriptions.json", encoding="utf-8"
    ) as json_file:
        equipment_description_dict = json.load(json_file)[0]
    print(f"Type: {type(equipment_description_dict)}")
    for equip in all_equipment:
        total_path = (
            f"./static/exercise_gifs/{equip.equipment_name}.gif"
        )
        if os.path.exists(total_path):
            equip.gif_path = total_path
            equip.equipment_description = (
                equipment_description_dict.get(
                    equip.equipment_name, "No description entry"
                )
            )
            count += 1
        else:
            print(f"path {total_path} not found")

    print(f"{count}/{total_number_of_equipment} gifs added")

    try:
        session.commit()
        return True
    except exc.SQLAlchemyError as err:
        print("error branch")
        session.rollback()
        return err


# Sets corresponding DB column for user to True
def agree_to_liability(session, user_name):
    user = (
        session.query(Users).filter(Users.user_name == user_name).one()
    )
    print("user", user)
    user.has_agreed_liability = True

    try:
        session.commit()
        return True
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


# Sets corresponding DB column for user to True
def watch_tutorial(session, user_name):
    user = (
        session.query(Users).filter(Users.user_name == user_name).one()
    )
    print("user", user)
    user.has_watched_tutorial = True

    try:
        session.commit()
        return True
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


# Sets corresponding DB column for user to False
def unwatch_tutorial(session, user_name):
    user = (
        session.query(Users).filter(Users.user_name == user_name).one()
    )
    print("user", user)
    user.has_watched_tutorial = False

    try:
        session.commit()
        return True
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


# ----------------------------------------------------------------------
# * QUERY METHODS

# Returns all past workouts of selected user
def get_past_workouts(session, user_name):
    assert session is not None
    print(f"User name: {user_name}")
    workouts = (
        session.query(Users, UserWorkouts, UserExercises)
        .join(UserWorkouts, Users.user_name == UserWorkouts.user_name)
        .join(
            UserExercises,
            UserWorkouts.workout_id == UserExercises.workout_id,
        )
        .filter(
            and_(
                Users.user_name == user_name,
                UserWorkouts.user_name == user_name,
            )
        )
        # Newer workouts show up earlier (by date and id)
        .order_by(
            desc(UserWorkouts.date),
            desc(UserWorkouts.workout_id),
            UserExercises.exercise_id,
        )
        .all()
    )

    return workouts


# Returns one most recent workout of selected user
def get_most_recent_workout(session, user_name):
    return (
        session.query(Users, UserWorkouts, UserExercises)
        .join(UserWorkouts, Users.user_name == UserWorkouts.user_name)
        .join(
            UserExercises,
            UserWorkouts.workout_id == UserExercises.workout_id,
        )
        .filter(
            and_(
                Users.user_name == user_name,
                UserWorkouts.user_name == user_name,
            )
        )
        .order_by(desc(UserWorkouts.date))
        .first()
    )


# Returns one most recent bodyweight of selected user
def get_most_recent_bodyweight(session, user_name):
    res = (
        session.query(Users, UserBodyweights.bodyweight)
        .join(
            UserBodyweights,
            Users.user_name == UserBodyweights.user_name,
        )
        .filter(
            and_(
                Users.user_name == user_name,
                UserBodyweights.user_name == user_name,
            )
        )
        .order_by(desc(UserBodyweights.date))
        .first()
    )

    if res == None:
        print("No bodyweight in DB. Returning 0")
        return 0
    else:
        return res[1]


# Returns true if a bodyweight measurement exists for the given user
def bodyweight_exists(session, user_name):
    res = (
        session.query(Users, UserBodyweights.bodyweight)
        .join(
            UserBodyweights,
            Users.user_name == UserBodyweights.user_name,
        )
        .filter(
            and_(
                Users.user_name == user_name,
                UserBodyweights.user_name == user_name,
            )
        )
        .order_by(desc(UserBodyweights.date))
        .first()
    )

    return res != None


# Returns true if the given equipment_name is a bodyweight exercise
def is_bodyweight_exercise(session, equipment_name):
    query = (
        session.query(EquipmentList.is_bodyweight)
        .filter(EquipmentList.equipment_name == equipment_name)
        .first()
    )

    # Returns False for custom workouts, and those without a designation
    if query is None:
        return False

    return (
        session.query(EquipmentList.is_bodyweight)
        .filter(
            EquipmentList.equipment_name == equipment_name,
        )
        .first()[0]
    )


# Returns all past exercises for selected user and selected piece of
# equipment, starting at the start date and ending today
def get_equipment_data(session, user_name, equipment_name, start_date):
    assert session is not None
    # add buffer to fully capture requests landing on the same day
    start_date -= timedelta(days=1)
    return (
        session.query(Users, UserWorkouts, UserExercises)
        .join(UserWorkouts, Users.user_name == UserWorkouts.user_name)
        .join(
            UserExercises,
            UserWorkouts.workout_id == UserExercises.workout_id,
        )
        .filter(
            and_(
                Users.user_name == user_name,
                UserWorkouts.user_name == user_name,
                UserWorkouts.date >= start_date,
                func.lower(UserExercises.equipment_name)
                == func.lower(equipment_name),
            )
        )
        .order_by(UserWorkouts.date)
        .all()
    )


# Returns all bodyweights for selected user (of all time)
def get_bodyweight_data(session, user_name):
    assert session is not None
    # add buffer to fully capture requests landing on the same day
    return (
        # ! do this on other tables (select just necessary cols)
        session.query(
            Users.user_name,
            UserBodyweights.bodyweight,
            UserBodyweights.date,
        )
        .join(
            UserBodyweights,
            Users.user_name == UserBodyweights.user_name,
        )
        .filter(
            and_(
                Users.user_name == user_name,
                UserBodyweights.user_name == user_name,
            )
        )
        .order_by(UserBodyweights.date)
        .all()
    )


# Estimate recommended reps of a user on a piece of equipment, given weight
def get_rep_estimation(session, user_name, equipment_name, weight):
    one_rep_estimation = (
        session.query(Users.one_rep_estimation)
        .filter(Users.user_name == user_name)
        .one()[0][equipment_name]
    )
    if one_rep_estimation == 0:
        return 0

    print("***1RM estimation = ", one_rep_estimation)
    if is_bodyweight_exercise(session, equipment_name):
        return OneRepEstimation.bodyweight_estimate_reps(
            session, user_name, one_rep_estimation, weight
        )
    else:
        return OneRepEstimation.estimate_reps(
            one_rep_estimation, weight
        )
    # return OneRepEstimation.estimate_reps(one_rep_estimation, weight)


# Estimate recommended reps of a user on a piece of equipment, given reps
def get_weight_estimation(session, user_name, equipment_name, reps):
    one_rep_estimation = (
        session.query(Users.one_rep_estimation)
        .filter(Users.user_name == user_name)
        .one()[0][equipment_name]
    )

    if one_rep_estimation == 0:
        return 0

    if is_bodyweight_exercise(session, equipment_name):
        return OneRepEstimation.bodyweight_estimate_weight(
            session, user_name, one_rep_estimation, reps
        )
    else:
        return OneRepEstimation.estimate_weight(
            one_rep_estimation, reps
        )

    # return OneRepEstimation.estimate_weight(one_rep_estimation, reps)


# Returns current one rep max estimation of a user on an equipment piece
def get_1rm_estimation(session, user_name, equipment_name):
    one_rep_estimation = (
        session.query(Users.one_rep_estimation)
        .filter(Users.user_name == user_name)
        .one()[0][equipment_name]
    )
    return one_rep_estimation


# Returns all users, or [] if empty
def get_all_users(session):
    assert session is not None
    return session.query(Users).all()


# Returns all equipment, or [] if empty
def get_all_equipment(session):
    assert session is not None
    return session.query(EquipmentList).all()


# Returns all custom equipment (user specific), or [] if empty
def get_all_custom_equipment(session, user_name):
    assert session is not None
    return (
        session.query(Users.custom_equipment)
        .filter(Users.user_name == user_name)
        .one()[0]["names"]
    )


# Returns all used equipment (user specific), or [] if empty
def get_all_used_equipment(session, user_name):
    assert session is not None
    return (
        session.query(Users.used_equipment)
        .filter(Users.user_name == user_name)
        .one()[0]["names"]
    )


# Returns requested user (by user_name), or None if not found
def get_user_by_username(session, user_name):
    assert session is not None
    return (
        session.query(Users)
        .filter(Users.user_name == user_name)
        .first()
    )


# Returns requested equipment (by equipment_id), or None if not found
def get_equipment_by_id(session, equipment_id):
    assert session is not None
    return (
        session.query(EquipmentList)
        .filter(EquipmentList.equipment_id == equipment_id)
        .first()
    )


# Returns requested equipment (by equipment_name), or None if not found
def get_equipment_by_name(session, equipment_name):
    assert session is not None
    return (
        session.query(EquipmentList)
        .filter(
            func.lower(EquipmentList.equipment_name)
            == func.lower(equipment_name)
        )
        .first()
    )


# Returns goal bodyweight of given user
def get_goal_bodyweight(session, user_name):
    assert session is not None
    return (
        session.query(Users.goal_bodyweight)
        .filter(Users.user_name == user_name)
        .first()
    )[0]


# Returns preferred name of given user
def get_preferred_name(session, user_name):
    assert session is not None
    return (
        session.query(Users.pref_name)
        .filter(Users.user_name == user_name)
        .first()
    )[0]


# Returns True if equipment_name is in EquipmentList and false if not
def equipment_in_database(session, equipment_name, user_name):
    assert session is not None

    if (
        session.query(EquipmentList)
        .filter(EquipmentList.equipment_name == equipment_name)
        .first()
        is not None
    ):
        return True

    custom_equipment_list = (
        session.query(Users.custom_equipment)
        .filter(Users.user_name == user_name)
        .one()[0]["names"]
    )
    if equipment_name in custom_equipment_list:
        return True

    else:
        return False


def has_agreed_to_liability(session, user_name):
    return (
        session.query(Users.has_agreed_liability)
        .filter(Users.user_name == user_name)
        .one()[0]
    )


def has_watched_tutorial(session, user_name):
    return (
        session.query(Users.has_watched_tutorial)
        .filter(Users.user_name == user_name)
        .one()[0]
    )


# def count_times_used_equipment(session, user_name, equipment_name):


# ----------------------------------------------------------------------
# * UTILITY METHODS

# Creates json of all equipment, with value set to 0
def get_equipment_as_blank_json(session):
    assert session is not None
    equipment_json = {}

    for row in get_all_equipment(session):
        equipment_name = row.__dict__["equipment_name"]
        equipment_json[equipment_name] = 0
    return equipment_json


def delete_workout_and_exercises(session, user_name, workout_id):
    assert workout_id >= 0
    assert user_name is not None

    # Delete workouts and exercises with corresponding workout id
    workouts = session.query(UserWorkouts).filter(
        and_(
            UserWorkouts.user_name == user_name,
            UserWorkouts.workout_id == workout_id,
        )
    )
    Query.delete(workouts)

    exercises = session.query(UserExercises).filter(
        UserExercises.workout_id == workout_id
    )
    Query.delete(exercises)

    try:
        session.commit()
        print("Workout %d deleted" % workout_id)
        return True
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


def generate_random_bodyweights(session, user_name, num):
    # Add random bodyweights
    for k in range(num):
        delta = round(random.uniform(-5, 5) * 2) / 2
        bw = 200 + delta  # [195, 205] by 0.5
        d = date.today() - timedelta(days=k)
        create_new_bodyweight(session, user_name, bw, d)

    try:
        session.commit()
        return True
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


def generate_random_dip_workouts(session, user_name, num):
    # Generate 10 random dip workouts
    workout_ids = []
    for i in range(0, num, 1):
        workout_date = date.today() - timedelta(days=num - i)
        workout_ids.append(
            create_new_workout(session, user_name, workout_date, "Demo")
        )

    # Generate 5 exercises each (all Dips)
    num_sets = 5

    for wid in workout_ids:
        num_reps_list = []
        weights_list = []
        failed_list = []

        for i in range(num_sets):
            num_reps = random.randint(-2, 16)
            if num_reps < 1:
                num_reps = 1
            num_reps_list.append(num_reps)
            weights_list.append(
                round(
                    random.randint(30, 32)
                    * ((i + 1) ** 1 / 3)
                    / (num_reps ** (1 / 4)),
                    1,
                )
            )
            # 1/4 are failed
            failed_list.append(
                bool(random.getrandbits(1) & random.getrandbits(1))
            )

        sets = {
            "num_sets": num_sets,
            "num_reps": num_reps_list,
            "weight": weights_list,
            "failed": failed_list,
            "was_pr": [],
        }
        create_new_exercise(session, user_name, wid, "Dip", sets)

    try:
        session.commit()
        return True
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


# ! no longer resets user_id
# Delets users table and resets user_id count
def dangerous_clear_table(session, table):
    assert session is not None
    session.query(table).delete()
    session.execute(
        "TRUNCATE TABLE "
        + table.get_table_name(table)
        + " RESTART IDENTITY CASCADE"
    )
    try:
        session.commit()
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


# Warning: Resets user info
def dangerous_reset_user(session, user_name):
    user = (
        session.query(Users).filter(Users.user_name == user_name).one()
    )

    # Reset Users values
    user.pref_name = user_name
    user.goal_bodyweight = 0

    equipment_json = get_equipment_as_blank_json(session)
    user.one_rep_estimation = equipment_json

    custom_equipment = {"names": []}
    user.custom_equipment = custom_equipment

    used_equipment = {"names": []}
    user.used_equipment = used_equipment

    user.has_agreed_liability = False
    user.has_watched_tutorial = False

    # Delete workouts (but doesn't delete exercises)
    workouts = session.query(UserWorkouts).filter(
        UserWorkouts.user_name == user_name,
    )
    Query.delete(workouts)

    # Delete bodyweights
    workouts = session.query(UserBodyweights).filter(
        UserBodyweights.user_name == user_name,
    )
    Query.delete(workouts)

    try:
        session.commit()
        print("Done")
        return True
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


# Warning: clears data for all users
def dangerous_reset_all_users(session):
    all_users = get_all_users(session)
    total_count = len(all_users)
    deleted_users = 0
    for user in all_users:
        did_reset_user = dangerous_reset_user(session, user.user_name)
        if did_reset_user:
            deleted_users += 1
        else:
            print(f"Failed for {user.user_name}")
    print(f"Reset {deleted_users} of {total_count} users")
    try:
        session.commit()
        return True
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


# Warning: Deletes user info
def dangerous_delete_user(session, user_name):
    user = (
        session.query(Users).filter(Users.user_name == user_name).one()
    )

    dangerous_reset_user(session, user_name)

    user = session.query(Users).filter(
        Users.user_name == user_name,
    )
    Query.delete(user)

    try:
        session.commit()
        print("Done")
        return True
    except exc.SQLAlchemyError as err:
        session.rollback()
        return err


# Warning: Deletes database info
def dangerous_reset_database(engine):
    assert engine is not None
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def create_table(engine):
    assert engine is not None
    Base.metadata.create_all(engine)


def create_local_session(
    user="rmd",
    password="xxx",
    host="localhost",
    port="5432",
    database="tigerfit",
):
    engine = create_engine(
        "postgresql"
        + os.environ["DATABASE_URL"][8:]
        # % (user, password, host, port, database)
    )
    Session = sessionmaker(bind=engine)
    return Session(), engine


def create_session():
    # postgres://username:password@hostname:port/database
    db_url = "postgresql" + os.environ["DATABASE_URL"][8:]
    engine = create_engine(db_url)
    # Session = sessionmaker(bind=engine)
    # return Session(), engine

    # create session and add objects
    # with sessionmaker(bind=engine)() as session:
    #     return session, engine

    # with create_engine(db_url) as engine:
    with sessionmaker(bind=engine)() as session:
        return session, engine


def dangerous_apply_to_all_users(session):
    for user in get_all_users(session):
        pass  # uncomment next line, using something of this form
        # user.pref_name = user.user_name
    try:
        session.commit()
        print("Done")
    except exc.SQLAlchemyError as err:
        session.rollback()
        print("Error")
        return err


# Used for testing of methods
def main():
    try:
        session, engine = create_session()
        print("Test session", session)
        print("Test engine", engine)

    finally:
        session.close()
        engine.dispose


if __name__ == "__main__":
    main()

# One rep estimation methods
class OneRepEstimation:
    # * https://en.wikipedia.org/wiki/One-repetition_maximum
    # * Brzycki Formula
    @staticmethod
    def estimate_one_rep_max(weight, reps):
        MAX_REP_LIMIT = 20
        if reps <= 0 or reps > MAX_REP_LIMIT:
            return 0
        return 36 * weight / (37 - reps)

    @staticmethod
    def estimate_weight(one_rep_max, reps):
        MAX_REP_LIMIT = 20
        if reps <= 0 or reps > MAX_REP_LIMIT:
            return 0
        return (37 - reps) * one_rep_max / 36

    @staticmethod
    def estimate_reps(one_rep_max, weight):
        MAX_REP_LIMIT = 20
        rep_estimation = 37 - 36 * weight / one_rep_max

        if rep_estimation <= 0:
            return 0
        if rep_estimation >= MAX_REP_LIMIT:
            return (
                MAX_REP_LIMIT * 5
            )  # high number (so 0.8 * est >= MAX)

        return rep_estimation

    # * For bodyweight workouts, use weight = bodyweight + weight added
    @staticmethod
    def bodyweight_estimate_one_rep_max(
        session, user_name, weight_added, reps
    ):
        MAX_REP_LIMIT = 20
        curr_bodyweight = get_most_recent_bodyweight(session, user_name)
        total_weight = weight_added + curr_bodyweight

        onerm_estimation = (
            36 * total_weight / (37 - reps) - curr_bodyweight
        )
        if reps <= 0 or reps > MAX_REP_LIMIT:
            return 0

        if onerm_estimation < 0:
            return 0
        return onerm_estimation

    @staticmethod
    def bodyweight_estimate_weight(
        session, user_name, one_rep_max, reps
    ):
        MAX_REP_LIMIT = 20
        curr_bodyweight = get_most_recent_bodyweight(session, user_name)
        total_weight = one_rep_max + curr_bodyweight

        if reps <= 0 or reps > MAX_REP_LIMIT:
            return 0

        weight_estimation = (
            37 - reps
        ) * total_weight / 36 - curr_bodyweight
        if weight_estimation < 0:
            return 0
        return weight_estimation

    @staticmethod
    def bodyweight_estimate_reps(
        session, user_name, one_rep_max, weight_added
    ):
        MAX_REP_LIMIT = 20
        curr_bodyweight = get_most_recent_bodyweight(session, user_name)

        rep_estimation = 37 - 36 * (weight_added + curr_bodyweight) / (
            one_rep_max + curr_bodyweight
        )

        if rep_estimation <= 0 or rep_estimation > MAX_REP_LIMIT:
            return 0

        return rep_estimation
