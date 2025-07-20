#include <memory>
#include <grpcpp/grpcpp.h>
#include "order.grpc.pb.h"
#include "order.pb.h"
#include "../../engine/include/order_book_variants.hpp"

class EngineService final : public fastob::EngineInternal::Service {
public:
    explicit EngineService(std::unique_ptr<IOrderBook> book);
    ::grpc::Status Limit(::grpc::ServerContext*, const fastob::LimitOrder*, fastob::Ack*) override;
    ::grpc::Status Market(::grpc::ServerContext*, const fastob::MarketOrder*, fastob::Ack*) override;
    ::grpc::Status Cancel(::grpc::ServerContext*, const fastob::CancelOrder*, fastob::Ack*) override;
    ::grpc::Status Top(::grpc::ServerContext*, const fastob::TopRequest*, fastob::TopReply*) override;
private:
    std::unique_ptr<IOrderBook> book_;
    uint64_t total_orders_ = 0;
};