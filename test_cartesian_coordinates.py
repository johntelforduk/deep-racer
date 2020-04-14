# A set of tests for the cartesian coordinates functions.

import cartesian_coordinates as cc
import unittest
from math import sqrt


class TestCartesianCoordinates(unittest.TestCase):

    def test_translation(self):
        self.assertEqual(cc.translation([2.0, 3.0], [10.0, 11.0]), [12.0, 14.0])

    def test_scale(self):
        self.assertEqual(cc.scale([2.0, 3.0], 5), [10.0, 15.0])

    def test_rotate_around_origin(self):
        new_position = cc.rotate_around_origin([1.0, 0.0], 90)
        self.assertAlmostEqual(new_position[0], 0.0)                # X
        self.assertAlmostEqual(new_position[1], -1.0)               # Y

        new_position = cc.rotate_around_origin([1.0, 0.0], -45)
        self.assertAlmostEqual(new_position[0], sqrt(2) / 2)        # X
        self.assertAlmostEqual(new_position[1], sqrt(2) / 2)        # Y

    def test_rotate_around_a_point(self):
        self.assertEqual(cc.rotate_around_a_point([2.0, 3.0], [2.0, 2.0], 90.0), [3.0, 2.0])


if __name__ == '__main__':
    unittest.main()
