import psycopg2
import os


class DatabaseConnection:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
            )
            self.cursor = self.connection.cursor()
        except psycopg2.Error as e:
            print("Error: Unable to connect to the database:", e)

    def execute_query(self, query):
        if not self.connection:
            self.connect()

        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print("Error while executing query:", e)
            return []

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


def main():
    from dotenv import load_dotenv

    load_dotenv()

    host = "jelani.db.elephantsql.com"
    database = "jlmiiewl"
    user = "jlmiiewl"
    password = os.environ["DATABASE_PASSWORD"]

    db_connection = DatabaseConnection(host, database, user, password)

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
