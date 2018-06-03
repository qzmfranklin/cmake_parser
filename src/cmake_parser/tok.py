'''Various token classes used in tokenizing cmake sources.
'''

import abc
import shlex

# pylint: disable=missing-docstring


class Token(metaclass=abc.ABCMeta):

    @abc.abstractproperty
    def value(self):
        pass

    def __init__(self, orig_text):
        self.orig_text = orig_text

    def __eq__(self, other):
        return self.__class__ is other.__class__ \
                and self.orig_text == other.orig_text

    def __repr__(self):
        format_string = '<%s %s>'
        return format_string % (
            self.__class__.__name__, self.orig_text.encode()
        )


class Comment(Token):

    @property
    def value(self):
        return self.orig_text


class Argument(Token):
    # pylint: disable=abstract-method
    pass


class BracketArgument(Argument):

    @property
    def value(self):
        text = self.orig_text
        assert text.startswith('[')
        bracket_len = 1
        for i in range(1, len(text)):
            char = text[i]
            if char == '[':
                bracket_len = i + 1
                break
            elif char == '=':
                bracket_len += 1
            else:
                raise ValueError(self, 'has invalid orig_text', text)
        return text[bracket_len:-bracket_len]


class EscapedArgument(Argument):

    @property
    def value(self):
        text = self.escaped_text
        pairs = {
            '\\\n': '',
            r'\ ': ' ',
            r'\;': ';',
            r'\n': '\n',
            r'\r': '\r',
            r'\t': '\t',
            r'\v': '\v',
        }
        for key, val in pairs.items():
            text = text.replace(key, val)
        return text

    @abc.abstractproperty
    def escaped_text(self):
        pass


class QuotedArgument(EscapedArgument):

    @property
    def escaped_text(self):
        toks = shlex.split(self.orig_text)
        assert len(toks) == 1
        return toks[0]


class UnquotedArgument(EscapedArgument):

    @property
    def escaped_text(self):
        return self.orig_text


class Delimiter(Token):

    def __init__(self, unused_orig_text):  # pylint: disable=unused-argument
        # pylint: disable=no-member
        super().__init__(self.__class__.__STR__)

    @property
    def value(self):
        # pylint: disable=no-member
        return self.__class__.__STR__


class Bra(Delimiter):
    __STR__ = '('


class Ket(Delimiter):
    __STR__ = ')'
