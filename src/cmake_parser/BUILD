licenses(['notice'])
package(default_visibility=['//visibility:public'])

LIBS = [
    '_token',
    'char_stream',
    'tokenizer',
]

py_library(
    name = 'cmake_parser',
    deps = LIBS,
    imports = [ '.' ],
)

[py_library(
    name = lib,
    srcs = [ lib + '.py' ],
) for lib in LIBS]

[py_test(
    name = lib + '_test',
    srcs = [ lib + '_test.py' ],
    deps = [ ':' + lib ],
    testonly = True,
    size = 'small',
    data = glob([
        'test_data/*.txt',
        'test_data/*.toks',
    ]),
) for lib in LIBS]
