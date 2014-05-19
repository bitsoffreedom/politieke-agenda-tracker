import os
import sys
sys.stdout = sys.stderr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")))

import atexit
import threading
import cherrypy

cherrypy.config.update({'environment': 'embedded'})

if cherrypy.__version__.startswith('3.0') and cherrypy.engine.state == 0:
    cherrypy.engine.start(blocking=False)
    atexit.register(cherrypy.engine.stop)
    
from bof.politiekeagenda.main import Root, url_config

application = cherrypy.Application(Root(), script_name=None, config=url_config)
