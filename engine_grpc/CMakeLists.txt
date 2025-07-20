cmake_minimum_required(VERSION 3.16)
project(engine_grpc LANGUAGES CXX)

find_package(gRPC REQUIRED)

set(PROTO_FILE ${CMAKE_CURRENT_SOURCE_DIR}/order.proto)
set(GEN_DIR    ${CMAKE_CURRENT_BINARY_DIR}/generated)
file(MAKE_DIRECTORY ${GEN_DIR})

set(GENERATED_SRCS
    ${GEN_DIR}/order.pb.cc
    ${GEN_DIR}/order.grpc.pb.cc
)
set(GENERATED_HDRS
    ${GEN_DIR}/order.pb.h
    ${GEN_DIR}/order.grpc.pb.h
)

# Paths to protoc + gRPC plugin
set(PROTOC          $<TARGET_FILE:protobuf::protoc>)
set(GRPC_CPP_PLUGIN $<TARGET_FILE:gRPC::grpc_cpp_plugin>)

add_custom_command(
    OUTPUT  ${GENERATED_SRCS} ${GENERATED_HDRS}
    COMMAND ${PROTOC}
        --proto_path=${CMAKE_CURRENT_SOURCE_DIR}
        --cpp_out=${GEN_DIR}
        --grpc_out=${GEN_DIR}
        --plugin=protoc-gen-grpc=${GRPC_CPP_PLUGIN}
        ${PROTO_FILE}
    DEPENDS ${PROTO_FILE}
    COMMENT "Generating C++ sources from order.proto"
    VERBATIM
)

add_library(order_proto ${GENERATED_SRCS})
target_include_directories(order_proto PUBLIC ${GEN_DIR})
target_link_libraries(order_proto PUBLIC gRPC::grpc++ protobuf::libprotobuf)

add_executable(engine_server
    src/service_impl.cpp
    src/service_main.cpp
)

target_include_directories(engine_server
    PRIVATE
        ${GEN_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/../engine/include
)

target_link_libraries(engine_server
    PRIVATE
        order_proto
        fastob
        gRPC::grpc++
        gRPC::grpc++_reflection
        protobuf::libprotobuf
)