# pylint: disable=missing-docstring

import unittest

import _token


class TestArgumentClasses(unittest.TestCase):

    def test_bracket_argument(self):
        data = {
            '[===[[==[foo]===]': '[==[foo',
            '[===[foo]===]': 'foo',
            '[=[foo]==]]=]': 'foo]==]',
            '[=[foo]=]': 'foo',
            '[[==[foo]]': '==[foo',
            '[[foo[===]]]': 'foo[===]',
            '[[foo]]': 'foo',
            '[[foo\\bar$foo\n\n${var}]]': 'foo\\bar$foo\n\n${var}',
        }
        for orig_text, value in data.items():
            arg = _token.BracketArgument(orig_text)
            self.assertEqual(orig_text, arg.orig_text)
            self.assertEqual(value, arg.value, msg=orig_text)

    def test_quoted_argument(self):
        data = {
            '"${var}"': '${var}',
            '"foo"': 'foo',
            '"foo\\\n bar"': 'foo bar',
            r'"\n"': '\n',
            r'"\r"': '\r',
            r'"\t"': '\t',
            r'"\v"': '\v',
        }
        for orig_text, value in data.items():
            arg = _token.QuotedArgument(orig_text)
            self.assertEqual(orig_text, arg.orig_text)
            self.assertEqual(value, arg.value, msg=orig_text)

    def test_unquoted_argument(self):
        data = {
            'NoSpace': 'NoSpace',
            r'Escaped\ Space': 'Escaped Space',
            r'Escaped\;Semicolon': 'Escaped;Semicolon',
        }
        for orig_text, value in data.items():
            arg = _token.UnquotedArgument(orig_text)
            self.assertEqual(orig_text, arg.orig_text)
            self.assertEqual(value, arg.value, msg=orig_text)


if __name__ == '__main__':
    unittest.main()
