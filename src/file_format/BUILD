load("@rules_python//python:py_library.bzl", "py_library")
load("@pypi//:requirements.bzl", "requirement")

py_library(
    name = "file_format_lib",
    srcs = [
        "__init__.py",
        "bfres.py",
        "kcl.py",
    ],
    deps = [
        "//src/math:math_lib",
        requirement("cgal"),
    ],
    visibility = ["//visibility:public"],
)