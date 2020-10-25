from src.device import Device, Request
import unittest


class TestDevice(unittest.TestCase):
    def test_init(self):
        device = Device(1)

        self.assertEqual(device.release_time, 0.0, 'release time after init')

    def test_process(self):
        device = Device(1)
        request = Request(0, 1, 0.0)
        request_count = 100000

        for _ in range(request_count):
            device.process(request)

        self.assertTrue(abs(device.release_time - request_count) / request_count < 0.01,
                        'mean without delays')

        device = Device(1)
        request = Request(0, 1, 0.5)
        request_count = 100000

        for _ in range(request_count):
            device.process(request)
            request = Request(0, 1, device.release_time + 0.5)

        self.assertTrue(abs(device.release_time - 1.5 * request_count) / (1.5 * request_count) < 0.01,
                        'mean with delays')


if __name__ == '__main__':
    unittest.main()
