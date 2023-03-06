# import flask
from flask_restx import Resource
from flask import jsonify

from marketinsights.server.portfoliomgr.portfolios import environments as environments
from marketinsights.server.portfoliomgr.portfolios import api as api
import json


@api.route('/<env_uuid>/models')
class ModelList(Resource):

    @api.doc(description='Get info for all models for an environment')
    def get(self, env_uuid):

        try:
            if env_uuid in environments.keys():
                models = environments[env_uuid]["models"]
                results = {"rc": "success", "models": [json.loads(str(models[key])) for key in models.keys()]}
            else:
                results = {"rc": "fail", "msg": "Environment ID not found"}
        except Exception as e:
            results = {"rc": "fail", "msg": str(e)}
        return jsonify(results)


@api.route('/<env_uuid>/models/<m_uuid>')
class Model(Resource):

    @api.doc(description='Get model info')
    def get(self, env_uuid, m_uuid):

        try:
            if env_uuid in environments.keys():
                models = environments[env_uuid]["models"]
                if m_uuid in models.keys():
                    results = {"rc": "success", "model": json.loads(str(models[m_uuid]))}
                else:
                    results = {"rc": "fail", "msg": "Model ID not found"}
            else:
                results = {"rc": "fail", "msg": "Environment ID not found"}
        except ValueError as e:
            results = {"rc": "fail", "msg": str(e)}

        return jsonify(results)
