# import flask
from flask_restx import Resource, reqparse
from flask import jsonify, request

from marketinsights.server.portfoliomgr.assets import environments as environments
from marketinsights.server.portfoliomgr.assets import api as api
import tradeframework.operations.trader as trader
from tradeframework.api.core import Asset

import json
import pandas


@api.route('/<env_uuid>/signals')
class Signals(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('capital', required=False, help='Starting capital amount before the signal')

    @api.doc(description='Get current portfolio signal')
    @api.expect(parser, validate=True)
    def get(self, env_uuid):

        args = self.parser.parse_args()
        capital = args["capital"] if args["capital"] else 1
        try:
            if env_uuid in environments.keys():
                env = environments[env_uuid]["environment"]
                results = {"rc": "success", "result": trader.getCurrentSignal(derivative=env.getPortfolio(), capital=int(capital))}
            else:
                results = {"rc": "fail", "msg": "Environment ID not found"}
        except ValueError as e:
            results = {"rc": "fail", "msg": str(e)}

        return jsonify(results)


@api.route('/<env_uuid>/predictions')
class Predictions(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('capital', required=False, help='Starting capital amount before the signal')
    parser.add_argument('market', required=True, help='Market for which to create predictions')
    parser.add_argument('prices', type=dict, required=True, help='JSON object containing list of predicted OHLC data', location='json')

    @api.doc(description='Get a set of signals based on the predicted prices in the JSON body')
    @api.expect(parser, validate=True)
    def post(self, env_uuid):

        args = self.parser.parse_args()
        capital = args["capital"] if args["capital"] else 1
        body = request.get_json()["prices"]["prices"]

        try:

            if env_uuid in environments.keys():
                env = environments[env_uuid]["environment"]

                prices = []
                for price in body:
                    price = pandas.read_json(json.dumps(price), orient='split')
                    # Uncomment the following on pandas < 1.2.0
                    #price.index = price.index.tz_localize('UTC')
                    price.index = price.index.tz_convert(env.getTimezone())
                    prices.append(Asset(args["market"], price))

                results = {"rc": "success", "result": trader.predictSignals(derivative=env.getPortfolio(), prices=prices, capital=int(capital))}
            else:
                results = {"rc": "fail", "msg": "Environment ID not found"}
        except ValueError as e:
            results = {"rc": "fail", "msg": str(e)}

        return jsonify(results)
