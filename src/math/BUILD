load("@rules_python//python:py_library.bzl", "py_library")
load("@pypi//:requirements.bzl", "requirement")

py_library(
    name = "math_lib",
    srcs = [
        "__init__.py",
        "aabb.py",
        "vec.py",
    ],
    deps = [
        requirement("byml"),
    ],
    visibility = ["//visibility:public"],
)