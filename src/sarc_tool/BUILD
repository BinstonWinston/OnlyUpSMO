load("@rules_python//python:py_library.bzl", "py_library")
load("@pypi//:requirements.bzl", "requirement")

py_library(
    name = "sarc_tool",
    srcs = glob(["*.py"]),
    deps = [
        requirement("sarclib"),
        requirement("libyaz0"),
    ],
    visibility = ["//visibility:public"],
)