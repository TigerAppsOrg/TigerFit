#!/usr/bin/env python

# ----------------------------------------------------------------------
# database.py
# Author: Adam Gamba
# ----------------------------------------------------------------------

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Float,
    Boolean,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableDict


Base = declarative_base()


def get_table_name(table):
    return table.__tablename__


class Users(Base):
    __tablename__ = "users"
    get_table_name = get_table_name

    # First Integer PK column in SQLAlchemy is autoincrement
    # netID of Princeton University user
    user_name = Column(String, index=True, primary_key=True)
    # Preferred name of user
    pref_name = Column(String)
    # Goal bodyweight of user
    goal_bodyweight = Column(Integer)
    # JSON format (property for each equipment)
    # x = {
    #     'Bench Press': (int),
    #     'Squat': (int),
    #     'Deadlift': (int),
    #     ...
    # }
    one_rep_estimation = Column(MutableDict.as_mutable(JSON))
    # JSON format
    # custom_equipment = {
    #     'names': [list of Strings]
    # }
    custom_equipment = Column(MutableDict.as_mutable(JSON))
    # JSON format
    # used_equipment = {
    #     'names': [list of Strings]
    # }
    used_equipment = Column(MutableDict.as_mutable(JSON))
    # True if user has agreed to liability agreement
    has_agreed_liability = Column(Boolean, default=False)
    # True if user has watched the tutorial (add workout page)
    has_watched_tutorial = Column(Boolean, default=False)

    def get_name(self):
        return self.__tablename__

    def __repr__(self):
        return "*User %s" % (self.user_name)


class UserBodyweights(Base):
    __tablename__ = "user_bodyweights"
    get_table_name = get_table_name

    # Auto-incrementing bodyweight id
    bodyweight_id = Column(Integer, primary_key=True)
    # Username of user
    user_name = Column(String, ForeignKey("users.user_name"))
    # Recorded bodyweight
    bodyweight = Column(Float)
    # Date of collected bodyweight
    date = Column(Date)

    def __repr__(self):
        return "*Bodyweight %d: User %s, bw %f" % (
            self.bodyweight_id,
            self.user_name,
            self.bodyweight,
        )


class UserWorkouts(Base):
    __tablename__ = "user_workouts"
    get_table_name = get_table_name

    # Auto-incrementing workout id
    workout_id = Column(Integer, primary_key=True)
    # Username of user
    user_name = Column(String, ForeignKey("users.user_name"))
    # Date of recorded workout
    date = Column(Date)
    # Title of recorded workout
    workout_title = Column(String)
    # Length (minutes) of recorded workout
    minutes_taken = Column(Integer)

    # def __repr__(self):
    #     return "*UserWorkout %d: User %s, title %s" % (
    #         self.workout_id,
    #         self.user_name,
    #         self.workout_title,
    #     )

    def to_dict(self):
        return {
            "id": self.workout_id,
            "date": self.date,
            "title": self.workout_title,
            "minutes_taken": self.minutes_taken,
        }


class UserExercises(Base):
    __tablename__ = "user_exercises"
    get_table_name = get_table_name

    # Auto-incrementing exercise id
    exercise_id = Column(Integer, primary_key=True)

    # Workout id of linked foreign key
    workout_id = Column(
        Integer, ForeignKey("user_workouts.workout_id")
    )  # ADD FK
    # ALTER TABLE user_exercises ADD CONSTRAINT workout_id foreign key (workout_id) references user_workouts (workout_id);

    # Equipment name of linked foreign key
    equipment_name = Column(
        String, ForeignKey("equipment_list.equipment_name")
    )  # ADD FK
    # ALTER TABLE user_exercises ADD CONSTRAINT equipment_name foreign key (equipment_name) references equipment_list (equipment_name);

    # JSON format (n = # of sets)
    # x = {
    #     'num_sets': n (int),
    #     'num_reps': [n, int],
    #     'weights': [n, float],
    #     'failed': [n, Boolean],
    #     'was_pr': [n, Boolean]
    # }
    sets = Column(MutableDict.as_mutable(JSON))
    # Notes of recorded exercise
    notes = Column(String)

    # def __repr__(self):
    #     return "*UserExercise %d: Equip %s, workout id %d" % (
    #         self.exercise_id,
    #         self.equipment_name,
    #         self.workout_id,
    #     )

    def to_dict(self):
        return {
            "exerciseid": self.exercise_id,
            "equip_name": self.equipment_name,
            "sets": self.sets,
            "notes": self.notes,
        }


class EquipmentList(Base):
    __tablename__ = "equipment_list"
    get_table_name = get_table_name

    # Equipment name of equipment
    equipment_name = Column(String, index=True, primary_key=True)
    # Main muscle group worked by equipment
    main_muscle_group = Column(String)
    # Path of gif file to be displayed on equipment info popup
    gif_path = Column(String)
    # Description of equipment to be displayed on equipment info popup
    equipment_description = Column(String)

    # JSON format
    # sub_muscle_groups = {
    #     'tags': [list of Strings]
    # }
    sub_muscle_groups = Column(MutableDict.as_mutable(JSON))
    # True if equipment is a bodyweight exercise (no weight added)
    is_bodyweight = Column(Boolean)
    # True if equipment is a timed exercise (time/ (opt) weight inputs)
    is_timed = Column(Boolean)
    # TODO - True if equipment is a cardio exercise (time/dist inputs)
    is_cardio = Column(Boolean)
    # TODO - True if equipment is a misc exercise (misc.)
    is_misc = Column(Boolean)

    def __repr__(self):
        return "*Equipment %s" % (self.equipment_name)
