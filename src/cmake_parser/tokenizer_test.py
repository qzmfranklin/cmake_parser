# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import glob
import pathlib
import textwrap
import unittest

import _token
import tokenizer

THIS_DIR = pathlib.Path(__file__).resolve().parent
DATA_DIR = THIS_DIR / 'test_data'


class TestCheckers(unittest.TestCase):

    def test_is_whitespace(self):
        data = ' \t\v\r\n'
        for char in data:
            actual = tokenizer.is_whitespace(char)
            self.assertEqual(actual, True, msg=ord(char))

    def test_is_quoted_character(self):
        data = ' \t\v\r\n\\#()"'
        for char in data:
            actual = tokenizer.is_quoted_character(char)
            self.assertEqual(actual, False, msg=ord(char))


class TestTokenizer(unittest.TestCase):

    def test_line_comment(self):
        linetext = '# one-line comment'
        data = {
            linetext: [
                _token.Comment(linetext),
            ],
            linetext + '\n': [
                _token.Comment(linetext),
            ],
            '\n'.join([linetext * 2, linetext]) + '\n':
            [_token.Comment(linetext * 2),
             _token.Comment(linetext)],
        }
        for text, tokens in data.items():
            g = tokenizer.Tokenizer.from_string(text)
            for actual, expected in zip(g.__iter__(), tokens):
                self.assertEqual(actual, expected)

    def test_bracket_comment(self):
        linetext = '#[[ bracket comment ]]'
        data = {
            linetext: [
                _token.Comment(linetext),
            ],
            linetext + '\n': [
                _token.Comment(linetext),
            ],
            linetext * 2: [
                _token.Comment(linetext),
                _token.Comment(linetext),
            ],
            '#[==[a\n#a': [
                _token.Comment('#[==[a'),
                _token.Comment('#a'),
            ],
            '#[=[ foo ]=] \t#[=[a]=]': [
                _token.Comment('#[=[ foo ]=]'),
                _token.Comment('#[=[a]=]'),
            ],
        }
        for text, tokens in data.items():
            g = tokenizer.Tokenizer.from_string(text)
            for actual, expected in zip(g.__iter__(), tokens):
                self.assertEqual(actual, expected)

    def test_bracket_argument(self):
        blocktext = textwrap.dedent(
            # pylint: disable=anomalous-backslash-in-string
            '''\
                [=[
                This is the first line in a bracket argument with bracket length
                1.  No \-escape sequences or ${variable} references are
                evaluated.  This is always one argument even though it contains
                a ; character.  The text does not end on a closing bracket of
                length 0 like ]].  It does end in a closing bracket of length 1.
                ]=]'''
        )
        data = {
            blocktext: [
                _token.BracketArgument(blocktext),
            ],
            '[[foo]]': [
                _token.BracketArgument('[[foo]]'),
            ],
        }
        for text, tokens in data.items():
            g = tokenizer.Tokenizer.from_string(text)
            for actual, expected in zip(g.__iter__(), tokens):
                self.assertEqual(actual, expected)

    def test_quoted_argument(self):
        data = {
            '"foo"': [
                _token.QuotedArgument('"foo"'),
            ],
            r'"\r"': [
                _token.QuotedArgument(r'"\r"'),
            ],
            r'"\t"': [
                _token.QuotedArgument(r'"\t"'),
            ],
            r'"\n"': [
                _token.QuotedArgument(r'"\n"'),
            ],
            r'"\;"': [
                _token.QuotedArgument(r'"\;"'),
            ],
            r'"\ "': [
                _token.QuotedArgument(r'"\ "'),
            ],
            '"foo;bar"': [
                _token.QuotedArgument('"foo;bar"'),
            ],
            '"foo""bar"': [
                _token.QuotedArgument('"foo"'),
                _token.QuotedArgument('"bar"'),
            ],
            '"foo\\\n bar"': [
                _token.QuotedArgument('"foo\\\n bar"'),
            ],
        }
        for text, tokens in data.items():
            g = tokenizer.Tokenizer.from_string(text)
            for actual, expected in zip(g.__iter__(), tokens):
                self.assertEqual(actual, expected)

    def test_unquoted_argument(self):
        data = {
            'foo': [
                _token.UnquotedArgument('foo'),
            ],
            r'\r': [
                _token.UnquotedArgument(r'\r'),
            ],
            r'\t': [
                _token.UnquotedArgument(r'\t'),
            ],
            r'\n': [
                _token.UnquotedArgument(r'\n'),
            ],
            r'\;': [
                _token.UnquotedArgument(r'\;'),
            ],
            r'\ ': [
                _token.UnquotedArgument(r'\ '),
            ],
            'foo;bar;': [
                _token.UnquotedArgument('foo'),
                _token.UnquotedArgument('bar'),
            ]
        }
        for text, tokens in data.items():
            g = tokenizer.Tokenizer.from_string(text)
            for actual, expected in zip(g.__iter__(), tokens):
                self.assertEqual(actual, expected)

    def test_realfiles(self):
        for src_path in glob.glob(str(DATA_DIR / '*.txt')):
            toks_path = src_path[:-len('txt')] + 'toks'
            g = tokenizer.Tokenizer.from_file(src_path)
            with open(str(toks_path), 'r') as f:
                g = tokenizer.Tokenizer.from_file(src_path)
                for expected, actual in zip(f, g):
                    expected = expected.rstrip('\n')
                    self.assertEqual(str(actual), expected, msg=src_path)


if __name__ == '__main__':
    unittest.main()
