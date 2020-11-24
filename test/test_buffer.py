from src.buffer import Buffer, Request
import unittest


class TestBuffer(unittest.TestCase):
    def test_init(self):
        buffer = Buffer(10)
        self.assertTrue(buffer.empty())

    def test_push(self):
        buffer = Buffer(3)

        self.assertTrue(buffer.push(Request(0, 1, 0.0)) is None)
        self.assertTrue(buffer.push(Request(0, 2, 0.0)) is None)
        self.assertTrue(buffer.push(Request(0, 3, 0.0)) is None)
        self.assertEqual(buffer.push(Request(0, 4, 0.0)), Request(0, 1, 0.0))
        self.assertEqual(buffer.push(Request(0, 5, 0.0)), Request(0, 2, 0.0))

    def test_pop(self):
        buffer = Buffer(4)
        buffer.push(Request(1, 1, 0.0))
        buffer.push(Request(0, 1, 0.0))
        buffer.push(Request(2, 1, 0.0))
        buffer.push(Request(0, 2, 1.0))

        self.assertEqual(buffer.pop(), Request(0, 1, 0.0))
        self.assertEqual(buffer.pop(), Request(0, 2, 1.0))
        self.assertEqual(buffer.pop(), Request(1, 1, 0.0))
        self.assertEqual(buffer.pop(), Request(2, 1, 0.0))
        self.assertTrue(buffer.empty())


if __name__ == '__main__':
    unittest.main()
