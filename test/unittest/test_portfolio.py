import unittest
import os
import json
import numpy as np
import pandas as pd
from quantutils.api.marketinsights import TradeFramework
from MIPriceAggregator.api.aggregator import MarketDataSource, MarketDataAggregator
import quantutils.dataset.pipeline as ppl
from tradeframework.api import Asset
import tradeframework.operations.utils as utils

dir = os.path.dirname(os.path.abspath(__file__))


class FrameworkTest(unittest.TestCase):

    def setUp(self):
        self.tf = TradeFramework("http://localhost:8080")

        # Get Market Data
        mds = MarketDataSource("MDSConnector", options={"remote": True, "location": "http://pricestore.192.168.1.203.nip.io"})
        aggregator = MarketDataAggregator([mds])

        market = {
            "ID": "DOW"
        }

        sources = [
            {
                "ID": "WallSt-hourly",
                "sample_unit": "H"
            },
            {
                "ID": "D&J-IND",
                "sample_unit": "5min"
            }
        ]

        start = "2013-01-01"
        end = "2013-07-11"

        marketData = aggregator.getData(market, sources, "H", start, end, debug=True)
        marketData = marketData.reset_index().set_index("Date_Time")[["Open", "Close"]]
        ts = ppl.removeNaNs(marketData)
        #ts.index = ts.index.tz_localize('UTC')
        #ts = ts.tz_convert("US/Eastern", level=0)
        self.asset = Asset("DOW", ts)

    def test_signals(self):
        response = self.tf.createEnvironment("TestEnv", "US/Eastern")
        env_uuid = response["environment"]["id"]
        p_uuid = response["environment"]["portfolio"]["id"]

        response = self.tf.createModel(env_uuid, p_uuid, "TestModel", "TrendFollowing", opts={"start": "15:00", "end": "16:00", "barOnly": True})

        # Append prices
        response = self.tf.appendAsset(env_uuid, "DOW", json.loads(self.asset.values.to_json(orient='split', date_format="iso")), debug=False)

        # Get signals
        signal = self.tf.getSignal(env_uuid, 10000, debug=False)

        print(signal)

        self.assertTrue(np.allclose(signal["result"]["value"], 0.994278195069851))

    def test_predictions(self):
        response = self.tf.createEnvironment("TestEnv", "US/Eastern")
        env_uuid = response["environment"]["id"]
        p_uuid = response["environment"]["portfolio"]["id"]

        response = self.tf.createModel(env_uuid, p_uuid, "TestModel", "TrendFollowing", opts={"start": "15:00", "end": "16:00", "barOnly": True})

        # Append prices
        response = self.tf.appendAsset(env_uuid, "DOW", json.loads(self.asset.values.to_json(orient='split', date_format="iso")), debug=False)

        possibles = []

        for i in range(-10, 10):
            ohlc = [[15274.38 + i, np.nan, np.nan, np.nan]]
            index = pd.DatetimeIndex(['2013-07-10 15:00:00'], tz='US/Eastern')
            possibles.append(json.loads(utils.createAssetFromOHLC(index, ohlc, "DOW").values.to_json(orient='split', date_format="iso")))

        # Get signals
        signals = self.tf.createPredictions(env_uuid, {"prices": possibles}, "DOW", 10000, debug=False)

        self.assertEqual(signals["result"][9]["markets"][0]["signal"], "BUY")
        self.assertEqual(signals["result"][10]["markets"][0]["signal"], "HOLD")
        self.assertEqual(signals["result"][11]["markets"][0]["signal"], "SELL")

if __name__ == '__main__':
    unittest.main()
