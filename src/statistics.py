
class Statistics:
    def __init__(self, producer_count, device_count):
        self.__denies = [0 for _ in range(producer_count)]
        self.__waiting_time = [[] for _ in range(producer_count)]
        self.__processing_time = [[] for _ in range(producer_count)]

        self.__downtime = [0.0 for _ in range(device_count)]

    def increase_denies(self, producer_id):
        self.__denies[producer_id] += 1

    def append_waiting_time(self, producer_id, value):
        self.__waiting_time[producer_id].append(value)

    def append_processing_time(self, producer_id, value):
        self.__processing_time[producer_id].append(value)

    def increase_downtime_time(self, device_id, value):
        self.__downtime[device_id] += value

    def get_deny_probability(self, request_count):
        if sum(request_count) != 0:
            return sum(self.__denies) / sum(request_count)
        return 0

    def get_utilization_rate(self, release_times):
        if sum(release_times) != 0:
            return (sum(release_times) - sum(self.__downtime)) / sum(release_times)
        return 0

    def get_residence_time(self, request_count):
        if sum(request_count) != 0:
            waiting_time = 0
            for i in self.__waiting_time:
                waiting_time += sum(i) / sum(request_count)
            if sum(request_count) != sum(self.__denies):
                processing_time = 0
                for i in self.__processing_time:
                    processing_time += sum(i) / (sum(request_count) - sum(self.__denies))
                return waiting_time + processing_time
            return waiting_time
        return 0

    def calculate_statistics(self, request_count, release_times):
        deny_probabilities = []
        average_waiting_time = []
        average_processing_time = []
        for i in range(len(request_count)):
            if request_count[i] != 0:
                # вероятность отказа в обслуживании заявок каждого источника
                deny_probabilities.append(self.__denies[i] / request_count[i])

                # среднее время ожидания заявок каждого источника в системе
                average_waiting_time.append(sum(self.__waiting_time[i]) / request_count[i])

                # среднее время обслуживания заявок каждого источника
                if request_count[i] != self.__denies[i]:
                    average_processing_time.append(sum(self.__processing_time[i]) / (request_count[i] - self.__denies[i]))
                else:
                    average_processing_time.append(0)
            else:
                deny_probabilities.append(0.0)
                average_waiting_time.append(0.0)
                average_processing_time.append(0.0)

        # среднее время пребывания заявок каждого источника в системе
        average_residence_time = [i + j for i, j in zip(average_processing_time, average_waiting_time)]

        waiting_time_dispersion = []
        processing_time_dispersion = []
        for i in range(len(request_count)):
            waiting_time_dispersion.append(0.0)
            processing_time_dispersion.append(0.0)
            if request_count[i] != 0:
                for j in self.__waiting_time[i]:
                    # дисперсия среднего времени ожидания заявок каждого источника в системе
                    waiting_time_dispersion[-1] += pow(j - average_waiting_time[i], 2)

                    # дисперсия среднего времени обслуживания заявок каждого источника
                    processing_time_dispersion[-1] += pow(j - average_processing_time[i], 2)
                waiting_time_dispersion[-1] /= request_count[i]
                if request_count[i] != self.__denies[i]:
                    processing_time_dispersion[-1] /= request_count[i] - self.__denies[i]
                else:
                    processing_time_dispersion[-1] = 0

        utilization_rate = []
        for i in range(len(release_times)):
            if release_times[i] != 0.0:
                # коэффициент  использования  устройств
                utilization_rate.append((release_times[i] - self.__downtime[i]) / release_times[i])
            else:
                utilization_rate.append(0.0)

        return deny_probabilities,\
            average_residence_time, average_waiting_time, average_processing_time,\
            waiting_time_dispersion, processing_time_dispersion,\
            utilization_rate
