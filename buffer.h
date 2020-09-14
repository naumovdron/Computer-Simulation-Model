#pragma once

#include <list>
#include <memory>
#include "request.h"

class Buffer {
public:
    using iterator = std::list<std::shared_ptr<request_t>>::iterator;
    using value_type = std::shared_ptr<request_t>;

    explicit Buffer(size_t size);

    void insertValue(value_type value);
    value_type removeValue();

    bool checkFreeSpace();
    bool checkRemoveItem();

private:
    std::list<value_type> data_;
    iterator insert_iter_;
    iterator remove_iter_;

    iterator getNext(iterator pos);
};
