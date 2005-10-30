#!/usr/bin/env python

# a minimal script to fetch a web page. We execute this in a separate process
# so we can cancel flickr requests if they take too long or go wrong

# usage: get.py [-P content-type ] url
# if -P, this is a POST, read postdata from stdin
# url should already be encoded

# try to keep the import set minimal so it starts quickly
import sys
import urllib2

if len(sys.argv)<2:
    print "bad args"
    sys.exit(-1)

if sys.argv[1]=="-P":
    is_post = True
    content_type = sys.argv[2]
    url = sys.argv[3]
else:
    is_post = False
    url = sys.argv[1]

txheaders = {}
data = None

if is_post:
    data = sys.stdin.read()
    txheaders['Content-type'] = content_type
    txheaders['Content-length'] = str(len(data))

req = urllib2.Request(url,data,txheaders)
resp = urllib2.urlopen(req).read()
print resp
