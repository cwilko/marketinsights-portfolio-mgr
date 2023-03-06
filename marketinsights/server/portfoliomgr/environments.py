# import flask
from flask_restx import Resource, reqparse, Namespace
from flask import jsonify

# import tradeframework
from tradeframework.environments import SandboxEnvironment

import json

api = Namespace('environments', description='Portfolio config operations')

environments = {}


@api.route('/')
class EnvironmentList(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True, help='Environment name')
    parser.add_argument('tz', required=True, help='Timezone for the environment')

    @api.doc(description='Get info for all environments')
    def get(self):

        results = {"rc": "success", "environments": [json.loads(str(environments[key]["environment"])) for key in environments.keys()]}
        return jsonify(results)

    @api.doc(description='Create a new trade environment')
    @api.expect(parser, validate=True)
    def post(self):

        args = self.parser.parse_args()
        try:
            env = SandboxEnvironment(args["name"], args["tz"])
            portfolio = env.createPortfolio(args["name"] + "_portfolio")
            env.setPortfolio(portfolio)
            environments[env.getId()] = {"environment": env, "portfolios": {portfolio.getId(): portfolio}, "models": {}}
            results = {"rc": "success", "environment": json.loads(str(env)), "portfolio": json.loads(str(portfolio))}
        except Exception as e:
            results = {"rc": "fail", "msg": str(e)}

        return jsonify(results)


@api.route('/<env_uuid>')
class Environment(Resource):

    @api.doc(description='Get environment info')
    def get(self, env_uuid):

        try:
            if env_uuid in environments.keys():
                results = {"rc": "success", "environment": json.loads(str(environments[env_uuid]["environment"]))}
            else:
                results = {"rc": "fail", "msg": "Environment ID not found"}
        except Exception as e:
            results = {"rc": "fail", "msg": str(e)}
        return jsonify(results)

    @api.doc(description='Remove an environment')
    def delete(self, env_uuid):

        try:
            if env_uuid in environments.keys():
                env = environments[env_uuid]["environment"]
                del environments[env_uuid]
                results = {"rc": "success", "environment": json.loads(str(env))}
            else:
                results = {"rc": "fail", "msg": "Environment ID not found"}
        except Exception as e:
            results = {"rc": "fail", "msg": str(e)}
        return jsonify(results)
