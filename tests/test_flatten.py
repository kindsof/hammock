from __future__ import absolute_import
import unittest

import hammock.cli.flatten as flatten


class TestFlatten(unittest.TestCase):

    def test_flatten(self):

        deep = {
            'a': [{'b': 1}, {'c': {'d': 2}}],
            'e': {'f': 3, 'g': {'h': 4}},
            'i': 5,
        }

        flat = flatten.flatten(deep)

        self.assertDictEqual(
            flat,
            {
                'a.0.b': 1,
                'a.1.c.d': 2,
                'e.f': 3,
                'e.g.h': 4,
                'i': 5,
            }
        )

    def test_empty(self):
        flat = flatten.flatten({})
        self.assertDictEqual(flat, {})

    def test_simple(self):
        deep = {'a': 1}
        flat = flatten.flatten(deep)
        self.assertDictEqual(flat, deep)
