# import flask
from flask_restx import Resource, reqparse
from flask import jsonify, request

from .environments import environments as environments
from .environments import api as api

import json


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


@api.route('/<env_uuid>/portfolios/<p_uuid>/portfolios')
class PortfolioLinks(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True, help='Portfolio name')
    parser.add_argument('optimizer', required=True, help='Optimizer type for the portfolio, options: EqualWeightsOptimizer, KellyOptimizer')
    parser.add_argument('options', type=dict, required=False, help='JSON object containing optimizer optional arguments', location='json')

    @api.doc(description='Create a new portfolio within a portfolio')
    @api.expect(parser, validate=True)
    def post(self, env_uuid, p_uuid):

        args = self.parser.parse_args()
        options = request.get_json()["options"] if request.get_json() and request.get_json()["options"] else {}

        try:
            if env_uuid in environments.keys():
                env = environments[env_uuid]["environment"]
                portfolios = environments[env_uuid]["portfolios"]
                if p_uuid in portfolios.keys():
                    portfolio = env.createDerivative(args["name"], weightGenerator=env.createOptimizer(args["optimizer"], opts=options))
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
    parser.add_argument('options', type=dict, required=False, help='JSON object containing model optional arguments', location='json')

    @api.doc(description='Create a new model within a portfolio')
    @api.expect(parser, validate=True)
    def post(self, env_uuid, p_uuid):

        args = self.parser.parse_args()
        options = request.get_json()["options"] if request.get_json() and request.get_json()["options"] else {}

        try:
            if env_uuid in environments.keys():
                env = environments[env_uuid]["environment"]
                portfolios = environments[env_uuid]["portfolios"]
                if p_uuid in portfolios.keys():
                    portfolio = env.createDerivative(args["name"], weightGenerator=env.createModel(args["type"], opts=options))
                    portfolios[p_uuid].addAsset(portfolio)
                    portfolios[portfolio.getId()] = portfolio
                    results = {"rc": "success", "model": json.loads(str(portfolio))}
                else:
                    results = {"rc": "fail", "msg": "Portfolio ID not found"}
            else:
                results = {"rc": "fail", "msg": "Environment ID not found"}
        except ValueError as e:
            results = {"rc": "fail", "msg": str(e)}

        return jsonify(results)


@api.route('/<env_uuid>/portfolios/<p_uuid>/assets')
class AssetLinks(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True, help='Asset name')

    @api.doc(description='Add a stored asset to a portfolio')
    @api.expect(parser, validate=True)
    def post(self, env_uuid, p_uuid):

        args = self.parser.parse_args()

        try:
            if env_uuid in environments.keys():
                env = environments[env_uuid]["environment"]
                portfolios = environments[env_uuid]["portfolios"]
                if p_uuid in portfolios.keys():
                    asset = env.getAssetStore().getAsset(args["name"])
                    portfolios[p_uuid].addAsset(asset)
                    results = {"rc": "success", "asset": json.loads(str(asset))}
                else:
                    results = {"rc": "fail", "msg": "Portfolio ID not found"}
            else:
                results = {"rc": "fail", "msg": "Environment ID not found"}
        except ValueError as e:
            results = {"rc": "fail", "msg": str(e)}

        return jsonify(results)
