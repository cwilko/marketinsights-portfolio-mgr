# import flask
from flask_restx import Resource, reqparse
from flask import jsonify, request

from marketinsights.server.portfoliomgr.models import environments as environments
from marketinsights.server.portfoliomgr.models import api as api

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
        # data.index = data.index.tz_localize('UTC')

        try:
            if env_uuid in environments.keys():
                env = environments[env_uuid]["environment"]
                data.index = data.index.tz_convert(env.getTimezone())
                asset = env.createAsset(args["market"], data)
                results = {"rc": "success", "asset": json.loads(str(asset))}
            else:
                results = {"rc": "fail", "msg": "Environment ID not found"}
        except ValueError as e:
            results = {"rc": "fail", "msg": str(e)}

        return jsonify(results)
