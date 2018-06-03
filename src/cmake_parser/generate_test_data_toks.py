#!/usr/bin/env python3
'''Generate test_data/*.toks files.
'''

import glob
import pathlib

import lexer

THIS_DIR = pathlib.Path(__file__).resolve().parent
DATA_DIR = THIS_DIR / 'test_data'

if __name__ == '__main__':
    for src_path in glob.glob(str(DATA_DIR / '*.txt')):
        g = lexer.Tokenizer.from_file(src_path)
        toks_path = src_path[:-len('txt')] + 'toks'
        with open(toks_path, 'w') as f:
            for token in g:
                print(token, file=f)
