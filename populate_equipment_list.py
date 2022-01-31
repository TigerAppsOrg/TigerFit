#!/usr/bin/env python

# ----------------------------------------------------------------------
# populate_equipment_list.py
# Author: Adam Gamba
# ----------------------------------------------------------------------

from database import EquipmentList
from database_methods import (
    dangerous_clear_table,
    create_new_equipment,
    create_session,
)
from sys import argv, stderr, exit
import json

# ----------------------------------------------------------------------


def main():
    try:
        session, engine = create_session()
        print("Remote session created (population)")
        dangerous_clear_table(session, EquipmentList)
        print("EquipmentList table cleared")

        with open("./static/json/equipment_list.json") as f:
            equipment_list = json.load(f)
            print("Num Equipment", len(equipment_list))

            for equip in equipment_list:
                create_new_equipment(
                    session,
                    equipment_name=equip["equipment_name"],
                    main_muscle_group=equip["main_muscle_group"],
                    sub_muscle_groups=equip["sub_muscle_groups"],
                    is_bodyweight=equip["is_bodyweight"],
                )

        session.close()
        engine.dispose()

    except Exception as ex:
        print("populate_equipment_list.py failure")
        print("Population exception: ", ex, file=stderr)
        session.close()
        engine.dispose()
        exit(1)


# ----------------------------------------------------------------------


if __name__ == "__main__":
    main()
