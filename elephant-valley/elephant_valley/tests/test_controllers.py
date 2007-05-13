import turbogears
from nose import with_setup
from turbogears import testutil, database

database.set_db_uri("sqlite:///:memory:")

from elephant_valley import model
from elephant_valley.controllers import Root

import cherrypy

model.ensureTables()
model.addTestData()

def teardown_func():
    """Tests for apps using identity need to stop CP/TG after each test to
    stop the VisitManager thread. See http://trac.turbogears.org/turbogears/ticket/1217
    for details.
    """
    turbogears.startup.stopTurboGears()

cherrypy.root = Root()

def test_get_fractals():
    fractals = cherrypy.root.get_fractals()
    val = [x.title for x in fractals]
    assert ['a', 'b', "bert's fractal" ] == val, "unexpected list of fractals %s" % val
    
def test_index_method():
    "the index method should return a string called now"
    import types
    result = testutil.call(cherrypy.root.index)
    assert type(result["now"]) == types.StringType
    assert result.get("fractal_titles") != None

    titles = result.get("fractal_titles")
    assert titles.count("a") == 1, "wibble not found in %s" % titles
    
test_index_method = with_setup(teardown=teardown_func)(test_index_method)

def test_indextitle():
    "The indexpage should have the right title"
    testutil.createRequest("/")
    assert cherrypy.response.status == "200 OK", cherrypy.response.status
    assert "<title>Elephant Valley: A Fractal Gallery</title>" in cherrypy.response.body[0]
test_indextitle = with_setup(teardown=teardown_func)(test_indextitle)

def test_more():
    testutil.createRequest("/more")
    assert cherrypy.response.status == "200 OK", cherrypy.response.status
    assert "<title>About Elephant Valley</title>" in cherrypy.response.body[0]
test_more = with_setup(teardown=teardown_func)(test_more)

def test_logintitle():
    "login page should have the right title"
    testutil.createRequest("/login")
    assert "<title>Login</title>" in cherrypy.response.body[0]
test_logintitle = with_setup(teardown=teardown_func)(test_logintitle)
