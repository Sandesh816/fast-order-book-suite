#include "service_impl.hpp"
#include "../../engine/include/order_book_variants.hpp"

EngineService::EngineService(std::unique_ptr<IOrderBook> book)
: book_(std::move(book)) {}

::grpc::Status EngineService::Limit(::grpc::ServerContext*, const fastob::LimitOrder* req, fastob::Ack* ack){
    book_->add_limit(req->is_buy(), req->price(), req->qty());
    total_orders_++;
    ack->set_ok(true);
    ack->set_message("OK");
    if (req->has_meta()) *ack->mutable_meta() = req->meta();
    return ::grpc::Status::OK;
}

::grpc::Status EngineService::Market(::grpc::ServerContext*, const fastob::MarketOrder* req, fastob::Ack* ack){
    book_->add_market(req->is_buy(), req->qty());
    total_orders_++;
    ack->set_ok(true);
    ack->set_message("OK");
    if (req->has_meta()) *ack->mutable_meta() = req->meta();
    return ::grpc::Status::OK;
}

::grpc::Status EngineService::Cancel(::grpc::ServerContext*, const fastob::CancelOrder* req, fastob::Ack* ack){
    book_->cancel(req->is_buy(), req->price(), req->qty());
    total_orders_++;
    ack->set_ok(true);
    ack->set_message("OK");
    if (req->has_meta()) *ack->mutable_meta() = req->meta();
    return ::grpc::Status::OK;
}

::grpc::Status EngineService::Top(::grpc::ServerContext*, const fastob::TopRequest*, fastob::TopReply* reply){
    reply->set_best_bid(book_->best_bid());
    reply->set_best_ask(book_->best_ask());
    return ::grpc::Status::OK;
}