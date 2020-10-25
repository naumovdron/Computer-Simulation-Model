from src.request import Request
import math
import random


class Device:
    def __init__(self, lambda_param):
        self.release_time = 0.0
        self.__lambda = lambda_param

    def process(self, request: Request):
        self.release_time = max(request.creation_time, self.release_time)
        self.release_time += self.__generate_delay_before_release()

    # экспоненциальный закон распределения
    def __generate_delay_before_release(self):
        # random.expovariate()
        return math.log(1 - random.random()) / -self.__lambda
