load("@rules_python//python:py_library.bzl", "py_library")

py_library(
    name = "kingdom_dataset",
    srcs = [
        "kingdom_dataset.py",
    ],
    data = [
        "//src/generator/data/kingdoms:kingdom_datasets",
    ],
    deps = [
        "//src/generator/data/proto:kingdom_dataset_py_pb2",
        "//src/stage:stage_lib",
    ],
    visibility = ["//visibility:public"],
)

py_library(
    name = "jump_dataset",
    srcs = [
        "jump_dataset.py",
    ],
    data = [
        "//src/generator/data/jumps:jump_dataset",
    ],
    deps = [
        "//src/generator/data/proto:jump_metadata_py_pb2",
        "//src/stage:stage_lib",
        "//src/math:math_lib",
    ],
    visibility = ["//visibility:public"],
)
