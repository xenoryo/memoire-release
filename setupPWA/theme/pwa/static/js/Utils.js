Utils = {
    http: {
        browseTo: function(link) {
            window.location.href = link;
        },
        getCurrentUrl: function() {
            return window.location.href;
        },
        stripVariablesFromUrl: function(url) {
            return url.split('#')[0].split('?')[0];
        },
        isCurrentUrl: function(url) {
            return Utils.http.stripVariablesFromUrl(Utils.http.getCurrentUrl()) == Utils.http.stripVariablesFromUrl(url);
        },
        prefixLinkWithLocation: function(link) {
            var fullLocation = window.location.href.replace(window.location.origin, "").split('/');
            fullLocation.pop();
            fullLocation = fullLocation.join('/');

            if (link.includes(fullLocation))
                return link;

            return fullLocation + '/' + link;
        },
        getDomainFromUrl: function(url) {
            return url.match(/^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n?]+)(:(\d)*)?/img)[0]
        },
        getPathFromUrl: function(url) {
            return Utils.http.stripVariablesFromUrl(
                url.substr(Utils.http.getDomainFromUrl(url).length)
            );
        }
    },


    storage: {
        saveJSON: function(key, value) {
            if (!key) throw "Utils::storage::saveJSON expects a key.";
            if (typeof value !== "object") throw "Utils::storage::saveJSON unexpected value.";

            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch(e) {
                throw "Utils::storage::saveJSON could not save value - " + e;
            }
        },
        readJSON: function(key) {
            if (!key) throw "Utils::storage::readJSON expects a key.";

            var value = localStorage.getItem(key);

            if (!value) return {};

            try {
                value = JSON.parse(value);
            } catch (e) {
                throw "Utils::storage::readJSON could not parse storage value.";
            }
            return value;
        }
    },

    DOM: {
        createIframe: function(id) {
            var iframe = document.createElement("iframe");

            iframe.id = id;
            iframe.name = id;
            iframe.style.display = "none";
            return iframe;
        },
        deleteElement: function(id) {
            var elem = document.getElementById(id);
            return elem.parentNode.removeChild(elem);
        }
    }
};