# import flask
from flask_restx import Resource, reqparse
from flask import jsonify, request

from tradeframework.api import Asset
from .models import environments as environments
from .models import api as api

import json
import pandas


@api.route('/<env_uuid>/assets')
class Assets(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('market', required=True, help='Market name')

    @api.doc(description='Append prices to the portfolio within an environment')
    @api.expect(parser, validate=True)
    def post(self, env_uuid):

        args = self.parser.parse_args()
        data = pandas.read_json(json.dumps(request.get_json()), orient='split')

        # Uncomment the following on pandas < 1.2.0
        #data.index = data.index.tz_localize('UTC')

        try:
            if env_uuid in environments.keys():
                env = environments[env_uuid]["environment"]
                data.index = data.index.tz_convert(env.getTimezone())
                portfolio = env.append(Asset(args["market"], data), copy=False)
                results = {"rc": "success", "portfolio": json.loads(str(portfolio))}
            else:
                results = {"rc": "fail", "msg": "Environment ID not found"}
        except ValueError as e:
            results = {"rc": "fail", "msg": str(e)}

        return jsonify(results)

    @api.doc(description='Append prices to a copy of the portfolio within an environment')
    @api.expect(parser, validate=True)
    def put(self, env_uuid):

        args = self.parser.parse_args()
        data = pandas.read_json(json.dumps(request.get_json()), orient='split')

        # Uncomment the following on pandas < 1.2.0
        #data.index = data.index.tz_localize('UTC')

        try:
            if env_uuid in environments.keys():
                env = environments[env_uuid]["environment"]
                data.index = data.index.tz_convert(env.getTimezone())
                portfolio = env.append(Asset(args["market"], data), copy=True)
                environments[env_uuid]["portfolios"][portfolio.getId()] = portfolio
                results = {"rc": "success", "portfolio": json.loads(str(portfolio))}
            else:
                results = {"rc": "fail", "msg": "Environment ID not found"}
        except ValueError as e:
            results = {"rc": "fail", "msg": str(e)}

        return jsonify(results)
