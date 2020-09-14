#pragma once

#include <memory>
#include "request.h"

class InfinityProducer {
public:
    InfinityProducer(size_t id, double lambda);
    InfinityProducer(size_t id, double lambda, double t);

    std::shared_ptr<request_t> generate();

private:
    const size_t id_;
    const double lambda_;
    double t_last_;
};
