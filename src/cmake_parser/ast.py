'''Syntactically parse the stream of tokens.

Construct the Abstract Syntax Tree.
'''

import abc
import enum

import lexer


class AstNode(metaclass=abc.ABCMeta):
    '''Ast Node in cmake syntax.
    '''


class _State(enum.Enum):
    '''Internal state of the parser.
    '''

    Start = 0

    End = -1


class AstParser(object):
    '''Parse lexical tokens into an AST.
    '''

    def __init__(self, lexer):
        self._lexer = lexer

    def parse():
        '''Parse the tokens into AST.

        :return: The root AstNode.
        '''
