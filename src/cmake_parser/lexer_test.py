# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import glob
import pathlib
import textwrap
import unittest

import lexer
import tok

THIS_DIR = pathlib.Path(__file__).resolve().parent
DATA_DIR = THIS_DIR / 'test_data'


class TestCheckers(unittest.TestCase):

    def test_is_whitespace(self):
        data = ' \t\v\r\n'
        for char in data:
            actual = lexer.is_whitespace(char)
            self.assertEqual(actual, True, msg=ord(char))

    def test_is_quoted_character(self):
        data = ' \t\v\r\n\\#()"'
        for char in data:
            actual = lexer.is_quoted_character(char)
            self.assertEqual(actual, False, msg=ord(char))


class TestTokenizer(unittest.TestCase):

    def test_line_comment(self):
        linetext = '# one-line comment'
        data = {
            linetext: [
                tok.Comment(linetext),
            ],
            linetext + '\n': [
                tok.Comment(linetext),
            ],
            '\n'.join([linetext * 2, linetext]) + '\n':
            [tok.Comment(linetext * 2),
             tok.Comment(linetext)],
        }
        for text, tokens in data.items():
            g = lexer.Tokenizer.from_string(text)
            for actual, expected in zip(g.__iter__(), tokens):
                self.assertEqual(actual, expected)

    def test_bracket_comment(self):
        linetext = '#[[ bracket comment ]]'
        data = {
            linetext: [
                tok.Comment(linetext),
            ],
            linetext + '\n': [
                tok.Comment(linetext),
            ],
            linetext * 2: [
                tok.Comment(linetext),
                tok.Comment(linetext),
            ],
            '#[==[a\n#a': [
                tok.Comment('#[==[a'),
                tok.Comment('#a'),
            ],
            '#[=[ foo ]=] \t#[=[a]=]': [
                tok.Comment('#[=[ foo ]=]'),
                tok.Comment('#[=[a]=]'),
            ],
        }
        for text, tokens in data.items():
            g = lexer.Tokenizer.from_string(text)
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
                tok.BracketArgument(blocktext),
            ],
            '[[foo]]': [
                tok.BracketArgument('[[foo]]'),
            ],
        }
        for text, tokens in data.items():
            g = lexer.Tokenizer.from_string(text)
            for actual, expected in zip(g.__iter__(), tokens):
                self.assertEqual(actual, expected)

    def test_quoted_argument(self):
        data = {
            '"foo"': [
                tok.QuotedArgument('"foo"'),
            ],
            r'"\r"': [
                tok.QuotedArgument(r'"\r"'),
            ],
            r'"\t"': [
                tok.QuotedArgument(r'"\t"'),
            ],
            r'"\n"': [
                tok.QuotedArgument(r'"\n"'),
            ],
            r'"\;"': [
                tok.QuotedArgument(r'"\;"'),
            ],
            r'"\ "': [
                tok.QuotedArgument(r'"\ "'),
            ],
            '"foo;bar"': [
                tok.QuotedArgument('"foo;bar"'),
            ],
            '"foo""bar"': [
                tok.QuotedArgument('"foo"'),
                tok.QuotedArgument('"bar"'),
            ],
            '"foo\\\n bar"': [
                tok.QuotedArgument('"foo\\\n bar"'),
            ],
        }
        for text, tokens in data.items():
            g = lexer.Tokenizer.from_string(text)
            for actual, expected in zip(g.__iter__(), tokens):
                self.assertEqual(actual, expected)

    def test_unquoted_argument(self):
        data = {
            'foo': [
                tok.UnquotedArgument('foo'),
            ],
            r'\r': [
                tok.UnquotedArgument(r'\r'),
            ],
            r'\t': [
                tok.UnquotedArgument(r'\t'),
            ],
            r'\n': [
                tok.UnquotedArgument(r'\n'),
            ],
            r'\;': [
                tok.UnquotedArgument(r'\;'),
            ],
            r'\ ': [
                tok.UnquotedArgument(r'\ '),
            ],
            'foo;bar;': [
                tok.UnquotedArgument('foo'),
                tok.UnquotedArgument('bar'),
            ]
        }
        for text, tokens in data.items():
            g = lexer.Tokenizer.from_string(text)
            for actual, expected in zip(g.__iter__(), tokens):
                self.assertEqual(actual, expected)

    def test_realfiles(self):
        for src_path in glob.glob(str(DATA_DIR / '*.txt')):
            toks_path = src_path[:-len('txt')] + 'toks'
            g = lexer.Tokenizer.from_file(src_path)
            with open(str(toks_path), 'r') as f:
                g = lexer.Tokenizer.from_file(src_path)
                for expected, actual in zip(f, g):
                    expected = expected.rstrip('\n')
                    self.assertEqual(str(actual), expected, msg=src_path)


if __name__ == '__main__':
    unittest.main()
