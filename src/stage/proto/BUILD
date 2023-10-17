load("@rules_python//python:proto.bzl", "py_proto_library")
load("@rules_proto//proto:defs.bzl", "proto_library")

py_proto_library(
    name = "stage_proto_py_pb2",
    deps = [":stage_proto"],
    visibility = ["//visibility:public"],
)

proto_library(
    name = "stage_proto",
    srcs = glob(["*.proto"]),
)
