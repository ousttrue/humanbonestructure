import unittest
import bvh
import pathlib
import os

TEST_DATA = pathlib.Path(os.environ['USERPROFILE']) / 'Desktop/test_motion.bvh'


class Test_BVH(unittest.TestCase):
    def test_parse(self):
        bvh.parse(TEST_DATA.read_text(encoding='utf-8'))
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
