# a module for handling interaction with the Flickr photo-sharing service

import os
import urllib, urllib2, urlparse, mimetools, mimetypes
import xml.dom.minidom
import md5

API_KEY="f29c6d8fa5d950131c4ae13adc55700d"
SECRET="037ec6eec0e91cab"

BASE_URL="http://www.flickr.com/services/rest/"
AUTH_URL="http://www.flickr.com/services/auth/"
UPLOAD_URL="http://www.flickr.com/services/upload/"

GF4D_GROUP="46555832@N00"

class FlickrError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

def parseResponse(resp):
    dom = xml.dom.minidom.parseString(resp)
    if dom.documentElement.nodeName != "rsp":
        raise FlickrError("Unexpected response: %s" % resp)

    if dom.documentElement.getAttribute("stat") != "ok":
        # error encountered
        err = dom.getElementsByTagName("err")[0]
        code = err.getAttribute("code")
        msg = err.getAttribute("msg")
        raise FlickrError("Error returned: %s [%s]" % (msg,code))
    return dom

def makeCall(url,**kwds):
    query = urllib.urlencode(kwds)
    url = "%s?%s" % (url, query)
    req = urllib2.Request(url)
    resp = urllib2.urlopen(req).read()
    #print resp
    dom = parseResponse(resp)
    return dom

def makeSignedCall(url,**kwds):
    sig = createSig(**kwds)
    kwds["api_sig"] = sig
    return makeCall(url,**kwds)

def getSignedUrl(url,**kwds):
    sig = createSig(**kwds)
    kwds["api_sig"] = sig
    query = urllib.urlencode(kwds)
    url = "%s?%s" % (url, query)
    return url

def createSig(**kwds):
    keys = kwds.keys()
    keys.sort()
    siglist = [ SECRET ]
    for k in keys:
        item = kwds[k]
        siglist.append(k)
        siglist.append(item)
    sig = "".join(siglist)
    hash =  md5.new(sig)
    digest = hash.hexdigest()
    return digest

def getFrob():
    resp = makeSignedCall(BASE_URL,api_key=API_KEY,method="flickr.auth.getFrob")
    return resp.getElementsByTagName("frob")[0].firstChild.nodeValue

def getAuthUrl(frob_):
    return getSignedUrl(AUTH_URL,api_key=API_KEY,perms="write",frob=frob_)

def getToken(frob_):
    resp = makeSignedCall(BASE_URL,method="flickr.auth.getToken",api_key=API_KEY,frob=frob_)
    token = Token(resp)
    return token

def checkToken(token):
    # we'll throw an exception if token is invalid
    resp = makeCall(BASE_URL,method="flickr.auth.checkToken",api_key=API_KEY,auth_token=token)
    return Token(resp)

def upload(photo,token,**kwds):
    kwds["api_key"]=API_KEY
    kwds["auth_token"]=token
    sig = createSig(**kwds)
    kwds["api_sig"] = sig
    files = [("photo",os.path.basename(photo),open(photo).read())]
    req = build_request(UPLOAD_URL,kwds,files)

    resp = urllib2.urlopen(req).read()
    xml = parseResponse(resp)
    photoid = xml.getElementsByTagName("photoid")[0].firstChild.nodeValue
    return photoid

def groups_search(query):
    resp = makeCall(BASE_URL,api_key=API_KEY,method="flickr.groups.search",text=query)
    groups = [ Group(x) for x in resp.getElementsByTagName("group")]
    return groups

def people_getPublicGroups(nsid):
    resp = makeCall(BASE_URL,api_key=API_KEY,method="flickr.people.getPublicGroups",user_id=nsid)
    groups = [ Group(x) for x in resp.getElementsByTagName("group")]
    return groups
    
class Token:
    def __init__(self,resp):
        self.token = resp.getElementsByTagName("token")[0].firstChild.nodeValue
        self.user = User(resp.getElementsByTagName("user")[0])
        
class User:
    def __init__(self,element):
        self.nsid = element.getAttribute("nsid")
        self.username = element.getAttribute("username")
        self.fullname = element.getAttribute("fullname")
        
class Group:
    def __init__(self,element):
        self.nsid = element.getAttribute("nsid")
        self.name = element.getAttribute("name")
    
# This code is from www.voidspace.org.uk/atlantibots/pythonutils.html
def encode_multipart_formdata(fields, files, BOUNDARY = '-----'+mimetools.choose_boundary()+'-----'):
    """ Encodes fields and files for uploading.
    fields is a sequence of (name, value) elements for regular form fields - or a dictionary.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files.
    Return (content_type, body) ready for urllib2.Request instance
    You can optionally pass in a boundary string to use or we'll let mimetools provide one.
    """    
    CRLF = '\r\n'
    L = []
    if isinstance(fields, dict):
        fields = fields.items()
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        filetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % filetype)
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY        # XXX what if no files are encoded
    return content_type, body

def build_request(theurl, fields, files, txheaders=None):
    """Given the fields to set and the files to encode it returns a fully formed urllib2.Request object.
    You can optionally pass in additional headers to encode into the object.
    (Content-type and Content-length will be overridden if they are set).
    fields is a sequence of (name, value) elements for regular form fields - or a dictionary.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files.    
    """
    content_type, body = encode_multipart_formdata(fields, files)
    if not txheaders: txheaders = {}
    txheaders['Content-type'] = content_type
    txheaders['Content-length'] = str(len(body))
    return urllib2.Request(theurl, body, txheaders)