from src.producer import Producer
import unittest


class TestProducer(unittest.TestCase):

    def test_init(self):
        producer_id = 2
        producer = Producer(producer_id, 0, 2)

        self.assertEqual(producer.id, producer_id, 'producer id')
        self.assertEqual(producer.get_request_count(), 0, 'count of request')

    def test_produce(self):
        producer_id = 1
        alpha = 0
        beta = 5
        producer = Producer(producer_id, alpha, beta)
        first_request = producer.produce()
        second_request = producer.produce()

        self.assertEqual(producer_id, first_request.producer_id, 'producer id of first request')
        self.assertEqual(producer_id, second_request.producer_id, 'second producer id of second request')
        self.assertEqual(0, first_request.id, 'first id')
        self.assertEqual(1, second_request.id, 'second id')
        self.assertTrue(first_request.creation_time >= alpha, 'lower bound of first request creation time')
        self.assertTrue(first_request.creation_time <= beta, 'upper bound of first request creation time')
        self.assertTrue(second_request.creation_time - first_request.creation_time >= alpha,
                        'lower bound of second request creation time')
        self.assertTrue(second_request.creation_time - first_request.creation_time <= beta,
                        'upper bound of second request creation time')

    def test_get_request_count(self):
        producer = Producer(1, 0, 2)
        for _ in range(100):
            producer.produce()

        self.assertEqual(producer.get_request_count(), 100, 'count of request')


if __name__ == '__main__':
    unittest.main()
