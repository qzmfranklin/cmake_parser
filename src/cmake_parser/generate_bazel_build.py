#!/usr/bin/env python3
'''Generate Bazel BUILD file for llvm from the CMakelists.txt files.
'''

import pathlib
import os

THIS_DIR = pathlib.Path(__file__).resolve().parent
ROOT_DIR = THIS_DIR.parent


class CmakeModule(object):
    '''A cmake module.
    '''

    FILENAME = 'CMakeLists.txt'

    @classmethod
    def from_path(cls, cmake_path):
        '''Create a cmake module from a path.
        '''
        if str(cmake_path.relative_to(ROOT_DIR)).startswith('tools'):
            return

        with open(str(cmake_path), 'r') as f:
            for line in f:
                line = line.rstrip()
                if line.startswith('add_llvm_library('):
                    start = line.rindex('(') + 1
                    if ' ' in line:
                        end = line.index(' ')
                        module_name = line[start:end]
                        print(
                            cmake_path.parent.relative_to(ROOT_DIR),
                            module_name, line[end:]
                        )
                    else:
                        module_name = line[start:]
                        print(
                            cmake_path.parent.relative_to(ROOT_DIR), module_name
                        )

    def __init__(self):
        self.name = None
        self.srcs = []
        self.hdrs = []
        self.textual_hdrs = []
        self.deps = []
        self.additional_header_dirs = []
        self.sub_dirs = []


def main():
    for root, _, _ in os.walk(str(ROOT_DIR)):
        cmake_path = pathlib.Path(root) / CmakeModule.FILENAME
        if cmake_path.is_file():  # pylint: disable=no-member
            # pylint: disable=unused-variable
            cmake_content = CmakeModule.from_path(cmake_path)


if __name__ == '__main__':
    main()
