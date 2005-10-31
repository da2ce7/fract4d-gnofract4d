#!/usr/bin/env python

# not a unit test suite for subprocess.py - that's part of python stdlib,
# so I assume it works.

# this is a prototype to check that the process of running a slow out-of-proc
# piece of code in a cancellable way works

import unittest
import copy
import sys
import os

import fcntl
import signal
import select
import errno
import time

import gtk

try:
    import subprocess
except ImportError:
    # this python too old - use our backported copy of stdlib file
    import gf4d_subprocess as subprocess

def makeNonBlocking(fd):
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    try:
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NDELAY)
    except AttributeError:
        import FCNTL
        fcntl.fcntl(fd, FCNTL.F_SETFL, fl | FCNTL.FNDELAY)
        
class Slave(object):
    def __init__(self, cmd, *args):
        self.cmd = cmd
        self.args = list(args)
        self.process = None
        self.input = ""
        self.in_pos = 0
        self.stdin = None
        self.stdout = None
        self.output = ""
        self.dead = False
        self.write_id = None
        self.read_id = None
        
    def run(self, input):
        self.input = input
        self.process = subprocess.Popen(
            [self.cmd, str(len(input))] + self.args,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,close_fds=True)

        makeNonBlocking(self.process.stdin.fileno())
        makeNonBlocking(self.process.stdout.fileno())
        self.stdin = self.process.stdin
        self.stdout = self.process.stdout

    def register(self, on_writable, on_readable):
        self.write_id = gtk.input_add(self.stdin, gtk.gdk.INPUT_WRITE, on_writable)
        self.read_id = gtk.input_add(self.stdout, gtk.gdk.INPUT_READ, on_readable)

    def unregister_write(self):
        if self.write_id:
            #print "unreg write"
            gtk.input_remove(self.write_id)
            self.write_id = None
            
    def unregister_read(self):
        if self.read_id:
            #print "unreg read"
            gtk.input_remove(self.read_id)
            self.read_id = None
            
    def write(self):
        if self.dead:
            self.unregister_write()
            return False
        
        bytes_to_write = min(len(self.input) - self.in_pos,1000)
        if bytes_to_write < 1:
            self.stdin.close()
            self.unregister_write()
            return False

        try:            
            self.stdin.write(
                self.input[self.in_pos:self.in_pos+bytes_to_write])
            #print "wrote %d" % bytes_to_write
        except IOError, err:
            if err.errno == errno.EAGAIN:
                print "again!"
                return True
            raise
        
        self.in_pos += bytes_to_write
        return True

    def read(self):
        if self.dead:
            self.unregister_read()
            return False
        try:
            data = self.stdout.read(-1)
            #print "read", len(data)
            if data == "":
                # checking all these ways to see if child has died
                # since they don't seem to be reliable
                if self.process.poll() == None:
                    #process has quit
                    #print "done"
                    self.unregister_read()
                    return False
                if self.process.returncode != None:
                    #print "returned"
                    self.unregister_read()
                    return False
                if self.stdout.closed:
                    #print "closed"
                    self.unregister_read()
                    return False
        except IOError, err:
            if err.errno == errno.EAGAIN:
                #print "again!"
                return True
            raise
        self.output += data
        return True
    
    def terminate(self):
        try:
            self.dead = True
            os.kill(self.process.pid,signal.SIGKILL)
        except OSError, err:
            if err.errno == errno.ESRCH:
                # already dead
                return
            raise

class SlaveOwner(object):
    def __init__(self, s):
        self.s = s
        
    def on_readable(self, source, condition):
        progress = 1.0 * self.s.in_pos / (len(self.s.input)+1)
        self.bar.set_text("Reading")
        self.bar.pulse()
        
        #print "readable:", source, condition
        if not self.s.read():
            gtk.main_quit()
        return True

    def on_writable(self, source, condition):
        progress = 1.0 * self.s.in_pos / (len(self.s.input)+1)
        self.bar.set_text("Writing %.2f" % progress)
        self.bar.set_fraction(progress)
        #print "writable:",source,condition
        self.s.write()
        return True
    
    def run(self,input):
        self.s.run(input)
        self.s.register(self.on_writable, self.on_readable)

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
        s = Slave("./stub_subprocess.py", str(wait_time))

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
        s = Slave("./stub_subprocess.py", str(0.01))
        so = SlaveOwner(s)

        input = "x" * (100 * 1000)
        so.run(input)
        #self.assertEqual(input, s.output)
        #print "register done"
        
    def testGet(self):
        s = Slave("./get.py", "GET", "http://www.google.com/index.html" )
        so = SlaveOwner(s)
        so.run("")
        self.failUnless(s.output.count("oogle") > 0)
        #print "get done"
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')



