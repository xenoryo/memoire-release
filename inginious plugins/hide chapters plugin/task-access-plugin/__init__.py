import os
import web
import json
import logging
import inginious.common.base

from .chapterManager import algo 
from inginious.frontend.user_manager import UserManager
from inginious.frontend.pages.utils import INGIniousPage
from inginious.frontend.pages.utils import INGIniousAuthPage

PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))
CHAPTER_CONFIG = "chapterConfig_"
EXERCISE_CONFIG = "exerciseConfig_"

class ChapterManager:

    def __init__(self, page):

        self.page = page
        self.userManager = page.user_manager
        self.courseFactory = page.course_factory

    def getUserManager(self):

        return self.userManager

    def getUnaccessibleChapters(self, username, courseName, passingThreshold):
        chaptersConfig = os.path.abspath(PATH_TO_PLUGIN) + "/" + CHAPTER_CONFIG + courseName + ".yaml"
        exercisesConfig = os.path.abspath(PATH_TO_PLUGIN) + "/" + EXERCISE_CONFIG + courseName + ".yaml"
        course = self.courseFactory.get_course(courseName)
        return algo(self.getUserManager().get_course_cache(username, course), chaptersConfig, exercisesConfig, passingThreshold)

class ChapterAccessApi(INGIniousAuthPage):

    def __init__(self):
        self.page = INGIniousPage()
        self.chapterManager = ChapterManager(self.page)

    def is_lti_page(self):
        return True

    def GET_AUTH(self):
        raise web.notfound()


    def POST_AUTH(self):
        web.header("Access-Control-Allow-Origin", "*")
        web.header("Content-Type", "application/json")
        postData = web.input()
        course = postData.course
        passingThreshold = postData.passingThreshold
        data = self.user_manager.session_lti_info()
        if data is None:
            raise web.notfound()

        inginious_usernames = list(self.database.users.find(
            {"ltibindings." + course + "." + data["consumer_key"]: data["username"]}
        ))

        if not inginious_usernames:
            return { "code": "500", "message": "No LTI session." }

        username = inginious_usernames[0]["username"]
        chaptersConfig = os.path.abspath(PATH_TO_PLUGIN) + "/" + CHAPTER_CONFIG + course + ".yaml"
        empty = []
        if(len(chaptersConfig) > 500):
            return json.dumps({"code": "200", "chapters": empty , "username": username , "course": course})
        try:
            chapters = self.chapterManager.getUnaccessibleChapters(username, course, passingThreshold)
        except:
            return json.dumps({"code": "500", "message": "An error occured while retrieving the chapters. Please contact your administrator."})
        return json.dumps({ "code": "200", "chapters": chapters, "username": username , "course": course})
    

def init (plugin_manager, course_factory, client, plugin_config):

    plugin_manager.add_page('/lti/plugins/chapterAccess/API/chapters/GET', ChapterAccessApi)
