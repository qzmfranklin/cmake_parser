# pylint: disable=missing-docstring

import pathlib
import sys

from src.base.python import gentemplate

THIS_DIR = pathlib.Path(__file__).resolve().parent
TEMPLATE_PATH = THIS_DIR / 'BUILD.j2'


@gentemplate.template(TEMPLATE_PATH)
def generate_bzl():
    return {'python_interpreter_abspath': sys.executable}
