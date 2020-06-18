const staticCacheNameIngi = 'site-static-ingi';

self.addEventListener('install', evt => {

    console.log('ingi service worker installed');

});
self.addEventListener('activate', evt => {
	console.log('ingi service worker activated');
  
  });
  
self.addEventListener('fetch', event => {
	event.respondWith(
          fetch(event.request).then(function(fetchResponse) {
            console.log("promise succeed")
            return caches.open(staticCacheNameIngi).then(cache => {
                cache.delete(event.request.url);
                cache.put(event.request.url, fetchResponse.clone())
                return fetchResponse;
            })
        }).catch((x) => {
            
			console.log("promise failed")
			
			console.log("url : " + event.request.url)
			
           	return caches.open(staticCacheNameIngi).then((cache) =>{
				   return cache.match(event.request.url).then( (cacheValue) =>{
					   console.log(cacheValue)
					   return cacheValue;
				   });
			});
			  
			
       

		}))
});