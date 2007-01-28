#!/usr/bin/env python

# test types which are used by formula authors

import fracttypes
import unittest

class Test(unittest.TestCase):
    def testTypeCtor(self):
        c = fracttypes.Type(
            id=72,
            suffix="i", printf="%d", typename="int",
            default=0, slots=1, cname="int")

        self.assertEqual("i",c.suffix)

    def testTypes(self):
        self.assertEqual(
            "bool",
            fracttypes.typeObjectList[fracttypes.Bool].typename)

        self.assertEqual(
            "int",
            fracttypes.typeObjectList[fracttypes.Int].typename)

        self.assertEqual(
            "float",
            fracttypes.typeObjectList[fracttypes.Float].typename)

        self.assertEqual(
            "complex",
            fracttypes.typeObjectList[fracttypes.Complex].typename)

        self.assertEqual(
            "color",
            fracttypes.typeObjectList[fracttypes.Color].typename)

        self.assertEqual(
            "string",
            fracttypes.typeObjectList[fracttypes.String].typename)

        self.assertEqual(
            "hyper",
            fracttypes.typeObjectList[fracttypes.Hyper].typename)

        self.assertEqual(
            "gradient",
            fracttypes.typeObjectList[fracttypes.Gradient].typename)

    def testTypeIDs(self):
        for i in xrange(len(fracttypes.typeObjectList)):
            self.assertEqual(i,fracttypes.typeObjectList[i].typeid)
            
    def testPrintfOfType(self):
        self.assertEqual(
            "%d", fracttypes.typeObjectList[fracttypes.Bool].printf)
        self.assertEqual(
            "%d", fracttypes.typeObjectList[fracttypes.Int].printf)
        self.assertEqual(
            "%g", fracttypes.typeObjectList[fracttypes.Float].printf)
        self.assertEqual(
            None, fracttypes.typeObjectList[fracttypes.String].printf)

    def testCType(self):
        expected =  {
            fracttypes.Int : "int",
            fracttypes.Float : "double",
            fracttypes.Complex : "double",
            fracttypes.Hyper : "double",
            fracttypes.Bool : "int",
            fracttypes.Color : "double",
            fracttypes.String : "<Error>",
            fracttypes.Gradient : "void *"
            }

        for (k,v) in expected.items():            
            self.assertEqual(v,fracttypes.typeObjectList[k].cname)
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

