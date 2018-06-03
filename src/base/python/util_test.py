# pylint: disable=missing-docstring

import pathlib
import unittest

import util

THIS_DIR = pathlib.Path(__file__).resolve().parent


class TestUtil(unittest.TestCase):

    def test_path_to_module_invalid(self):
        paths = [
            'foo.bar.py',  # illegal character '.'
            'foo/bar.ex',  # incorrect extension name
            '/foo/bar/kar.py',  # absolute path
        ]
        for path in paths:
            with self.assertRaises(ValueError):
                util.path_to_module(path)

    def test_path_to_module_valid(self):
        data = {
            'foo.py': 'foo',
            'foo/bar.py': 'foo.bar',
        }
        for path, module in data.items():
            actual_module = util.path_to_module(path)
            self.assertEqual(module, actual_module)

    def test_get_workspace(self):
        actual_workspace = THIS_DIR.parent.parent.parent
        self.assertEqual(pathlib.Path(actual_workspace), util.get_workspace())

    def test_get_country_code(self):
        data = {
            '23.38.3.132': 'NL',  # Netherlands
            '89.38.3.132': 'RO',  # Romania
            '12.8.8.9': 'US',  # United States
            '140.205.220.96': 'CN',  # China
        }
        for ip_addr, country_code in data.items():
            actual_country_code = util.get_country_code(ip_addr)
            self.assertEqual(country_code, actual_country_code)


if __name__ == '__main__':
    unittest.main()
