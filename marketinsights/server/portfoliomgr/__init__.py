from flask_restx import Api

from marketinsights.server.portfoliomgr.signals import api as ns1

api = Api(
    title='Portfolio Manager API',
    version='1.0',
    description='MarketInsights Portfolio Manager API',
    # All API metadatas
)

api.add_namespace(ns1)
