#!/usr/bin/env python

# unit tests for canon module

import unittest
import canon

class CanonTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testEmptyTree(self):
        self.assertEqual(canon.linearize(None),None)

def suite():
    return unittest.makeSuite(CanonTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

