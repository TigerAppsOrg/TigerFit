from database import EquipmentList
from database_methods import (
    get_all_equipment,
    create_session,
    populate_equipment_gifs,
)
from sys import stderr, exit
import os


def main():
    try:
        print("Remote session (gif population)")
        session, engine = create_session()
        print("Remote session created (gif population)")

        # use database_methods function
        did_populate = populate_equipment_gifs(session)

        session.close()
        engine.dispose()

    except Exception as ex:
        print("populate_equipment_list_gifs.py failure")
        print("Population exception: ", ex, file=stderr)
        exit(1)


# ----------------------------------------------------------------------


if __name__ == "__main__":
    main()
