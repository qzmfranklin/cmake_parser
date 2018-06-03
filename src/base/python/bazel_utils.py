'''Python client for interacting with Bazel.
'''

import pathlib
import subprocess

THIS_DIR = pathlib.Path(__file__).resolve().parent


def __exec(cmd):
    '''Execute a given bazel command.

    :param cmd: The bazel command to run.
    :type cmd: List of strings.

    :return: The stdout output from the bazel command.
    :rtype: String.

    Examples:

        # bazel build //foo/bar:kaz
        __exec(['build', '//foo/bar:kaz'])

        # bazel info
        __exec(['info'])
    '''
    cmd = ['bazel'] + cmd
    return subprocess.check_output(cmd).decode()


def get_info_dict():
    '''Get a raw dictionary representation of `bazel info`.
    '''
    retval = {}
    raw_data = __exec(['info'])
    for line in raw_data.split('\n'):
        line = line.rstrip('\n')
        # Each line represents a key-value pair in the following format:
        #   <key>: <value>
        pos = line.find(':')
        key = line[:pos]
        value = line[pos + 2:]
        retval[key] = value
    return retval
