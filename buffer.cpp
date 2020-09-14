#include "buffer.h"

Buffer::Buffer(size_t size):
    data_(size, nullptr),
    insert_iter_(data_.begin()),
    remove_iter_(data_.begin())
{}

void Buffer::insertValue(value_type value) { *(insert_iter_++) = move(value);}

Buffer::value_type Buffer::removeValue() {
    value_type value = nullptr;
    swap(*(remove_iter_++), value);
    return value;
}

bool Buffer::checkFreeSpace() {
    iterator it = insert_iter_;
    if (*it == nullptr) {
        return true;
    }
    it = getNext(it);
    while (it != insert_iter_) {
        if (*it == nullptr) {
            insert_iter_ = it;
            return true;
        }
        it = getNext(it);
    }
    return false;
}

bool Buffer::checkRemoveItem() {
    iterator it = remove_iter_;
    if (*it != nullptr) {
        return true;
    }
    it = getNext(it);
    while (it != remove_iter_) {
        if (*it != nullptr) {
            remove_iter_ = it;
            return true;
        }
        it = getNext(it);
    }
    return false;
}

Buffer::iterator Buffer::getNext(iterator pos) {
    if (++pos == data_.end()) {
        return data_.begin();
    }
    return pos;
}
