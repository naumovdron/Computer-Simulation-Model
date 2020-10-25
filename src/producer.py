from src.request import Request
import random


class Producer:
    def __init__(self, producer_id, alpha, beta):
        self.id = producer_id
        self.__current_request = 0
        self.__alpha = alpha
        self.__beta = beta
        self.next_creation_time = self.__generate_delay_before_request()

    def produce(self):
        request_id = self.__current_request
        creation_time = self.next_creation_time
        new_request = Request(self.id, request_id, creation_time)

        self.__current_request += 1
        self.next_creation_time += self.__generate_delay_before_request()

        return new_request

    def get_request_count(self):
        return self.__current_request

    # равномерный закон распределения
    def __generate_delay_before_request(self):
        return random.random() * (self.__beta - self.__alpha) + self.__alpha
