#!/usr/bin/env python

# unit tests for flickr api

import unittest
import copy
import sys

import flickr

sys.path.append("..") #FIXME

# don't want to tell the world this token, so it's kept in this
# non-checked-in file. User needs to create it initially
try:
    TOKEN = open("token.txt").read().strip()
except IOError, err:
    frob = flickr.getFrob()
    url = flickr.getAuthUrl(frob)
    print """
You need to get an authorization token to allow Gnofract 4D to access your Flickr account.
Click on the URL below and follow the instructions, then close the browser window and press ENTER.

"""
    print url
    sys.stdin.readline()
    token = flickr.getToken(frob)
    print "token",token
    open("token.txt","w").write(token.token)    

class Test(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def testEcho(self):
        resp = flickr.makeCall(
            "http://www.flickr.com/services/rest/",
            method="flickr.test.echo",
            name="hello",
            api_key=flickr.API_KEY)

        self.assertSuccessfulRest(resp)
        self.assertEqual(resp.getElementsByTagName("name")[0].firstChild.nodeValue,"hello")

    def testToken(self):
        t = flickr.checkToken(TOKEN)
        user = t.user
        self.assertNotEqual(user.username,"")
        self.assertNotEqual(user.nsid,"")

    def disabled_testUpload(self):
        id = flickr.upload(
            "../pixmaps/gnofract4d-logo.png",
            TOKEN,
            title="Burning Bush",
            description="test image of exceptional ugliness")

    def testGetGnofract4DGroup(self):
        groups = flickr.groups_search("gnofract 4d")

        found = False
        for g in groups:
            if g.name == "Gnofract 4D":
                self.assertEqual(g.nsid,flickr.GF4D_GROUP)
                found = True
        self.failUnless(found)

    def testGroupMembership(self):
        user = flickr.checkToken(TOKEN).user
        nsid = user.nsid
        groups = flickr.people_getPublicGroups(nsid)
        gf4d = [g for g in groups if g.nsid == flickr.GF4D_GROUP]
        if len(gf4d) == 0:
            # current user is not a member of gf4d group
            print "\nYou're not a member of the Gnofract 4D group. You should join!"

    def assertWellFormedRest(self, resp):        
        docNode = resp.documentElement
        self.assertEqual(docNode.nodeName,"rsp")

    def assertSuccessfulRest(self,resp):
        self.assertWellFormedRest(resp)
        docNode = resp.documentElement
        self.assertEqual(docNode.getAttribute("stat"),"ok")
        

    
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')



