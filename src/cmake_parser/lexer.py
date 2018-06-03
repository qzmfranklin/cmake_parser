r'''Tokenize cmake file.


This module does NOT support parsing legacy unquoted elements.  Examples of such
elements and how they SHOULD be quoted are:
        ORIGINAL FORM           QUOTED FORM
        -Da="b c"               "-Da=\"b c\""
        -Da=$(v)                "-Da=$(v)"
        a" "b"c"d               "a\" \"b\"c\"d"
'''

import enum
import io
import re

import char_stream
import tok


def is_whitespace(char):
    '''Check whether a character this is a whitespace character.
    '''
    return char and char in ' \t\v\n\r'


def is_quoted_character(char):
    r'''
    unquoted_element  ::=  <any character except whitespace or one of '()#"\'> |
                       escape_sequence
    '''
    return char and not is_whitespace(char) and char not in '()#"\\'


@enum.unique
class _State(enum.Enum):
    '''Internal state of Tokenizer.

    Must not be used publicly.
    '''

    # TODO (zhongming): Upgrade to python3.6 and start using enum.auto() to
    # simlify assignment of numbers here.
    Start = 0

    Comment = 100
    CommentLine = 101
    CommentBracketOpen = 102
    CommentBracketContent = 103
    CommentBracketClose = 104

    BracketArgumentOpen = 200
    BracketArgumentContent = 201
    BracketArgumentClose = 202

    QuotedArgument = 300
    QuotedArgumentBackslash = 301

    UnquotedArgument = 400
    UnquotedArgumentEscape = 401

    End = -1


class Tokenizer(object):
    '''Tokenize a CMakeLists.txt file.
    '''

    @classmethod
    def from_string(cls, text):
        '''Create a Tokenizer from a string.
        '''
        return cls(char_stream.CharStream(io.StringIO(text)))

    @classmethod
    def from_file(cls, filename):
        '''Create a Tokenizer from a CMakeLists.txt file.
        '''
        return cls(char_stream.CharStream(open(str(filename), 'r')))

    def __init__(self, stream):
        assert isinstance(stream, char_stream.CharStream)
        self._stream = stream
        self._state = _State.Start
        self._orig_text = ''

        # Variables used in the state machine.
        self.__open_block_length = 0
        self.__close_block_length = 0

    def __del__(self):
        self._stream.close()

    def _push(self, *, to_next=True):
        '''Push the current character into the symbol.

        :to_next: If True, also moves the input stream to the next position.
            Otherwise, the input stream is untouched.

        This is an internal method and MUST NOT be used publicly.
        '''
        curr = self._stream.curr()
        if not curr is None:
            self._orig_text += self._stream.curr()
            if to_next:
                next(self._stream)

    def _error(self):
        '''Report tokenizing error.
        '''
        curr = self._stream.curr()
        raise ValueError(self._orig_text, 'cannot parse', curr)

    def _next(self):
        '''Move the input stream forward by one character.

        If it already reached the EOF, do nothing and do not raise the
        StopIteration exception.
        '''
        try:
            next(self._stream)
        except StopIteration:
            pass

    def _emit(self, clazz):
        '''Emit token.

        Clear internal the symbol but do not touch the input stream.

        Only subclasses of tok.Token will be processed.

        This is an internal method and MUST NOT be used publicly.
        '''
        assert issubclass(clazz, tok.Token)
        retval = clazz(self._orig_text)
        self._orig_text = ''
        return retval

    def __iter__(self):
        while not self._stream.is_eof():
            result = self._iterate()
            if result:
                yield result
        result = self._iterate()
        if result:
            yield result

    def __next__(self):
        while not self._stream.is_eof():
            result = self._iterate()
            if result:
                return result
        result = self._iterate()
        if result:
            return result

    __REGEX__ = re.compile('[^A-Za-z0-9;]')

    def _iterate(self):
        '''Iterate one character.

        This is an internal method and MUST NOT be used publicly.

        If you want to iterate through the tokens, use the __iter__() method.
        '''
        # pylint: disable=too-many-return-statements
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements
        curr = self._stream.curr()
        # if curr:
        # print(self._state.name, '\t', curr.encode())
        # else:
        # print(self._state.name, '\t', curr)
        if self._state == _State.Start:
            # Existing: (empty)
            # #             ->  Comment
            # [             ->  BracketArgumentOpen
            # "             ->  QuotedArgument
            #
            if curr == '#':
                self._push()
                self._state = _State.Comment
            elif curr == '[':
                self._push()
                self.__open_block_length = 0
                self._state = _State.BracketArgumentOpen
            elif curr == '"':
                self._push()
                self._state = _State.QuotedArgument
            elif curr == '(':
                self._push()
                return self._emit(tok.Bra)
            elif curr == ')':
                self._push()
                return self._emit(tok.Ket)
            elif is_whitespace(curr):
                self._next()
            else:
                if curr != '\\':
                    self._push()
                self._state = _State.UnquotedArgument
        elif self._state == _State.Comment:
            # Existing:  #
            # [             ->  CommentBracketOpen
            #                   reset __open_block_length
            # \n EOF        ->  Start
            #                   _emit Comment
            # other         ->  CommentLine
            if curr == '[':
                self._push()
                self.__open_block_length = 0
                self._state = _State.CommentBracketOpen
            elif curr == '\n' or curr is None:
                self._next()
                self._state = _State.Start
                return self._emit(tok.Comment)
            else:
                self._push()
                self._state = _State.CommentLine
        elif self._state == _State.CommentLine:
            # Existing: #[^\[].*
            # \n EOF        ->  Start
            #                   _emit Comment
            # other         ->  CommentLine
            if curr == '\n' or curr is None:
                self._next()
                self._state = _State.Start
                return self._emit(tok.Comment)
            else:
                self._push()
                self._state = _State.CommentLine
        elif self._state == _State.CommentBracketOpen:
            # Existing: #\[=*
            # =             ->  increment __open_block_length
            # [             ->  CommmentBracketContent
            # \n EOF        ->  Start
            #                   _emit Comment
            # other         ->  CommentLine
            if curr == '=':
                self._push()
                self.__open_block_length += 1
            elif curr == '[':
                self._push()
                self._state = _State.CommentBracketContent
            elif curr == '\n' or curr is None:
                self._next()
                self._state = _State.Start
                return self._emit(tok.Comment)
            else:
                self._push()
                self._state = _State.CommentLine
        elif self._state == _State.CommentBracketContent:
            # Existing: #\[={len}\[.*
            # ]             ->  CommentBracketClose
            #                   reset __close_block_length
            # \n EOF        ->  Start
            #                   _emit Comment
            # other         ->  CommentLine
            if curr == ']':
                self._push()
                self.__close_block_length = 0
                self._state = _State.CommentBracketClose
            elif curr == '\n' or curr is None:
                self._next()
                self._state = _State.Start
                return self._emit(tok.Comment)
            else:
                self._push()
        elif self._state == _State.CommentBracketClose:
            # Existing: #\[={len}[.*\]=*
            # =             ->  increment __close_block_length
            # ] (same len)  ->  Start
            #                   _emit Comment
            # \n EOF        ->  Start
            #                   _emit Comment
            # other         ->  CommentBracketContent
            if curr == '=':
                self._push()
                self.__close_block_length += 1
            elif curr == ']' and \
                    self.__close_block_length == self.__open_block_length:
                self._push()
                self._state = _State.Start
                return self._emit(tok.Comment)
            elif curr == '\n' or curr is None:
                self._next()
                self._state = _State.Start
                return self._emit(tok.Comment)
            else:
                self._push()
                self._state = _State.CommentBracketContent
        elif self._state == _State.BracketArgumentOpen:
            # Existing:  \[=*
            # =             ->  increment __open_block_length
            # [             ->  BracketArgumentContent
            # other         ->  Error
            if curr == '=':
                self._push()
                self.__open_block_length += 1
            elif curr == '[':
                self._push()
                self._state = _State.BracketArgumentContent
            else:
                self._error()
        elif self._state == _State.BracketArgumentContent:
            # Existing: \[={len}\].*
            # ]             ->  BracketArgumentContent
            # other         ->  append to _orig_text
            if curr == '=':
                self._push()
                self.__open_block_length += 1
            elif curr == ']':
                self._push()
                self.__close_block_length = 0
                self._state = _State.BracketArgumentClose
            else:
                self._push()
        elif self._state == _State.BracketArgumentClose:
            # Existing: \[={len}\].*\[=*
            # =             ->  increment __close_block_length
            # ] (same len)  ->  Start
            #                   _emit BracketArgument
            # other         ->  BracketArgumentContent
            if curr == '=':
                self._push()
                self.__close_block_length += 1
            elif curr == ']' and \
                    self.__close_block_length == self.__open_block_length:
                self._push()
                self._state = _State.Start
                return self._emit(tok.BracketArgument)
            else:
                self._push()
                self._state = _State.BracketArgumentContent
        elif self._state == _State.QuotedArgument:
            # Existing: ".*
            # \             ->  QuotedArgumentBackslash
            # "             ->  Start
            #                   _emit QuotedArgument
            # other         ->  (append character)
            if curr == '\\':
                self._push()
                self._state = _State.QuotedArgumentBackslash
            elif curr == '"':
                self._push()
                self._state = _State.Start
                return self._emit(tok.QuotedArgument)
            else:
                self._push()
        elif self._state == _State.QuotedArgumentBackslash:
            # Existing: ".*\\
            # \n            ->  QuotedArgument
            # t r n ;       ->  QuotedArgument
            # A-Za-z0-9;    ->  QuotedArgument
            # other         ->  Error
            if curr == '\n':
                self._push()
                self._state = _State.QuotedArgument
            elif curr in 'trn;':
                self._push()
                self._state = _State.QuotedArgument
            elif self.__class__.__REGEX__.match(curr):
                self._push()
                self._state = _State.QuotedArgument
            else:
                self._error()
        elif self._state == _State.UnquotedArgument:
            # Existing: any chars except '()#"\'
            # \             ->  UnquotedArgumentEscape
            # ()#" ' ' \t   ->  Start
            #                   _next, don't _push
            #                   _emit UnquotedArgument
            if curr == '\\':
                self._push()
                self._state = _State.UnquotedArgumentEscape
            elif is_whitespace(curr) or \
                    (curr and curr in '()#"'):
                self._state = _State.Start
                return self._emit(tok.UnquotedArgument)
            else:
                self._push()
        elif self._state == _State.UnquotedArgumentEscape:
            # Existing: any chars except '()#"\' plus a trailing '\'
            # t r n ; ' '   ->  UnquotedArgument
            # other         ->  Error
            if curr and curr in 'trn; ':
                self._push()
                self._state = _State.UnquotedArgument
            else:
                self._error()
