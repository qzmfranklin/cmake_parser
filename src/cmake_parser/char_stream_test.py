# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import io
import unittest

import char_stream


class TestCharStream(unittest.TestCase):

    def test_unsupported_ops(self):
        string = 'foo'
        g = char_stream.CharStream(io.StringIO(string))

        ops = [
            '__iter__',
            'flush',
            'readline',
            'readlines',
            'seek',
            'tell',
        ]
        for op in ops:
            method = getattr(g, op)
            with self.assertRaises(io.UnsupportedOperation):
                method()

        with self.assertRaises(io.UnsupportedOperation):
            g.writelines([])

    def test_is_eof(self):
        string = 'foo'
        g = char_stream.CharStream(io.StringIO(string))
        # pylint: disable=unused-variable
        for i in range(len(string) + 2):
            self.assertFalse(g.is_eof())
        for i in range(len(string)):
            next(g)
        # pylint: enable=unused-variable
        self.assertTrue(g.is_eof())

    def test_curr(self):
        string = 'foo'
        g = char_stream.CharStream(io.StringIO(string))
        for ch in string:
            self.assertEqual(g.curr(), ch)
            self.assertEqual(next(g), ch)
        self.assertIsNone(g.curr())


if __name__ == '__main__':
    unittest.main()
