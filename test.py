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
        doc_re = re.compile(r'\<\!ENTITY version "(\S+)"\>')

        m = doc_re.search(doc)
        self.failUnless(m,"doc doesn't specify version")
        self.assertEqual(gnofract4d.version,m.group(1), "Version mismatch")

    def testOptionsVersionMatches(self):
        from fract4d import options
        self.assertEqual(gnofract4d.version,options.version)

    def testDesktopFileVersionMatches(self):
        dtop = open("gnofract4d.desktop").read()
        dtop_re  = re.compile("Version=(\S+)")
        m = dtop_re.search(dtop)
        self.failUnless(m,"Desktop file doesn't specify version")
        self.assertEqual(gnofract4d.version,m.group(1), "Version mismatch")

    def testWebsiteVersionMatches(self):
        if not os.path.exists("website"):
            # not included in source dist
            return
        mkweb = open("website/mkweb.py").read()
        ver_re = re.compile(r'text="Version (\S+) released.')

        m = ver_re.search(mkweb)
        self.failUnless(m,"doc doesn't specify version")
        self.assertEqual(gnofract4d.version,m.group(1), "Version mismatch")

    def testGenerateMandelbrot(self):
        if os.path.exists("test.png"):
            os.remove("test.png")
        try:
            gnofract4d.main(["-s", "test.png", "--width", "24", "-j", "12", "-q"])
            self.failUnless(os.path.exists("test.png"))
        finally:
            if os.path.exists("test.png"):
                os.remove("test.png")
            

    def testVersionChecks(self):
        self.assertEqual(True, gnofract4d.test_version(2,6,0))
        self.assertEqual(True, gnofract4d.test_version(2,7,0))
        self.assertEqual(True, gnofract4d.test_version(3,0,0))
        
        self.assertEqual(False, gnofract4d.test_version(1,99,0))
        self.assertEqual(False, gnofract4d.test_version(2,0,0))
        self.assertEqual(False, gnofract4d.test_version(2,5,0))
    
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

