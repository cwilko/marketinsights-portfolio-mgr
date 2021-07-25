# import flask
from flask_restx import Resource, reqparse, Namespace
from flask import jsonify

# import tradeframework
from tradeframework.environments import SandboxEnvironment

import uuid

api = Namespace('portfolios', description='Portfolio config operations')

env = SandboxEnvironment("PortfolioMgr")
portfolios = {}


@api.route('/portfolios')
class Environment(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('optimizer', required=True, help='Optimizer type for the portfolio, options: EqualWeightsOptimizer, KellyOptimizer')

    @api.expect(parser, validate=True)
    @api.doc(description='Create a new portfolio')
    def post(self):

        args = self.parser.parse_args()

        try:
            id = str(uuid.uuid4())
            portfolios[id] = env.createPortfolio(id, env.createOptimizer(args["optimizer"], id + "_optimizer"))
            results = {"rc": "success", "id": id}
        except ValueError as e:
            results = {"rc": "fail", "msg": str(e)}

        return jsonify(results)


@api.route('/portfolios/<p_uuid>')
class Portfolios(Resource):

    @api.doc(description='Get portfolio info')
    def get(self, p_uuid):

        if p_uuid in portfolios.keys():
            results = {"rc": "success", "portfolio": str(portfolios[p_uuid]), "id": p_uuid}
        else:
            results = {"rc": "fail", "msg": "Portfolio ID not found"}
        return jsonify(results)

    @api.doc(description='Append price data to a portfolio')
    def put(self, p_uuid):

        try:
            results = {"rc": "success"}
        except ValueError as e:
            results = {"rc": "fail", "msg": str(e)}

        return jsonify(results)

    @api.doc(description='Remove a portfolio')
    def delete(self, p_uuid):

        try:
            if p_uuid in portfolios.keys():
                portfolio = env.removePortfolio(p_uuid)
                del portfolios[p_uuid]
                results = {"rc": "success", "portfolio": str(portfolio), "id": p_uuid}
            else:
                results = {"rc": "fail", "msg": "Portfolio ID not found"}
        except Exception as e:
            results = {"rc": "fail", "msg": str(e)}
        return jsonify(results)
