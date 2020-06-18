window.onload = function() {
    LocationManager.jumpToLastPosition();
    _loadEvents();

    this.loadSystems([Inginious, Syllabus], function() {
        Inginious.registerServiceWorker();
        Syllabus.registerServiceWorker();
        CourseManager.blockChapterAccess();        
    });
}

function loadSystems(systems, callback) {
    var loaded = 0;
    for (var i=0; i<systems.length;i++) {
        systems[i].start().always(function() {
            loaded++;

            if (loaded == systems.length) callback();
        });
    }
}

function _loadEvents() {
    var loadExercisesBtn = document.getElementById("btnCacheTasks");
    
    if (loadExercisesBtn) loadExercisesBtn.addEventListener("click", _taskLoadingFrame);
}


function _taskLoadingFrame() {
    var container = document.getElementById("syllabusLoadingPopup");
    container.style.display = "block";

    Syllabus.onTaskLoad(function(loaded, total) {
        var percentage = Math.round( (loaded / total) * 100 );
        console.log("We loaded " + percentage + '% of tasks [' + loaded + '/' + total + ']');

        var loadingBar = document.getElementById("loadingBar");

        loadingBar.innerText = percentage + '%';
        loadingBar.style.width = percentage + '%';

        if (loaded == total) setTimeout(function() {
            container.style.display = "none";
        }, 1500);
    });

    Syllabus.loadTasks();
}