from database_methods import (
    get_1rm_estimation,
    create_local_session,
)
import sys


def main():
    try:
        print("Creating session...")
        from dotenv import load_dotenv

        load_dotenv()
        session, engine = create_local_session()

        print("Session created (1rm_estimation)")

        # use database_methods function
        user_name = sys.argv[1]
        equip_name = sys.argv[2]
        val = get_1rm_estimation(session, user_name, equip_name)
        print(f"One rep max estimation for {equip_name} = {val}")

        session.close()
        engine.dispose()

    except Exception as ex:
        print("error.")
        exit(1)


# ----------------------------------------------------------------------


if __name__ == "__main__":
    main()
