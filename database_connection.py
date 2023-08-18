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

    # params should be a list of parameters
    # Returns all_rows as [[],[],...] and is_error
    def execute_query(self, query, params=[]):
        if not self.connection:
            self.connect()

        try:
            print("executing %s:" % query)
            self.cursor.execute(query, params)

            # Contains a status like "UPDATE 3" or "SELECT 1"
            # If it is an UPDATE, it will return no rows
            update_status = self.cursor.statusmessage
            if "UPDATE" in update_status:
                return [], False

            # results = self.cursor.fetchall()
            # if len(results) > 0:
            return self.cursor.fetchall(), False
            # else:
            # return [], False
        except psycopg2.Error as e:
            print(
                "***********************Error while executing query:", e
            )
            return [], True

    # def execute_query(self, query):
    #     return DatabaseConnection.execute_query(self, query, [])

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
