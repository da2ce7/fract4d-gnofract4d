from turbogears import controllers, expose

import model
from turbogears import identity, redirect
from cherrypy import request, response
# from elephant_valley import json

import logging
log = logging.getLogger("elephant_valley.controllers")

class Root(controllers.RootController):
    @expose(template="elephant_valley.templates.welcome")
    # @identity.require(identity.in_group("admin"))
    def index(self):
        import time
        # log.debug("Happy TurboGears Controller Responding For Duty")
        fractal_titles=[x.title for x in self.get_fractals()] + ["fish"]
        log.debug("titles: %s" % fractal_titles)
        return dict(
            now=time.ctime(),
            image="/static/images/front.jpg",
            fractal_titles=fractal_titles)

    def get_fractals(self):
        return model.Fractal.select()
    
    @expose(template="elephant_valley.templates.login")
    def login(self, forward_url=None, previous_url=None, *args, **kw):
        
        if not identity.current.anonymous \
            and identity.was_login_attempted() \
            and not identity.get_identity_errors():
            raise redirect(forward_url)

        forward_url=None
        previous_url= request.path

        if identity.was_login_attempted():
            msg=_("The credentials you supplied were not correct or "
                   "did not grant access to this resource.")
        elif identity.get_identity_errors():
            msg=_("You must provide your credentials before accessing "
                   "this resource.")
        else:
            msg=_("Please log in.")
            forward_url= request.headers.get("Referer", "/")
            
        response.status=403
        return dict(message=msg, previous_url=previous_url, logging_in=True,
                    original_parameters=request.params,
                    forward_url=forward_url)

    @expose()
    def logout(self):
        identity.current.logout()
        raise redirect("/")

    @expose(template="elephant_valley.templates.more")
    def more(self):
        return dict(image="/static/images/cheby.jpg")
