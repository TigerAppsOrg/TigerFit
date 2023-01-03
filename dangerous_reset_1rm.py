from database_methods import (
    reset_1RM,
    create_local_session,
)
import sys


def main():
    try:
        print("Creating session...")
        from dotenv import load_dotenv

        load_dotenv()
        session, engine = create_local_session()

        print("Session created (dangerous_reset_1rm)")

        # use database_methods function
        user_name = sys.argv[1]
        equip_name = sys.argv[2]
        result = reset_1RM(session, user_name, equip_name)
        if result == 0:
            print(f"Successfully reset {equip_name} to 0")
        else:
            print("Error. something went wrong")

        session.close()
        engine.dispose()

    except Exception as ex:
        print("error.", ex)
        exit(1)


# ----------------------------------------------------------------------


if __name__ == "__main__":
    main()
