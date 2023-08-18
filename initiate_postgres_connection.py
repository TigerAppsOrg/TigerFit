import os
import database_connection as db_conn


def main():
    from dotenv import load_dotenv

    load_dotenv()

    host = "jelani.db.elephantsql.com"
    database = "jlmiiewl"
    user = "jlmiiewl"
    password = os.environ["DATABASE_PASSWORD"]

    db_connection = db_conn.DatabaseConnection(
        host, database, user, password
    )

    while True:
        sql_statement = input(
            "Enter SQL statement to execute (or 'exit' to quit): "
        )

        if sql_statement.lower() == "exit":
            db_connection.close()
            print("Exiting...")
            break

        results = db_connection.execute_query(sql_statement)
        print("Query results:", results)


if __name__ == "__main__":
    main()
