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
    def __init__(self, cmd, args=[]):
        self.cmd = cmd
        self.args = args
        self.process = None
        self.input = ""
        self.in_pos = 0
        self.stdin = None
        self.stdout = None
        self.output = ""
        
    def run(self, input):
        self.input = input
        self.process = subprocess.Popen(
            [self.cmd, str(len(input))] + self.args,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,close_fds=True)

        makeNonBlocking(self.process.stdin.fileno())
        makeNonBlocking(self.process.stdout.fileno())
        self.stdin = self.process.stdin
        self.stdout = self.process.stdout
    
    def write(self):
        bytes_to_write = min(len(self.input) - self.in_pos,1000)
        if bytes_to_write < 1:
            self.stdin.close()
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
        try:
            data = self.stdout.read(-1)
            #print "read", len(data)
            if data == "":
                # checking all these ways to see if child has died
                # since they don't seem to be reliable
                if self.process.poll() == None:
                    #process has quit
                    #print "done"
                    return False
                if self.process.returncode != None:
                    #print "returned"
                    return False
                if self.stdout.closed:
                    print "closed"
                    return False
        except IOError, err:
            if err.errno == errno.EAGAIN:
                print "again!"
                return True
            raise
        self.output += data
        return True
    
    def terminate(self):
        try:
            os.kill(self.process.pid,signal.SIGKILL)
        except OSError, err:
            if err.errno == errno.ESRCH:
                # already dead
                return
            raise
        
class Test(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def runProcess(self,wait_time):
        nchunks = 100
        bytes_per_chunk = 1000
        nbytes = bytes_per_chunk * nchunks

        input = "x" * nbytes
        s = Slave("./stub_subprocess.py")

        s.run(input)
        
        while 1:
            (r,w,e) = select.select([],[s.stdin],[],0.01)
            if len(w) == 0:
                continue
            
            if not s.write():
                break

        #print "done with input"

        bytes_read = 0
        while 1:
            (r,w,e) = select.select([s.stdout],[],[],0.01)
            if len(r) == 0:
                continue
            
            if not s.read():
                break

        self.assertEqual(input, s.output)
        
        s.terminate()
        
    def testRun(self):
        self.runProcess(0.001)
    
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')



