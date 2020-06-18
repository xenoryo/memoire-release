LocationManager = {

    jumpToLastPosition: function() {
        var active = sessionStorage.getItem('location_manager_active'),
            lastUrl = localStorage.getItem('location_manager_url');

        if (!active && lastUrl && !Utils.http.isCurrentUrl(lastUrl)) {
            Utils.http.browseTo(Utils.http.stripVariablesFromUrl(lastUrl));
        } 
        else if (!active && lastUrl) {
            sessionStorage.setItem('location_manager_active', true);
            LocationManager._jumpToLastScrolled();
            LocationManager._saveUserPosition();
            LocationManager._loadEvents();
        }
        else {
            sessionStorage.setItem('location_manager_active', true);
            LocationManager._saveUserPosition();
            LocationManager._loadEvents();
        }
    },
    _saveUserPosition: function() {
        localStorage.setItem('location_manager_url', window.location.href);
    },
    _loadEvents: function() {
        window.addEventListener("scroll", LocationManager._onScroll);
    },
    _onScroll: function(event) {
        localStorage.setItem('location_manager_scroll', window.scrollY);
    },
    _jumpToLastScrolled: function() {
        window.scroll(0, parseInt(localStorage.getItem('location_manager_scroll'), 10));
    }
    
};