CONST_APP_CONFIG = "chapters_manager_course_config";
CONST_CHAPTER_STATE = "chapters_manager_state";

CourseManager = {
    blockChapterAccess: function() {
        var course = CourseManager.getCourse();

        if (!Syllabus.loggedIn()) {
            console.log("Could not find username, loading default chapters.");
            CourseManager._removeChapterLinks(CourseManager.getBaseChapters());
            return;
        }

        if (!course) {
            console.log("Could not find course in the app config file.");
            CourseManager._removeChapterLinks(CourseManager.getBaseChapters());
            return;
        }

        Inginious.plugins.chapterAccess(course).done(function(data) {

            if (data.code == 200) {
                CourseManager._removeChapterLinks(data.chapters);
                CourseManager._saveChapterState(data.chapters);
            } else {
                console.log(data.code + ": " + data.message);
                CourseManager._removeChapterLinks(CourseManager._getChapterState());
            }

        }).fail(function() {
            
            console.log("Failure of server chapter request. Fallback.");
            CourseManager._removeChapterLinks(CourseManager._getChapterState());

        });
    },
    getCourse: function() {
        var appConfig = Utils.storage.readJSON(CONST_APP_CONFIG);

        return appConfig.course;
    },
    getExercises: function() {
        var appConfig = Utils.storage.readJSON(CONST_APP_CONFIG);
        return [ 'mcq-rel-framing', 'q-rel-delay' , 'q-rel-delay1' ,'mcq-rel-abp', 'q-rel-alt-bit-1' , 'q-rel-alt-bit-2', 'mcq-rel-gbn', 'mcq-rel-sr' , 'q-rel-gbn-max' ];
        return appConfig.exercises;
    },
    getBaseChapters: function() {
        var appConfig = Utils.storage.readJSON(CONST_APP_CONFIG);

        return appConfig.basicChapterConfig;
    },
    _removeChapterLinks: function(chapters) {
        $('[href]').each(function(i, e){
            var $e = $(e);
            var link = $e.attr('href');
        
            if (CourseManager._isChapterLink(link, chapters)) {
                $e.removeAttr('href');
                $e.attr('title', "You must complete the mandatory chapters before accessing this content");
            }
        });
    },
    _isChapterLink: function(link, chapters) {
        for (var i = 0; i < chapters.length; i++) {
            if (chapters[i] == "index") 
                continue;

            var reg = new RegExp(chapters[i] + "\.html?");

            link = Utils.http.prefixLinkWithLocation(link);

            if (link.match(reg)) return true;
        }

        return false;
    },
    
    _saveChapterState: function(chapters) {
        var state = {chapters : chapters};

        Utils.storage.saveJSON(CONST_CHAPTER_STATE, state);
    },

    _getChapterState: function() {
        var state = Utils.storage.readJSON(CONST_CHAPTER_STATE);

        return state.chapters || CourseManager.getBaseChapters();
    }
};