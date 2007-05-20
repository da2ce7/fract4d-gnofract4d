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

class TestWithTemplates(object):
    def check_basic_response(self,expected="200 OK"):
        assert cherrypy.response.status == expected, cherrypy.response.status

    def check_for_string(self,s):
        print cherrypy.response.body[0]
        assert s in cherrypy.response.body[0], "'%s' not in response" % s
        
    def test_index(self):
        testutil.createRequest("/")
        self.check_basic_response()
        self.check_for_string("<title>Elephant Valley: A Fractal Gallery</title>")

    def test_more(self):
        testutil.createRequest("/more")
        self.check_basic_response()
        self.check_for_string("<title>About Elephant Valley</title>")

    def test_logintitle(self):
        testutil.createRequest("/login")
        self.check_for_string("<title>Login</title>")
        
    #test_logintitle = with_setup(teardown=teardown_func)(test_logintitle)

    def test_fractals(self):
        testutil.createRequest("/fractals/bert")
        self.check_basic_response()
        self.check_for_string("<title>Fractals by bert</title>")
        self.check_for_string("bert's fractal")

        testutil.createRequest("/fractals/fred")
        self.check_basic_response()
        self.check_for_string("<title>Fractals by fred</title>")

    
