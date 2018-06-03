'''Streamline the generation of files from templates.
'''

import os
import pathlib

import jinja2
from jinja2.ext import Extension  # pylint: disable=unused-import

from src.base.python import util

ROOT_DIR = util.get_workspace()


class _InTemplateError(jinja2.ext.Extension):
    '''Allow templates to use the 'raise' keyword to throw error.

    Taken from:
        https://stackoverflow.com/questions/21778252/how-to-raise-an-exception-in-a-jinja2-macro
    '''

    # This is our keyword(s):
    tags = set(['raise'])

    # See also: jinja2.parser.parse_include()
    def parse(self, parser):
        # the first token is the token that started the tag. In our case we
        # only listen to "raise" so this will be a name token with
        # "raise" as value. We get the line number so that we can give
        # that line number to the nodes we insert.
        lineno = next(parser.stream).lineno

        # Extract the message from the template
        message_node = parser.parse_expression()

        return jinja2.nodes.CallBlock(
            self.call_method('_raise', [message_node], lineno=lineno), [], [],
            [],
            lineno=lineno
        )

    def _raise(self, msg, unused_caller):
        # pylint: disable=unused-argument
        # pylint: disable=no-self-use
        '''Raise the exception when filling the template.
        '''
        raise jinja2.exceptions.TemplateRuntimeError(msg)


# pylint: disable=redefined-outer-name
def template(input_template, default_output_paths=[]):  # pylint: disable=dangerous-default-value
    '''Decorator function that helps generate file from jinja2 template.


    :param input_template: The path to the jinja2 template file.
    :type input_template: str or pathlib.Path.
    :param default_output_paths: The path to the default output file.  The
        default value, empty list, directs the generated function to use the
        @input_template's filename with the extension .j2 or .in stripped as the
        default output file path.  This is a list because in some cases we want
        to produce multiple identical copies of the generated file.
    :type default_output_paths: A list of str or pathlib.Path.  Mixed types are
        OK.
    :return: A configure function.  See the full explanation in the `Example`
        section.
    :rtype: A function.

    :raises:
        ValueError: The template filename does not have a valid extension name.
        FileNotFoundError: The template file does not exist.

    :Example:

        # STEP 1  Define the generation function.
        @template('settings.py.j2')
        def generate_build():
            return { 'redis': { 'url': 'localhost', 'port': 16379 } }

        # STEP 2  The contentt of the settings.py.j2 file.
        {{ redis.url }}:{{ redis.port }}

        # STEP 3  Call the generation function.
        generate_build()

        # RESTFUL  Generated file content.
        localhost:16379

        # You may also generate multiple identical copies from a single template
        # file.  There are two ways to do that:

        # Method 1: Use the decorator to define the default list.
        @template('settings.py.j2', ['path/to/foo1', 'path/to/foo2'])
        def generate_build():
            return { 'redis': { 'url': 'localhost', 'port': 16379 } }
        generate_build()

        # Method 2: Call the decorated function with a list of paths.
        generate_build(['path/to/foo3'])


    More information is documented inside the __doc__ string of the
    __inner_func__.
    '''
    ipath = pathlib.Path(input_template).resolve()
    allowed_exts = ['.j2', '.in']
    if ipath.suffix not in allowed_exts:
        raise ValueError(
            'Template filename must end one of %s' % allowed_exts, ipath
        )
    # pylint: disable=no-member
    if not ipath.is_file():
        raise FileNotFoundError('Cannot find template file:', ipath)

    def __func__(func):
        cwd = os.getcwd()
        parent_dir = ipath.parent

        if default_output_paths:
            default_opaths = default_output_paths
        else:
            default_opaths = [parent_dir / ipath.stem]

        def __inner_func__(
            ofiles=default_opaths, *, dry_run=False, verbose=False
        ):  # pylint: disable=dangerous-default-value
            '''
            :param ofiles: The output filenames.  The generated file is copied
                to all files in this list.  The default value of this list is
                determined by the `default_output_paths` parameter in the
                template() function.
            :type ofiles: A list of str or pathlib.Path.  Mixed types are OK.

            :param dry_run: If True, only print what file will be generated from
                which template instead of generating the file.  The default
                value is False.
            :type dry_run: bool.

            :param verbose: If True, show the __configure_*__.py files and the
                template files for each generated file.  This is most useful for
                inspection and debugging.
            :type verbose: bool.
            '''
            j2_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader([str(parent_dir)]),
                extensions=[_InTemplateError]
            )
            template = j2_env.get_template(ipath.name)
            data = func()
            content = template.render(data)

            for opath in ofiles:
                if not dry_run:
                    with open(str(opath), 'w') as f:  # pylint: disable=invalid-name
                        f.write(content)
                if verbose:
                    print(
                        ' ' * 8, opath.relative_to(ROOT_DIR), '<===',
                        ipath.relative_to(ROOT_DIR)
                    )
                else:
                    print(opath.relative_to(cwd))

            return content

        __inner_func__.__configure__ = True

        return __inner_func__

    return __func__


def is_configure(func):
    '''Check whether a function is a configure function.
    '''
    return hasattr(func, '__configure__') and func.__configure__ is True
