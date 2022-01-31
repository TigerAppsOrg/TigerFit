#!/usr/bin/env python

# ----------------------------------------------------------------------
# display.py
# Author: Adam Gamba
# Description: Prints out all contents of heroku postgreSQL database
# ----------------------------------------------------------------------

from sys import argv, stderr, exit
from database import (
    Base,
    Users,
    UserWorkouts,
    UserExercises,
    EquipmentList,
)
from database_methods import create_session

# ----------------------------------------------------------------------


def main():

    if len(argv) != 1:
        print("Usage: python display.py", file=stderr)
        exit(1)

    try:

        # Creates remote session
        session, _ = create_session()

        TABLE_NAMES = [
            Users,
            UserWorkouts,
            UserExercises,
            EquipmentList,
        ]
        for table in TABLE_NAMES:
            print("-------------------------------------------")
            print(table.get_table_name(table))
            print("-------------------------------------------")
            for i, row in enumerate(session.query(table).all()):
                fields_dict = vars(row)
                if i == 0 and len(fields_dict) > 1:
                    for j, var in enumerate(sorted(fields_dict)):
                        if j > 0:
                            print(var, end=" ")
                    print("\n")

                for j, var in enumerate(sorted(fields_dict)):
                    if j > 0:
                        print(fields_dict[var], end=" ")
                print()

        session.close()

    except Exception as ex:
        print(ex, file=stderr)
        session.close()
        exit(1)


# ----------------------------------------------------------------------

if __name__ == "__main__":
    main()
