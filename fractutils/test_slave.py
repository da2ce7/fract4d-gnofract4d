#!/usr/bin/env python

# check that running a slow out-of-proc piece of code in a cancellable way works

import unittest
import select
import sys

import gtk

import slave

class GTKTestSlave(slave.GTKSlave):
    def __init__(self, cmd, *args):        
        slave.GTKSlave.__init__(self,cmd,*args)
        self.complete = False

    def on_complete(self):
        slave.GTKSlave.on_complete(self)

        self.complete = True
        gtk.main_quit()

    def on_writable(self,source,condition):
        slave.GTKSlave.on_writable(self,source,condition)
        
        progress = 1.0 * self.in_pos / (len(self.input)+1)
        self.bar.set_text("Writing %.2f" % progress)
        self.bar.set_fraction(progress)
        return True

    def on_readable(self,source,condition):
        slave.GTKSlave.on_readable(self,source,condition)
        
        self.bar.set_text("Reading")
        self.bar.pulse()
        return True
    
    def run(self,input):
        slave.GTKSlave.run(self,input)

        window = gtk.Window()
        self.bar = gtk.ProgressBar()
        window.add(self.bar)
        window.show_all()
        gtk.main()
        
class Test(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def runProcess(self,input,wait_time):
        s = slave.Slave("./stub_subprocess.py", str(wait_time))

        s.run(input)
        return s
    
    def sendInput(self,s,n=sys.maxint):
        while n > 0:
            (r,w,e) = select.select([],[s.stdin],[],0.01)
            if len(w) == 0:
                continue
            
            if not s.write():
                break

            n -= 1
        #print "done with input"

    def readOutput(self,s):
        bytes_read = 0
        while 1:
            (r,w,e) = select.select([s.stdout],[],[],0.01)
            if len(r) == 0:
                continue
            
            if not s.read():
                break

    def testTerminate(self):
        s = self.runProcess("y" * 200, 2.0)
        self.sendInput(s,1)
        s.terminate()
        self.assertEqual(False, s.write())
        self.assertEqual(False, s.read())
        
    def testRun(self):
        input = "x" * (100 * 1000)
        s = self.runProcess(input, 0.001)
        self.sendInput(s)
        self.readOutput(s)
        self.assertEqual(input, s.output)

    def testRegister(self):
        s = GTKTestSlave("./stub_subprocess.py", str(0.01))

        input = "x" * (100 * 1000)
        s.run(input)
        self.assertEqual(input, s.output)
        self.failUnless(s.complete, "operation didn't complete")
        
    def testGet(self):
        s = GTKTestSlave("./get.py", "GET", "http://www.google.com/index.html" )
        s.run("")
        self.failUnless(s.output.count("oogle") > 0)
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')



