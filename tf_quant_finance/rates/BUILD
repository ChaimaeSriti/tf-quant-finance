# Tools for handling rate curves.

licenses(["notice"])

package(default_visibility = ["//tf_quant_finance:__subpackages__"])

py_library(
    name = "rates",
    srcs = ["__init__.py"],
    srcs_version = "PY2AND3",
    deps = [
        ":cashflows",
        ":forwards",
        ":swap_curve_fit",
        "//tf_quant_finance/rates/constant_fwd",
        "//tf_quant_finance/rates/hagan_west",
    ],
)

py_library(
    name = "forwards",
    srcs = ["forwards.py"],
    srcs_version = "PY2AND3",
    deps = [
        "//tf_quant_finance/math:segment_ops",
        # numpy dep,
        # tensorflow dep,
    ],
)

py_test(
    name = "forwards_test",
    size = "small",
    srcs = ["forwards_test.py"],
    python_version = "PY3",
    deps = [
        ":forwards",
        # numpy dep,
        # tensorflow dep,
    ],
)

py_library(
    name = "cashflows",
    srcs = ["cashflows.py"],
    srcs_version = "PY2AND3",
    deps = [
        # numpy dep,
        # tensorflow dep,
    ],
)

py_test(
    name = "cashflows_test",
    size = "small",
    srcs = ["cashflows_test.py"],
    python_version = "PY3",
    deps = [
        ":cashflows",
        # numpy dep,
        # tensorflow dep,
    ],
)

py_library(
    name = "swap_curve_fit",
    srcs = ["swap_curve_fit.py"],
    srcs_version = "PY2AND3",
    deps = [
        "//tf_quant_finance/math:gradient",
        "//tf_quant_finance/math/interpolation/linear:linear_interpolation",
        "//tf_quant_finance/math/optimizer:conjugate_gradient",
        # attr dep,
        # numpy dep,
        # tensorflow dep,
    ],
)

py_test(
    name = "swap_curve_test",
    size = "medium",
    timeout = "long",
    srcs = ["swap_curve_test.py"],
    python_version = "PY3",
    shard_count = 3,
    deps = [
        ":swap_curve_fit",
        "//tf_quant_finance",
        "//tf_quant_finance/math/interpolation/linear",
        "//tf_quant_finance/rates/constant_fwd",
        # numpy dep,
        # tensorflow dep,
    ],
)
