from src.request import Request


class Buffer:
    def __init__(self, size):
        self.__data = [None for _ in range(size)]
        self.__current_index = 0

    def push(self, request: Request):
        index = self.__current_index
        for _ in range(len(self.__data)):
            if self.__data[index] is None:
                self.__data[index] = request
                self.__current_index = self.__get_next_index(index)
                return None
            index = self.__get_next_index(index)

        # отказ под указателем
        to_deny = self.__data[self.__current_index]
        self.__data[self.__current_index] = request
        self.__current_index = self.__get_next_index(self.__current_index)
        return to_deny

    # приоритет по номеру источника, по одной заявке
    def pop(self) -> Request:
        highest_priority = 0
        for i in range(len(self.__data)):
            if self.__data[highest_priority] is None:
                highest_priority = i
            elif (self.__data[i] is not None
                  and (self.__data[i].producer_id < self.__data[highest_priority].producer_id
                       or (self.__data[i].producer_id == self.__data[highest_priority].producer_id
                           and self.__data[i].id < self.__data[highest_priority].id))):
                highest_priority = i

        to_pop = self.__data[highest_priority]
        self.__data[highest_priority] = None
        return to_pop

    def empty(self):
        for i in self.__data:
            if i is not None:
                return False
        return True

    def size(self):
        return len(self.__data)

    def get_data(self):
        return self.__data

    # буферизация по кольцу
    def __get_next_index(self, index):
        return (index + 1) % len(self.__data)
