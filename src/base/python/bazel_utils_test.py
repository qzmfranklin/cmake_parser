# pylint: disable=missing-docstring

import os
import unittest

import bazel_utils

if 'PYTHON_RUNFILES' in os.environ:
    import textwrap
    raise RuntimeError(
        textwrap.dedent(
            '''\
            This test must be run manually via the following command:
                python3 bazel_utils_test.py'''
        )
    )


# pylint: disable=missing-docstring
class TestBazelUtils(unittest.TestCase):

    def test_get_info_dict(self):
        info_dict = bazel_utils.get_info_dict()
        self.assertIsInstance(info_dict, dict)
        keys = {'bazel-bin', 'release', 'workspace', 'bazel-genfiles'}
        for key in keys:
            self.assertIn(key, info_dict)


if __name__ == '__main__':
    unittest.main()
