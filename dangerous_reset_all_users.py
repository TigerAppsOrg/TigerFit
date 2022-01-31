#!/usr/bin/env python

# ----------------------------------------------------------------------
# dangerous_delete_all_users.py
# Author: Ian Murray
# Description: Resets data for every user
# ----------------------------------------------------------------------

from sys import argv, stderr, exit
from database_methods import (
    create_session,
    dangerous_reset_all_users,
)

# ----------------------------------------------------------------------


def main():

    if len(argv) != 1:
        print(
            "Usage: python dangerous_reset_user.py",
            file=stderr,
        )
        exit(1)

    try:
        # Creates remote session
        session, _ = create_session()

        # Reset user and generate random data
        dangerous_reset_all_users(session=session)
        # generate_random_bodyweights(
        #     session=session, user_name=user_name, num=10
        # )
        # generate_random_dip_workouts(
        #     session=session, user_name=user_name, num=10
        # )

        session.close()

    except Exception as ex:
        print(ex, file=stderr)
        session.close()
        exit(1)


# ----------------------------------------------------------------------

if __name__ == "__main__":
    main()
