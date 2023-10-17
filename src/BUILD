load("@rules_python//python:py_binary.bzl", "py_binary")
load("@pypi//:requirements.bzl", "requirement")

py_binary(
    name = "generate_stage",
    main = "main.py",
    srcs = ["main.py"],
    deps = [
        "//src/math:math_lib",
        "//src/generator/data:kingdom_dataset",
        "//src/generator:generator_lib",
        "//src/stage:stage_lib",
        "//src/sarc_tool:sarc_tool",
        "//src/file_format:file_format_lib",
        requirement("byml"),
        requirement("sarclib"),
    ],
)