from database_methods import (
    create_local_session,
    dangerous_reset_database,
    create_new_user,
)

# from casclient import CasClient
import populate_equipment_list


def main():

    session, engine = create_local_session()
    dangerous_reset_database(engine)

    # Populate equipment data from equipment_list.json
    populate_equipment_list.main()

    # ! Create initial user - change when we go live
    # user_name = CasClient().authenticate()
    create_new_user(
        session, user_name="agamba", age=21, goal_bodyweight=155
    )
    create_new_user(
        session, user_name="nc12", age=20, goal_bodyweight=300
    )
    create_new_user(session, user_name="im6")
    create_new_user(session, user_name="kcapupp")
    create_new_user(session, user_name="darrenz")


if __name__ == "__main__":
    main()
