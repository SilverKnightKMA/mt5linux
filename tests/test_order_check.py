import unittest
from unittest.mock import patch

import mt5linux.metatrader5 as metatrader5


class FakeConnection:
    def __init__(self):
        self._config = {}
        self.executed = []
        self.evaluated = []

    def execute(self, code):
        self.executed.append(code)

    def eval(self, code):
        self.evaluated.append(code)
        return "order-check-result"


class OrderCheckTests(unittest.TestCase):
    def setUp(self):
        self.connection = FakeConnection()

    def build_mt5(self):
        patcher = patch.object(metatrader5.rpyc.classic, "connect", return_value=self.connection)
        self.addCleanup(patcher.stop)
        patcher.start()
        return metatrader5.MetaTrader5(host="mt5", port=8001)

    def test_order_check_forwards_request_as_single_argument(self):
        request = {"action": 1, "symbol": "XAUUSD", "volume": 0.01}
        mt5 = self.build_mt5()

        result = mt5.order_check(request)

        self.assertEqual(result, "order-check-result")
        self.assertEqual(
            self.connection.evaluated[-1],
            "mt5.order_check({'action': 1, 'symbol': 'XAUUSD', 'volume': 0.01})",
        )

    def test_order_check_request_keyword_uses_same_call_shape(self):
        request = {"action": 1, "symbol": "XAUUSD", "volume": 0.01}
        mt5 = self.build_mt5()

        result = mt5.order_check(request=request)

        self.assertEqual(result, "order-check-result")
        self.assertEqual(
            self.connection.evaluated[-1],
            "mt5.order_check({'action': 1, 'symbol': 'XAUUSD', 'volume': 0.01})",
        )

    def test_order_check_uses_repr_for_request_literal(self):
        mt5 = self.build_mt5()

        result = mt5.order_check("not a request dict")

        self.assertEqual(result, "order-check-result")
        self.assertEqual(self.connection.evaluated[-1], "mt5.order_check('not a request dict')")


if __name__ == "__main__":
    unittest.main()
