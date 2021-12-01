# Standard library imports
import os

# Third party imports
from flask import Flask
from flask_restx import Api


# Local application imports
from endpoints import api as _api


app = Flask("api")
api = Api(app)
api.add_namespace(_api)
