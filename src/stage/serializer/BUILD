load("@rules_python//python:py_library.bzl", "py_library")
load("@pypi//:requirements.bzl", "requirement")

py_library(
    name = "serializer_lib",
    srcs = [
        "__init__.py",
        "context.py",
    ],
    data = [
        "//src/stage/base_stage_data:base_stage_data",
    ],
    deps = [
        "//src/math:math_lib",
        "//src/stage/proto:stage_proto_py_pb2",
        "//src/sarc_tool:sarc_tool",
        requirement("byml"),
    ],
    visibility = ["//visibility:public"],
)
