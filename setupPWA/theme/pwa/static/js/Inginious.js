Inginious = {
    url: null,

    start: function() {
        return Syllabus.getInginiousURL().done(function(url) {
            Inginious.url = url;
            localStorage.setItem('inginious_url', url);
        }).fail(function() {
            Inginious.url = localStorage.getItem('inginious_url');
        });
    },

    registerServiceWorker: function() {
        if (!Inginious.url) 
            throw "Inginious::registerServiceWorker could not load base url - Did you forget to start ? ";

        var pluginPath = "/plugins/INGIniousServiceWorkerRegristrant.html";
        var iframe = Utils.DOM.createIframe("inginiousServiceWorker");


        iframe.src = Inginious.url + pluginPath;

        document.body.appendChild(iframe);
        
    },


    plugins: {

        chapterAccess: function(course) {
            if (!Inginious.url) 
                throw "Inginious::plugins::chapterAccess could not load base url - Did you forget to start ? ";

            var validTaskName = Utils.storage.readJSON("chapters_manager_course_config").exercises[0];
            var passingThreshold = Utils.storage.readJSON("chapters_manager_course_config").passingThreshold;
			return $.ajax({
				url: "/plugin/hideChapters/" + course + "/" + Syllabus.getSyllabusCourseName() + "/" + validTaskName + "/" + passingThreshold,
				dataType: 'json'
			});

        }

    }
}