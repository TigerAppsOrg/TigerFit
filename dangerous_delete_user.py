#!/usr/bin/env python

# ----------------------------------------------------------------------
# dangerous_delete_user.py
# Author: Adam Gamba
# Description: Resets user of given username and generates random
# bodyweights and dip data
# ----------------------------------------------------------------------

from sys import argv, stderr, exit
from database_methods import create_session, dangerous_delete_user

# ----------------------------------------------------------------------


def main():

    if len(argv) != 2:
        print(
            "Usage: python dangerous_delete_user.py username",
            file=stderr,
        )
        exit(1)

    try:
        user_name = argv[1]

        # Creates remote session
        session, _ = create_session()

        # Reset user and generate random data
        dangerous_delete_user(session=session, user_name=user_name)

        session.close()

    except Exception as ex:
        print(ex, file=stderr)
        session.close()
        exit(1)


# ----------------------------------------------------------------------

if __name__ == "__main__":
    main()
