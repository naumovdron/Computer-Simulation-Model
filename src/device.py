from src.request import *
import math
import random


class Device:
    def __init__(self, lambda_param):
        self.release_time = 0.0
        self.__lambda = lambda_param
        self.__current_request = None

    def process(self, request: Request):
        self.release_time = max(request.creation_time, self.release_time)
        self.release_time += self.__generate_delay_before_release()
        self.__current_request = request

    def release(self):
        self.__current_request = None

    def get_current_request(self):
        return self.__current_request

    # экспоненциальный закон распределения
    def __generate_delay_before_release(self):
        return random.expovariate(self.__lambda)
        # return math.log(1 - random.random()) / -self.__lambda
