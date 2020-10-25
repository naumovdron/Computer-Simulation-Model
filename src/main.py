from src.request_manager import RequestManager


if __name__ == "__main__":
    producer_count = 3
    alpha = 0.5
    beta = 1
    device_count = 2
    lambda_param = 1
    buffer_size = 4

    rm = RequestManager(producer_count, alpha, beta, device_count, lambda_param, buffer_size)

    for _ in range(1000):
        rm.process_next_event()

    print(rm.get_producers_number_of_generated_requests())
    print('deny probabilities: ', rm.get_deny_probabilities())
    print('average residence time: ', rm.get_average_residence_time())
    print('average waiting time: ', rm.get_average_waiting_time())
    print('average processing time: ', rm.get_average_processing_time())

    print('devices_utilization_rate: ', rm.get_devices_utilization_rate())
