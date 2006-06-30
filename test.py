#!/usr/bin/env python

# run all the tests
import os
import sys
import unittest
import re
import getopt

try:
    # a hack, but seems easy enough
    os.system("cp gnofract4d gnofract4d.py")    
    import gnofract4d
finally:
    os.remove("gnofract4d.py")

print "Running all unit tests. This may take several minutes."

class Test(unittest.TestCase):
    def testSetupCfgVersionMatches(self):
        "Check that the version number in the main script matches the one in the setup.cfg file"
        cfg = open("setup.cfg").read()
        lib_re = re.compile(r'install_lib\s*=\s*(\S+)')
        m = lib_re.search(cfg)
        self.failUnless(m,"Config file doesn't specify install_lib")
        libdir = m.group(1)

        v = gnofract4d.version
        self.assertEqual("/usr/lib/gnofract4d-%s" % gnofract4d.version, libdir, "Version mismatch")

    def testSetupPyVersionMatches(self):
        setup = open("setup.py").read()
        setup_re = re.compile(r'gnofract4d_version\s*=\s*"(\S+)"')
        m = setup_re.search(setup)
        self.failUnless(m,"setup.py doesn't specify version")
        self.assertEqual(gnofract4d.version,m.group(1), "Version mismatch")

    def testDocVersionMatches(self):        
        # check the docs
        doc = open("doc/gnofract4d-manual/C/gnofract4d-manual.xml").read()
        doc_re = re.compile(r'This is &gf4d; version (\S+)\.')

        m = doc_re.search(doc)
        self.failUnless(m,"doc doesn't specify version")
        self.assertEqual(gnofract4d.version,m.group(1), "Version mismatch")

    def testBadOptions(self):
        self.assertRaises(getopt.GetoptError, gnofract4d.Options,["--fish"])

    def testOptions(self):
        o = gnofract4d.Options(
            ["-h"])
        self.assertEqual(1, o.output.count("To generate an image"))
        self.assertEqual(True, o.quit_now)

        o = gnofract4d.Options(
            ["-P", "foo", "-f", "bar/baz.frm#wibble"])

        self.assertEqual(["foo","bar"],o.extra_paths)
        self.assertEqual("baz.frm",o.basename)
        self.assertEqual("wibble",o.func)

        o = gnofract4d.Options(
            ["-i", "780", "-j", "445"])

        self.assertEqual(780, o.width)
        self.assertEqual(445, o.height)

        o = gnofract4d.Options(
            ["--params", "foo"])

        self.assertEqual(["foo"], o.args)
        
def suite():
    return unittest.makeSuite(Test,'test')

def main():        
    os.chdir('fract4d')
    os.system('./test.py')
    os.chdir('../fract4dgui')
    os.system('./test.py')
    os.chdir('../fractutils')
    os.system('./test.py')
    os.chdir('..')

    unittest.main(defaultTest='suite')

    
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "--thisonly":
        sys.argv.remove("--thisonly")
        unittest.main(defaultTest='suite')
    else:
        main()

