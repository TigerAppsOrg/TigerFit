#!/usr/bin/env python

# ----------------------------------------------------------------------
# multiply_1rms_by_factor.py
# Author: Adam Gamba
# ----------------------------------------------------------------------

from database_methods import (
    get_all_equipment,
    get_all_custom_equipment,
    get_all_1rms,
    insert_1RM,
    create_local_session,
)
from sys import argv, stderr, exit

# ----------------------------------------------------------------------

# Multiplies 1RMS for all default/custom equipment by factor for user
def multiy_all_1rms(session, user_name, factor=1):

    one_rms = get_all_1rms(session, user_name)
    for name in one_rms.keys():
        print("key: ", name)
        curr_1rm = one_rms[name]

        insert_1RM(session, user_name, name, curr_1rm * factor)


def main():
    try:
        session, engine = create_local_session()

        FACTOR = 1
        user_name = 'agamba'
        multiy_all_1rms(session, user_name, FACTOR)

        session.close()
        engine.dispose()

    except Exception as ex:
        print("multiply_1rms_by_factor.py failure")
        print("Exception: ", ex, file=stderr)
        session.close()
        engine.dispose()
        exit(1)


# ----------------------------------------------------------------------


if __name__ == "__main__":
    main()
