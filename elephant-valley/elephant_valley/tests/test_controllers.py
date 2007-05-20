import turbogears
from nose import with_setup
from turbogears import testutil, database

database.set_db_uri("sqlite:///:memory:")

from elephant_valley import model
from elephant_valley.controllers import Root, Fractals

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

class TestBaseDicts(object):
    def test_get_fractals(self):
        fractals = cherrypy.root.get_fractals()
        val = [x.title for x in fractals]
        assert ['a', 'b', "bert's fractal" ] == val, \
               "unexpected list of fractals %s" % val
    
    def test_index_method(self):
        "the index method should return a string called now"

        result = testutil.call(cherrypy.root.index)
        assert result.get("now") != None
        assert result.get("fractal_titles") != None

        titles = result.get("fractal_titles")
        assert titles.count("a") == 1, "wibble not found in %s" % titles

    def test_fractals_bert(self):
        result = testutil.call(cherrypy.root.fractals.default,uid="bert")

        assert result["user"]=="bert"
        
    
