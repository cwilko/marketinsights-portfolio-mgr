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
    parser.add_argument('name', required=True, help='Model name')

    @api.doc(description='Get info for all environments')
    def get(self):

        results = {"rc": "success", "environments": [json.loads(str(environments[key]["environment"])) for key in environments.keys()]}
        return jsonify(results)

    @api.doc(description='Create a new trade environment')
    @api.expect(parser, validate=True)
    def post(self):

        args = self.parser.parse_args()

        try:
            env = SandboxEnvironment(args["name"])
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


@api.route('/<env_uuid>/portfolios')
class PortfolioList(Resource):

    @api.doc(description='Get info for all portfolios for an environment')
    def get(self, env_uuid):

        try:
            if env_uuid in environments.keys():
                portfolios = environments[env_uuid]["portfolios"]
                results = {"rc": "success", "portfolios": [json.loads(str(portfolios[key])) for key in portfolios.keys()]}
            else:
                results = {"rc": "fail", "msg": "Environment ID not found"}
        except Exception as e:
            results = {"rc": "fail", "msg": str(e)}
        return jsonify(results)


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


@api.route('/<env_uuid>/portfolios/<p_uuid>')
class Portfolio(Resource):

    @api.doc(description='Get portfolio info')
    def get(self, env_uuid, p_uuid):

        try:
            if env_uuid in environments.keys():
                portfolios = environments[env_uuid]["portfolios"]
                if p_uuid in portfolios.keys():
                    results = {"rc": "success", "portfolio": json.loads(str(portfolios[p_uuid]))}
                else:
                    results = {"rc": "fail", "msg": "Portfolio ID not found"}
            else:
                results = {"rc": "fail", "msg": "Environment ID not found"}
        except ValueError as e:
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


@api.route('/<env_uuid>/portfolios/<p_uuid>/portfolios')
class PortfolioLinks(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True, help='Portfolio name')
    parser.add_argument('optimizer', required=True, help='Optimizer type for the portfolio, options: EqualWeightsOptimizer, KellyOptimizer')
    parser.add_argument('args', action='append', required=False, help='Optional list of arguments for the Optimizer')

    @api.doc(description='Create a new portfolio within a portfolio')
    @api.expect(parser, validate=True)
    def post(self, env_uuid, p_uuid):

        args = self.parser.parse_args()

        try:
            if env_uuid in environments.keys():
                env = environments[env_uuid]["environment"]
                portfolios = environments[env_uuid]["portfolios"]
                if p_uuid in portfolios.keys():
                    portfolio = env.createPortfolio(args["name"], env.createOptimizer(args["name"] + "_optimizer", args["optimizer"]))
                    portfolios[p_uuid].addAsset(portfolio)
                    portfolios[portfolio.getId()] = portfolio
                    results = {"rc": "success", "portfolio": json.loads(str(portfolio))}
                else:
                    results = {"rc": "fail", "msg": "Portfolio ID not found"}
            else:
                results = {"rc": "fail", "msg": "Environment ID not found"}
        except ValueError as e:
            results = {"rc": "fail", "msg": str(e)}

        return jsonify(results)


@api.route('/<env_uuid>/portfolios/<p_uuid>/models')
class ModelLinks(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True, help='Model name')
    parser.add_argument('type', required=True, help='Model type, e.g: BuyAndHold, TrendFollowing')
    parser.add_argument('args', action='append', required=False, help='Optional list of arguments for the model')

    @api.doc(description='Create a new model within a portfolio')
    @api.expect(parser, validate=True)
    def post(self, env_uuid, p_uuid):

        args = self.parser.parse_args()

        try:
            if env_uuid in environments.keys():
                env = environments[env_uuid]["environment"]
                portfolios = environments[env_uuid]["portfolios"]
                models = environments[env_uuid]["models"]
                if p_uuid in portfolios.keys():
                    model = env.createModel(args["name"], args["type"])
                    portfolios[p_uuid].addAsset(model)
                    models[model.getId()] = model
                    results = {"rc": "success", "model": json.loads(str(model))}
                else:
                    results = {"rc": "fail", "msg": "Portfolio ID not found"}
            else:
                results = {"rc": "fail", "msg": "Environment ID not found"}
        except ValueError as e:
            results = {"rc": "fail", "msg": str(e)}

        return jsonify(results)
