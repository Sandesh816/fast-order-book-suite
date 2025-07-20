#include <grpcpp/grpcpp.h>
#include <grpcpp/ext/proto_server_reflection_plugin.h>
#include <iostream>

#include "service_impl.hpp"
#include "../../engine/include/order_book_variants.hpp"

int main(int, char**) {
    grpc::reflection::InitProtoReflectionServerBuilderPlugin(); 

    const std::string address = "0.0.0.0:50051";
    std::unique_ptr<IOrderBook> book = std::make_unique<HashOrderBook>();
    EngineService service(std::move(book));

    grpc::ServerBuilder builder;
    builder.AddListeningPort(address, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);
    auto server = builder.BuildAndStart();
    std::cout << "[engine] listening on " << address << std::endl;
    server->Wait();
    return 0;
}