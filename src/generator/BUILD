load("@rules_python//python:py_library.bzl", "py_library")

py_library(
    name = "generator_lib",
    srcs = [
        "__init__.py",
        "generator.py",
    ],
    deps = [
        "//src/math:math_lib",
        "//src/sarc_tool:sarc_tool",
        "//src/generator/data:kingdom_dataset",
        "//src/generator/data:jump_dataset",
        "//src/stage/proto:stage_proto_py_pb2",
    ],
    visibility = ["//visibility:public"],
)
