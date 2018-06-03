'''Additional utilities that complete argparse.
'''

import argparse
import netaddr


# pylint: disable=invalid-name
def ip(s):
    '''
    Convert a string to an netaddr.IPAddress object.

    If the input string cannot be converted to an ip address, return None.
    '''
    try:
        return netaddr.IPAddress(s)
    except netaddr.core.AddrFormatError:
        return


def file(mode, default_file, **file_kwargs):
    '''
    Decorator that generates a function that opens files.

    mode: The mode to use to open the file, e.g., 'r', 'w', etc..
    default_file: If the returned function receives a None or an empty, this
        file-like object is returned by the returned function.
    file_kwargs: Passed on to the open() function.
    return: A function with the following interface:
        def foo(s):
            return FileObject(s)

    Enable very elegant handling of files with argparse parsers.  For example:

        1.  Open file for read, use sys.stdin as default if no argument is
            given:
                >>> parser.add_argument('--input-file', type=file('r',
                    sys.stdin))

        2.  Open file for write, use sys.stdout as default if no argument is
            given:
                >>> parser.add_argument('--input-file', type=file('w',
                    sys.stdout))

        3.  Open file for read, with custom flags, i.e., using UTF-8 encoding:
                >>> parser.add_argument('--input-file',
                        type=file('r', sys.stdin, encoding='utf8'))
    '''

    def __inner_func__(s):
        # pylint: disable=no-else-return
        if not s:
            return default_file
        else:
            return open(s, mode, **file_kwargs)

    return __inner_func__


def key_value_pair(delimiter='=', *, key_only_ok=False):
    '''
    Decorator that generates a function for parsing key-value pairs.

    delimiter: A string, the tokenization delimiter that separates the key from
        the value.  If multiple delimiters are present, only the first is
        treated as the token separator.
    key_only_ok: A boolean.  If True, the generated function will assign None to
        the value if the value is not present in the input.

    CAVEAT:
        Even when key_only_ok is set to True, input string such as 'foo=' are
        considered having an empty string as the value.

    Usage examples:

        1.  Take in the input string using '=' as the delimiter, allowing
            ommitting the value:

                >>> parser.add_argument'--config-item',
                        type=key_value_pair(key_only_ok=True))
    '''

    def __inner_func__(s):
        if not s:
            return {}
        pos = s.find(delimiter)
        if pos == -1:
            if key_only_ok:
                return s, None
            else:
                raise RuntimeError("Invalid key-value pair '%s'." % s)
        else:
            key = s[:pos]
            value = s[pos + len(delimiter):]
            return key, value

    return __inner_func__


class Formatter(argparse.HelpFormatter):
    '''
    Preserve raw description text while adding default value to the help text.

    The help texts are still stripped of whitespace characters.


    Usage:

        Only the name of this class is considered a public API.  All the methods
        provided by the class are considered an implementation detail.

        This class is used in the constructor of argparse.ArgumentParser, for
        example:
            >>> parser = argparse.ArgumentParser(formatter_class=Formatter)
            >>> parser = subparsers.add_parser(formatter_class=Formatter)

    Implementation Detail:
        The implementation is modified from the various formatter classes in the
        argparse.py file shipped with the standard python3 distribution.
    '''

    def _fill_text(self, text, width, indent):
        return ''.join([indent + line for line in text.splitlines(True)])

    # pylint: disable=redefined-builtin
    def _get_help_string(self, action):
        help = action.help
        if '%(default)' not in action.help:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    help += '\n(default: %(default)s)'
        return help
