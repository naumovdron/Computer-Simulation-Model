import math
import random
from operator import attrgetter
from typing import NamedTuple


class Request(NamedTuple):
    producer_id: int
    id: int
    creation_time: float


class Buffer:
    def __init__(self, size):
        self.__data = [None for _ in range(size)]
        self.__current_index = 0

    def push(self, request: Request):
        # проверка текущей позиции вне цикла, так как в случае, когда размер буфера равен единице,
        # индекс текущего и следующего элемента совпадают
        if self.__data[self.__current_index] is None:
            self.__data[self.__current_index] = request
            self.__current_index = self.__get_next_index(self.__current_index)
            return None
        index = self.__get_next_index(self.__current_index)
        while index != self.__current_index:
            if self.__data[index] is None:
                self.__data[index] = request
                self.__current_index = self.__get_next_index(self.__current_index)
                return None
            index = self.__get_next_index(index)

        # отказ под указателем
        to_deny = self.__data[self.__current_index]
        self.__data[self.__current_index] = request
        self.__current_index = self.__get_next_index(self.__current_index)
        return to_deny

    # приоритет по номеру источника, по одной заявке
    def pop(self):
        current_index = 0
        for i in range(len(self.__data)):
            if (self.__data[i] is not None
                    and (self.__data[i].producer_id < self.__data[current_index].producer_id
                         or (self.__data[i].producer_id == self.__data[current_index].producer_id
                             and self.__data[i].id < self.__data[current_index].id))):
                current_index = i
        to_pop = self.__data[current_index]
        self.__data[current_index] = None
        return to_pop

    # буферизация по кольцу
    def __get_next_index(self, index):
        index += 1
        if index == len(self.__data):
            index = 0
        return index


class Producer:
    def __init__(self, producer_id, alpha, beta):
        self.id = producer_id
        self.next_creation_time = 0.0
        self.__current_request = 0
        self.__alpha = alpha
        self.__beta = beta

    def produce(self):
        request_id = self.__current_request
        creation_time = self.next_creation_time
        self.__current_request += 1
        # равномерный закон распределения
        self.next_creation_time = random.random() * (self.__beta - self.__alpha) + self.__alpha
        return Request(self.id, request_id, creation_time)


class Device:
    def __init__(self, lambda_param):
        self.release_time = 0.0
        self.__lambda = lambda_param

    def process(self, request: Request):
        pass
        # экспоненциальный закон распределения
        # self.__release_time +=


class RequestManager:
    def __init__(self, producer_count, alpha, beta, device_count, lambda_param, buffer_size):
        self.__producers = [Producer(i, alpha, beta) for i in range(producer_count)]
        self.__request_count = 0
        self.__devices = [Device(lambda_param) for _ in range(device_count)]
        self.__current_device = 0
        self.__buffer = Buffer(buffer_size)

    def process_next_event(self):
        if self.__is_next_event_creation():
            new_request = min(self.__producers, key=attrgetter('next_creation_time')).produce()
            self.__request_count += 1
            if self.__buffer.push(new_request):
                pass
            else:
                # отказали заявке
                pass
        else:
            self.__devices[self.__current_device].process(self.__buffer.pop())
            self.__current_device = self.__get_next_device_index(self.__current_device)

    def __is_next_event_creation(self):
        next_request_creation_time = min(self.__producers, key=attrgetter('next_creation_time')).next_creation_time
        current_device_release_time = self.__devices[self.__current_device].release_time
        if next_request_creation_time <= current_device_release_time:
            return True
        return False

    # выбор прибора по кольцу
    def __get_next_device_index(self, device_index):
        device_index += 1
        if device_index == len(self.__devices):
            device_index = 0
        return device_index


def main():
    rm = RequestManager(1, 1, 2, 1, 1, 1)
    rm.process_next_event()
    rm.process_next_event()


if __name__ == "__main__":
    main()
