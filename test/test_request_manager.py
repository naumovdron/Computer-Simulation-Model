from src.request_manager import RequestManager, Request
import unittest


class TestRequestManager(unittest.TestCase):
    def test_init(self):
        producer_count = 50
        device_count = 7
        rm = RequestManager(producer_count, 1, 2, device_count, 1, 10)

        self.assertEqual(rm.get_producer_count(), producer_count)
        self.assertEqual(rm.get_device_count(), device_count)


if __name__ == '__main__':
    unittest.main()
