from src.producer import Producer
from src.device import Device
from src.statistics import Statistics
from src.buffer import Buffer
from src.event import *
from operator import attrgetter


class RequestManager:
    def __init__(self, producer_count, alpha, beta, device_count, lambda_param, buffer_size):
        self.__producers = [Producer(i, alpha, beta) for i in range(producer_count)]
        self.__devices = [Device(lambda_param) for _ in range(device_count)]
        self.__current_device = 0
        self.__buffer = Buffer(buffer_size)
        self.__alpha = alpha
        self.__beta = beta
        self.__lambda = lambda_param

        self.__stat = Statistics(producer_count, device_count)
        self.__creation_log = []
        self.__setting_log = []

        self.__event_log = []

        self.__release_log = []
        self.__deny_log = []
        self.__buffer_log = []

    def get_producer_count(self):
        return len(self.__producers)

    def get_device_count(self):
        return len(self.__devices)

    def get_buffer_size(self):
        return self.__buffer.size()

    def get_alpha(self):
        return self.__alpha

    def get_beta(self):
        return self.__beta

    def get_lambda(self):
        return self.__lambda

    def get_logs(self):
        return self.__event_log, self.__release_log, self.__deny_log, self.__buffer_log

    def get_request_count(self):
        request_count = []
        for i in self.__producers:
            request_count.append(i.get_request_count())
        return request_count

    def get_deny_probability(self):
        return self.__stat.get_deny_probability(self.get_request_count())

    def get_utilization_rate(self):
        return self.__stat.get_utilization_rate([i.release_time for i in self.__devices])

    def get_residence_time(self):
        return self.__stat.get_residence_time(self.get_request_count())

    def get_statistics(self):
        request_count, release_times = self.get_request_count(), []
        for i in self.__devices:
            release_times.append(i.release_time)
        return self.__stat.calculate_statistics(request_count, release_times)

    # обработка следующего события
    def process_next_event(self):
        event = self.__get_next_event()
        self.__event_log.append(event)

        if isinstance(event, CreationEvent):
            self.__process_creation_event(event)

        elif isinstance(event, SettingEvent):
            self.__process_setting_event(event)

        self.__buffer_log.append(list(self.__buffer.get_data()))
        self.__pop_extra_from_logs()

    def process_remaining_requests(self):
        while not self.__buffer.empty():
            next_released_device = min(self.__devices, key=attrgetter('release_time'))
            next_released_device_time = next_released_device.release_time

            request = self.__buffer.pop()
            current = self.__current_device
            if request.creation_time <= next_released_device_time:
                current = self.__devices.index(next_released_device)
            else:
                for _ in range(len(self.__devices)):
                    if self.__devices[current].release_time <= request.creation_time:
                        break
                    current = self.__get_next_device_index(current)

            self.__release_log.append(ReleaseEvent(self.__devices[current].release_time,
                                                   current,
                                                   self.__devices[current].get_current_request()))
            self.__devices[current].release()
            e = SettingEvent(max(self.__devices[current].release_time, request.creation_time), current, request)
            self.__event_log.append(e)
            self.__process_setting_event(e)
            self.__buffer_log.append(list(self.__buffer.get_data()))
            self.__pop_extra_from_logs()

    def __pop_extra(self, log):
        while len(log) > 10:
            log.pop(0)

    # убираем устаревшие события и состояния
    def __pop_extra_from_logs(self):
        self.__pop_extra(self.__event_log)
        self.__pop_extra(self.__deny_log)
        self.__pop_extra(self.__release_log)
        self.__pop_extra(self.__buffer_log)

    # определение следующего события
    def __get_next_event(self):
        next_creating_producer = min(self.__producers, key=attrgetter('next_creation_time'))
        next_request_creation_time = next_creating_producer.next_creation_time

        next_released_device = min(self.__devices, key=attrgetter('release_time'))
        next_released_device_time = next_released_device.release_time

        if next_request_creation_time <= next_released_device_time:
            producer_id = self.__producers.index(next_creating_producer)
            self.__release_log.append(None)
            return CreationEvent(next_request_creation_time,
                                 producer_id,
                                 self.__producers[producer_id].get_request_count())

        if self.__buffer.empty():
            device_id = self.__devices.index(next_released_device)
            self.__release_log.append(ReleaseEvent(next_released_device_time,
                                                   device_id,
                                                   self.__devices[device_id].get_current_request()))
            self.__devices[device_id].release()
            producer_id = self.__producers.index(next_creating_producer)
            return CreationEvent(next_request_creation_time,
                                 producer_id,
                                 self.__producers[producer_id].get_request_count())

        request = self.__buffer.pop()
        current = self.__current_device
        if request.creation_time <= next_released_device_time:
            current = self.__devices.index(next_released_device)
        else:
            for _ in range(len(self.__devices)):
                if self.__devices[current].release_time <= request.creation_time:
                    break
                current = self.__get_next_device_index(current)

        self.__release_log.append(ReleaseEvent(self.__devices[current].release_time,
                                               current,
                                               self.__devices[current].get_current_request()))
        self.__devices[current].release()
        return SettingEvent(max(self.__devices[current].release_time, request.creation_time), current, request)

    def __process_creation_event(self, e: CreationEvent):
        new_request = self.__producers[e.producer_id].produce()
        denied = self.__buffer.push(new_request)
        if denied is not None:
            # отказали заявке
            self.__stat.increase_denies(denied.producer_id)
            self.__stat.append_waiting_time(denied.producer_id, new_request.creation_time - denied.creation_time)
            self.__deny_log.append(DenyEvent(new_request.creation_time, denied))
        else:
            self.__deny_log.append(None)

    def __process_setting_event(self, e: SettingEvent):
        self.__stat.increase_downtime_time(e.device_index, e.time - self.__devices[e.device_index].release_time)
        self.__stat.append_waiting_time(e.request.producer_id, e.time - e.request.creation_time)

        self.__devices[e.device_index].process(e.request)
        self.__current_device = self.__get_next_device_index(e.device_index)

        self.__stat.append_processing_time(e.request.producer_id, self.__devices[e.device_index].release_time - e.time)
        self.__deny_log.append(None)

    # выбор прибора по кольцу
    def __get_next_device_index(self, device_index):
        return (device_index + 1) % len(self.__devices)

    def __get_prev_device_index(self, device_index):
        return (len(self.__devices) - 1 + device_index) % len(self.__devices)
