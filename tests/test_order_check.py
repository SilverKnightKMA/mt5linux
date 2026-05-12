import importlib
import sys
import types
import unittest


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


class FakeClassic:
    def __init__(self):
        self.connection = FakeConnection()

    def connect(self, host, port):
        self.host = host
        self.port = port
        return self.connection


class OrderCheckTests(unittest.TestCase):
    def setUp(self):
        self.previous_rpyc = sys.modules.get("rpyc")
        self.fake_classic = FakeClassic()
        fake_rpyc = types.ModuleType("rpyc")
        fake_rpyc.__dict__["classic"] = self.fake_classic
        sys.modules["rpyc"] = fake_rpyc

        import mt5linux.metatrader5 as metatrader5

        self.metatrader5 = importlib.reload(metatrader5)

    def tearDown(self):
        if self.previous_rpyc is None:
            sys.modules.pop("rpyc", None)
        else:
            sys.modules["rpyc"] = self.previous_rpyc

    def test_order_check_forwards_request_as_single_argument(self):
        request = {"action": 1, "symbol": "XAUUSD", "volume": 0.01}
        mt5 = self.metatrader5.MetaTrader5(host="mt5", port=8001)

        result = mt5.order_check(request)

        self.assertEqual(result, "order-check-result")
        self.assertEqual(
            self.fake_classic.connection.evaluated[-1],
            "mt5.order_check({'action': 1, 'symbol': 'XAUUSD', 'volume': 0.01})",
        )

    def test_order_check_request_keyword_uses_same_call_shape(self):
        request = {"action": 1, "symbol": "XAUUSD", "volume": 0.01}
        mt5 = self.metatrader5.MetaTrader5(host="mt5", port=8001)

        result = mt5.order_check(request=request)

        self.assertEqual(result, "order-check-result")
        self.assertEqual(
            self.fake_classic.connection.evaluated[-1],
            "mt5.order_check({'action': 1, 'symbol': 'XAUUSD', 'volume': 0.01})",
        )


if __name__ == "__main__":
    unittest.main()
