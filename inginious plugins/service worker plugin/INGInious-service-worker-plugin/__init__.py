import os
import web
import inginious
from inginious.frontend.pages.utils import INGIniousPage

PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))

class ServiceWorker:

    def GET(self):
        web.header("Access-Control-Allow-Origin", "*")
        web.header("Content-Type", "application/javascript")
        page = open(PATH_TO_PLUGIN + "/ingi-service-worker.js","r")
        return page.read()

    def POST(self):
        return self.GET()

class ServiceWorkerRegistrant:
    
    def GET(self):
        web.header("Access-Control-Allow-Origin", "*")
        web.header("Content-Type", "text/html")
        page = open(PATH_TO_PLUGIN + "/service-worker-registrant.html","r")

        return page.read()

    def POST(self):
        return self.GET()
        


def init (plugin_manager, course_factory, client, plugin_config):
    plugin_manager.add_page('/plugins/INGIniousServiceWorkerRegristrant.html', ServiceWorkerRegistrant)
    plugin_manager.add_page('/ingi-service-worker.js', ServiceWorker)






