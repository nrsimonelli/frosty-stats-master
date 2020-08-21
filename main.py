from flask import Flask
from flask_restful import Api, Resource

import psycopg2

app = Flask(__name__)
api = Api(app)
# assign database name & location to variable "db"
db = "dbname=%s host=%s " % ('mini_stats', 'localhost')
schema = "schema.sql"


# initializes connection to PostgreSQL
def get_connection():
    connection = psycopg2.connect(db)
    return connection


# closes connection to PostgreSQL
def close_connection(connection):
    if connection:
        connection.close()
        print("Postgres connection is now closed")


# prints database version
def read_database_version():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print("You are connect to PostgreSQL version: ", db_version)
        close_connection(connection)
    except (Exception, psycopg2.Error) as error:
        print("Error while getting data", error)


# runs read_database_version and tests connection to PostgreSQL
print("Printing Database version:")
read_database_version()


class Frosty(Resource):
    def get(self):
        return 201


api.add_resource(Frosty, "/")

if __name__ == "__main__":
    app.run(debug=True)
