'''Readonly character stream with 1-character lookahead.
'''

import io


class CharStream(io.IOBase):
    # pylint: disable=too-many-public-methods
    # pylint: disable=missing-docstring
    '''Readonly character stream with single character lookup ahead.
    '''

    def __init__(self, stream):  # pylint: disable=super-init-not-called
        if not isinstance(stream, io.IOBase):
            raise TypeError(stream, 'is not an instance of io.IOBase.')
        if not stream.readable():
            raise TypeError(stream, 'is not readable.')
        self._stream = stream
        self._buffer = ''

    def curr(self):
        '''Peek the current character without moving the stream.

        If it already reached the EOF, None is returned.
        '''
        if not self._buffer:
            try:
                self._buffer = next(self._stream)
                return self._buffer[0]
            except StopIteration:
                return
        if self._buffer:
            return self._buffer[0]

    def is_eof(self):
        '''Check if the stream has been exhausted.

        May conditionally read one symbol into buffer.
        '''
        if self._buffer:
            return False
        try:
            self._buffer = next(self._stream)
            return False
        except StopIteration:
            return True

    def __next__(self):
        if self._buffer:
            char = self._buffer[0]
            self._buffer = self._buffer[1:]
            return char
        return next(self._stream)

    def close(self):
        self._stream.close()

    def closed(self):
        return self._stream.closed()

    def isatty(self):
        return False

    def seekable(self):
        return False

    def writable(self):
        return False

    def readable(self):
        return True

    def __enter__(self):
        raise io.UnsupportedOperation

    def __exit__(self, *unused_args):
        raise io.UnsupportedOperation

    def __iter__(self):
        raise io.UnsupportedOperation

    def flush(self):
        raise io.UnsupportedOperation

    def readline(self):
        raise io.UnsupportedOperation

    def readlines(self):
        raise io.UnsupportedOperation

    def tell(self):
        raise io.UnsupportedOperation

    def writelines(self, unused_lines):  # pylint: disable=unused-argument
        raise io.UnsupportedOperation
