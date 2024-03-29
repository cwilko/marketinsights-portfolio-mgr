import unittest
import os
import json
import numpy as np
import pandas as pd
import quantutils.dataset.pipeline as ppl
from marketinsights.remote.portfoliomgr import TradeFramework
from marketinsights.api.aggregator import MarketDataAggregator
import tradeframework.operations.utils as utils  # TODO: Remove need for Asset in remote api

dir = os.path.dirname(os.path.abspath(__file__))


class FrameworkTest(unittest.TestCase):

    def setUp(self):
        HOST = os.getenv('HOSTNAME')
        if not HOST:
            HOST = "localhost"

        print(HOST)

        self.tf = TradeFramework("http://" + HOST + ":8080")

        # Get Market Data

        data_config = [
            {
                "ID": "MDS",
                "class": "MDSConnector",
                "opts": {
                    "remote": True,
                    "location": "http://pricestore.192.168.1.203.nip.io"
                },
                "timezone": "UTC",
                "markets": [
                    {
                        "ID": "DOW",
                        "sources": [
                            {
                                "ID": "WallSt-hourly",
                                "sample_unit": "H"
                            },
                            {
                                "ID": "D&J-IND",
                                "sample_unit": "5min"
                            }
                        ]
                    }
                ]

            }
        ]

        aggregator = MarketDataAggregator(data_config)

        start = "2013-01-01"
        end = "2013-07-10 18:00"

        marketData = aggregator.getData("DOW", "H", start, end, debug=False)
        marketData = marketData.reset_index().set_index("Date_Time")[["Open", "High", "Low", "Close"]]
        ts = ppl.removeNaNs(marketData)
        # ts.index = ts.index.tz_localize('UTC')
        # ts = ts.tz_convert("US/Eastern", level=0)

        self.marketData = ts

    def test_signals(self):
        response = self.tf.createEnvironment("TestEnv", "US/Eastern")
        env_uuid = response["environment"]["id"]
        p_uuid = response["environment"]["portfolio"]["id"]

        # Create prices
        response = self.tf.appendAsset(env_uuid, "DOW", json.loads(self.marketData.to_json(orient='split', date_format="iso")), debug=True)

        response = self.tf.createModel(env_uuid, p_uuid, "TestModel", "TrendFollowing", opts={"start": "15:00", "end": "16:00", "barOnly": True})
        print(response)
        m_uuid = response["model"]["id"]

        response = self.tf.addStoredAsset(env_uuid, m_uuid, "DOW")

        response = self.tf.refresh(env_uuid)

        # Get signals
        signal = self.tf.getSignal(env_uuid, 10000, debug=False)

        # Jan'23: Bug: Original value here was based on date that missed July 1st 2013 data!
        # Jan'23: Bug: To ensure test_predictions (below) works, the time series needs to run to 2pm on 2013-07-10
        self.assertTrue(np.allclose(signal["result"]["value"], 0.9912554640452014))

    def test_predictions(self):
        response = self.tf.createEnvironment("TestEnv", "US/Eastern")
        env_uuid = response["environment"]["id"]
        p_uuid = response["environment"]["portfolio"]["id"]

        # Create prices
        response = self.tf.appendAsset(env_uuid, "DOW", json.loads(self.marketData.to_json(orient='split', date_format="iso")), debug=False)

        response = self.tf.createModel(env_uuid, p_uuid, "TestModel", "TrendFollowing", opts={"start": "15:00", "end": "16:00", "barOnly": True})
        m_uuid = response["model"]["id"]

        response = self.tf.addStoredAsset(env_uuid, m_uuid, "DOW")

        response = self.tf.refresh(env_uuid)

        possibles = []

        for i in range(-10, 10):
            ohlc = [[15274.38 + i, np.nan, np.nan, np.nan]]
            index = pd.DatetimeIndex(['2013-07-10 15:00:00'], tz='US/Eastern')
            possibles.append(json.loads(utils.createAssetFromOHLC(index, ohlc, "DOW").values.to_json(orient='split', date_format="iso")))

        # Get signals
        signals = self.tf.createPredictions(env_uuid, {"prices": possibles}, "DOW", 10000, debug=False)

        self.assertEqual(signals["result"][9][0]["markets"][0]["signal"], "SELL")
        self.assertEqual(signals["result"][10][0]["markets"][0]["signal"], "HOLD")
        self.assertEqual(signals["result"][11][0]["markets"][0]["signal"], "BUY")

if __name__ == '__main__':
    unittest.main()
