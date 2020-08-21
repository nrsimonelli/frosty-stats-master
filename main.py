from flask import Flask
from flask_restful import Api, Resource

import psycopg2

app = Flask(__name__)
api = Api(app)

class Frosty(Resource):
  def get(self):
    return 201

api.add_resource(Frosty, "/")

if __name__ == "__main__":
  app.run(debug=True)
