load("@rules_python//python:proto.bzl", "py_proto_library")
load("@rules_proto//proto:defs.bzl", "proto_library")

py_proto_library(
    name = "kingdom_dataset_py_pb2",
    deps = [":kingdom_dataset_proto"],
    visibility = ["//visibility:public"],
)

proto_library(
    name = "kingdom_dataset_proto",
    srcs = ["kingdom_dataset.proto"],
)

py_proto_library(
    name = "jump_metadata_py_pb2",
    deps = [":jump_metadata_proto"],
    visibility = ["//visibility:public"],
)

proto_library(
    name = "jump_metadata_proto",
    srcs = ["jump_metadata.proto"],
)