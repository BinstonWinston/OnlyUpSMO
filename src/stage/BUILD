load("@rules_python//python:py_library.bzl", "py_library")
load("@pypi//:requirements.bzl", "requirement")

py_library(
    name = "stage_lib",
    srcs = [
        "__init__.py",
        "area.py",
        "object.py",
        "player_start_info.py",
        "scenario.py",
        "scenario_start_camera.py",
    ],
    deps = [
        "//src/config:config",
        "//src/math:math_lib",
        "//src/file_format:file_format_lib",
        "//src/stage/proto:stage_proto_py_pb2",
        "//src/stage/serializer:serializer_lib",
        requirement("byml"),
    ],
    visibility = ["//visibility:public"],
)
