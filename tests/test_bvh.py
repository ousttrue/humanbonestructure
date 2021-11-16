import unittest
import bvh
import pathlib
import os

TEST_DATA = pathlib.Path(os.environ['USERPROFILE']) / 'Desktop/test_motion.bvh'


class Test_BVH(unittest.TestCase):
    def test_parse(self):
        root, frametime, frames, data = bvh.parse(
            TEST_DATA.read_text(encoding='utf-8'))
        self.assertEqual('Hips', root.name)
        self.assertEqual('Spine', root.children[0].name)
        self.assertEqual(0.008333, frametime)
        self.assertEqual(4007, frames)
        self.assertEqual(len(data), frames * root.get_channel_count())


if __name__ == '__main__':
    unittest.main()
