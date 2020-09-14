#include "infinity_producer.h"

#include <cstdlib>

InfinityProducer::InfinityProducer(size_t id, double lambda):
        id_(id),
        lambda_(lambda),
        t_last_(0)
{}

InfinityProducer::InfinityProducer(size_t id,double lambda, double t):
        id_(id),
        lambda_(lambda),
        t_last_(t)
{}

std::shared_ptr<request_t> InfinityProducer::generate() {
    // Пуассоновский закон распределения
    t_last_ += -1 / lambda_ * log(static_cast<double>(rand()) / RAND_MAX);
    return std::make_shared<request_t>(request_t{id_, t_last_});
}
