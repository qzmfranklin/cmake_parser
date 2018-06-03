py_library(
    name = 'gentemplate',
    visibility = [
        '//visibility:public',
    ],
    srcs = [
        'gentemplate.py',
    ],
    imports = [
        '.',
    ],
)

py_test(
    name = 'util_test',
    visibility = [
        '//visibility:__pkg__',
    ],
    srcs = [
        'util_test.py',
    ],
    deps = [
        ':util',
    ],
)

py_library(
    name = 'util',
    visibility = [
        '//visibility:public',
    ],
    srcs = [
        'util.py',
    ],
    imports = [
        '.',
    ],
)

py_library(
    name = 'bazel_utils',
    visibility = [
        '//visibility:public',
    ],
    srcs = [
        'bazel_utils.py',
    ],
    imports = [
        '.',
    ],
)
