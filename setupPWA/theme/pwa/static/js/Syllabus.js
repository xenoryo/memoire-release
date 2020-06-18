CONST_APP_CONFIG_URL = "_static/js/appConfig.json";

Syllabus = {
    appConfig: null,
    loadingCounter: 0,
    start: function() {
	    Syllabus.loadingCounter = 0;
        Syllabus.appConfig = Utils.storage.readJSON(CONST_APP_CONFIG);

        return Syllabus.getAppConfig().done(function(data) { 
            Utils.storage.saveJSON(CONST_APP_CONFIG, data);

            Syllabus.appConfig = data;
        });
    },
    loggedIn: function() {
        var loginReg = /log\s*out\s*\((.+)\)/i,
        navbarDom = document.getElementsByClassName("navbar-syllabus");

        if (!navbarDom.length)
            throw "getLoginName::Could not locate navbar...";

        var logoutDom = navbarDom[0].querySelector('a[href="/logout"]');

        if (!logoutDom)
            return null;

        var logoutMatches = logoutDom.innerHTML.match(loginReg);

        if (!logoutMatches)
            throw "getLoginName::Found logout button, but could not retrieve account name...";

        return logoutMatches[1] ? true: false;
    },
    registerServiceWorker: function() {
        if (!Syllabus.loggedIn()) 
            return;

        if('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/syllabus/sphinx/sw.js')
                .then(reg => console.log('service worker registered', reg))
                .catch(err => console.log('service worker not registered', err));
        }
    },
    getSyllabusCourseName: function(){
        var urlPath = Utils.http.getPathFromUrl(Utils.http.getCurrentUrl());

        if (urlPath[0] === '/')
            urlPath = urlPath.substr(1);

        return urlPath.split("/")[1];
    },
    getAppConfig: function() {
        return $.ajax({
            url: CONST_APP_CONFIG_URL
        });
    },
    getInginiousURL: function() {
        return $.ajax({
            url: "/config/inginious_url/" + Syllabus.getSyllabusCourseName()
        });
    },
    getLtiParams: function(taskId) {
        return $.ajax({
            url: "/course/lti_params/" + taskId + "/" + Syllabus.getSyllabusCourseName(),
            dataType: 'json'
        });
    },
    onTaskLoad: function(callback) {
        var nbrCourses = CourseManager.getExercises().length;

        callback( Syllabus.loadingCounter, nbrCourses );

        if(Syllabus.loadingCounter < nbrCourses)
            window.setTimeout(Syllabus.onTaskLoad.bind(this, callback), 100);
    },
    loadTasks() {
        if (!Syllabus.loggedIn())
            return;

        var course = CourseManager.getCourse();
        var tasks = CourseManager.getExercises();

        /*for(var i = 0; i < arr.length ; i++) {
                let task = arr[i];
                Syllabus._loadTask(course, task).done(function(success){
                    if (!success) console.log("Could not load task: " + task);
                });
            }*/
        for(var i = 0; i < tasks.length ; i++) {
            let task = tasks[i];

            Syllabus._loadTask(course, task).done(function(success){
                if (!success) console.log("Could not load task: " + task);
            });
        }
    },

    _loadTask: function(course, taskId) {
        return Syllabus.getLtiParams(taskId).done(function(params) {
            var ingininiousUrl = Inginious.url,
                url = ingininiousUrl + '/lti/' + course + '/' + taskId;

            if (!ingininiousUrl) 
                return false;

            var iframe = Utils.DOM.createIframe(taskId, Syllabus._loadTaskDone),
                form = Syllabus._createLtiForm(url, params, taskId);

            document.body.appendChild(iframe);
            document.body.appendChild(form);
            
            iframe.onload = Syllabus._loadTaskDone;

            form.submit();

            return true;
        });
    },
    
    _loadTaskDone: function() {
        Syllabus.loadingCounter = Syllabus.loadingCounter +1;
        console.log("an iframe has finished loading and counter is now equal to " + Syllabus.loadingCounter);
    },

    _createLtiForm: function(url, params, target) {
        var form = document.createElement("form");

        form.action= url;
        form.encType= "application/x-www-form-urlencoded";
        form.target = target;
        form.name= "ltiLaunchForm";
        form.class= "ltiLaunchForm";
        form.method= "POST";

        for (element in params) {
            if (!params.hasOwnProperty(element)) continue;

            var input = document.createElement("input");

            input.name = element;
            input.value = params[element];

            form.appendChild(input);
        }

        return form;
    }
};