import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")))

import cherrypy

import time
from datetime import datetime, timedelta

import models
import database

from config import *

from helpers import *

cherrypy.config.update({ 'server.socket_port': 3017 })
cherrypy.request.base = 'https://politiekeagenda.bof.nl'

url_config = {
    # Use the default dispatcher unless otherwise defined
    '/': {
        'request.dispatch': cherrypy.dispatch.Dispatcher(),
        #~ 'tools.encode.on': True,
        #~ 'tools.encode.encoding': 'utf8', 
        'tools.staticdir.on' : True,
        'tools.staticdir.dir' : os.path.join(root_directory, "static")
    }
}

class Root:
    
    @cherrypy.expose
    def index(self):
        cherrypy.request.base = 'https://politiekeagenda.bof.nl'
        session = database.Session()
            
        assemblies = (session.query(models.Assembly)
            .join((models.Revision, models.Revision.revision_id==models.Assembly.latest_revision_id))
            .filter(models.Revision.status==None)
            .filter(models.Revision.date > int(time.mktime((datetime.now() - timedelta(hours=5)).timetuple())))
            .order_by(models.Revision.date.asc())
            .all())
            
        return template_lookup.get_template("assemblies.html").render(
            assemblies=assemblies
        )
    
    @cherrypy.expose
    def track(self, assembly_id):
        cherrypy.request.base = 'https://politiekeagenda.bof.nl'
        session = database.Session()
        assembly = session.query(models.Assembly).filter(models.Assembly.id==assembly_id).one()
        assembly.ignore = 0
        assembly.track = 1
        session.commit()
        
    @cherrypy.expose
    def ignore(self, assembly_id):
        cherrypy.request.base = 'https://politiekeagenda.bof.nl'
        session = database.Session()
        assembly = session.query(models.Assembly).filter(models.Assembly.id==assembly_id).one()
        assembly.track = 0
        assembly.ignore = 1
        session.commit()
    
    @cherrypy.expose
    def clear(self, assembly_id):
        cherrypy.request.base = 'https://politiekeagenda.bof.nl'
        session = database.Session()
        assembly = session.query(models.Assembly).filter(models.Assembly.id==assembly_id).one()
        assembly.ignore = 0
        assembly.track = 0
        session.commit()
    
    @cherrypy.expose
    def config(self):
        cherrypy.request.base = 'https://politiekeagenda.bof.nl'
        session = database.Session()
        keywords = session.query(models.Config).filter(models.Config.key=='keywords').one().value
        return template_lookup.get_template("config.html").render(keywords=keywords) 
    
    @cherrypy.expose
    def save_config(self, **kwargs):
        cherrypy.request.base = 'https://politiekeagenda.bof.nl'
        session = database.Session()
        config = session.query(models.Config).filter(models.Config.key=='keywords').one()
        config.value = kwargs["config.keywords"].decode("utf-8")
        session.commit()
        raise cherrypy.HTTPRedirect(cherrypy.url("/"))

if __name__ == "__main__":
    cherrypy.request.base = 'https://politiekeagenda.bof.nl'
    cherrypy.quickstart(Root(), config=url_config)
