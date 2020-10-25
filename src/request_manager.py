from src.producer import Producer
from src.device import Device
from src.buffer import Buffer
from src.request import Request
from operator import attrgetter


class RequestManager:
    def __init__(self, producer_count, alpha, beta, device_count, lambda_param, buffer_size):
        self.__producers = [Producer(i, alpha, beta) for i in range(producer_count)]
        self.__devices = [Device(lambda_param) for _ in range(device_count)]
        self.__current_device = 0
        self.__buffer = Buffer(buffer_size)

        self.__denies = [0 for _ in range(producer_count)]
        self.__residence_time = [0.0 for _ in range(producer_count)]
        self.__waiting_time = [0.0 for _ in range(producer_count)]
        self.__processing_time = [0.0 for _ in range(producer_count)]

        self.__downtime = [0.0 for _ in range(device_count)]

    def process_next_event(self):
        if self.__is_next_event_creation():
            new_request = min(self.__producers, key=attrgetter('next_creation_time')).produce()
            denied = self.__buffer.push(new_request)
            if denied is not None:
                # отказали заявке
                self.__denies[denied.producer_id] += 1
                self.__waiting_time[denied.producer_id] += new_request.creation_time - denied.creation_time
                self.__residence_time[denied.producer_id] += new_request.creation_time - denied.creation_time
        else:
            self.__set_request_on_device(self.__buffer.pop())

    def get_producer_count(self):
        return len(self.__producers)

    def get_device_count(self):
        return len(self.__devices)

    # количество сгенерированных каждым источником требований
    def get_producers_number_of_generated_requests(self):
        return [i.get_request_count() for i in self.__producers]

    # вероятность отказа в обслуживании заявок каждого источника
    def get_deny_probabilities(self):
        return [self.__denies[i] / self.__producers[i].get_request_count() for i in range(len(self.__producers))]

    # среднее время пребывания заявок каждого источника в системе
    def get_average_residence_time(self):
        return [self.__residence_time[i] / self.__producers[i].get_request_count()
                for i in range(len(self.__producers))]

    # среднее время ожидания заявок каждого источника в системе
    def get_average_waiting_time(self):
        return [self.__waiting_time[i] / self.__producers[i].get_request_count()
                for i in range(len(self.__producers))]

    # среднее время обслуживания заявок каждого источника
    def get_average_processing_time(self):
        return [self.__processing_time[i] / (self.__producers[i].get_request_count() - self.__denies[i])
                for i in range(len(self.__producers))]

    # TODO: дисперсии двух последних характеристик

    # коэффициент  использования  устройств
    def get_devices_utilization_rate(self):
        return [(self.__devices[i].release_time - self.__downtime[i]) / self.__devices[i].release_time
                for i in range(len(self.__devices))]

    def __is_next_event_creation(self):
        next_request_creation_time = min(self.__producers, key=attrgetter('next_creation_time')).next_creation_time
        current_device_release_time = min(self.__devices, key=attrgetter('release_time')).release_time
        if next_request_creation_time <= current_device_release_time or self.__buffer.empty():
            return True
        return False

    def __set_request_on_device(self, request: Request):
        nearest_released = self.__current_device
        current = self.__current_device
        for _ in range(len(self.__devices)):
            if self.__devices[current].release_time < self.__devices[nearest_released].release_time:
                nearest_released = current
            current = self.__get_next_device_index(current)

        processing_start_time = max(self.__devices[nearest_released].release_time, request.creation_time)

        if request.creation_time > self.__devices[nearest_released].release_time:
            self.__downtime[nearest_released] += request.creation_time - self.__devices[nearest_released].release_time
        self.__devices[nearest_released].process(request)

        processing_duration = self.__devices[nearest_released].release_time - processing_start_time
        processing_finish_time = processing_start_time + processing_duration

        self.__waiting_time[request.producer_id] += processing_start_time - request.creation_time
        self.__residence_time[request.producer_id] += processing_finish_time - request.creation_time
        self.__processing_time[request.producer_id] += processing_duration

    # выбор прибора по кольцу
    def __get_next_device_index(self, device_index):
        return (device_index + 1) % len(self.__devices)
