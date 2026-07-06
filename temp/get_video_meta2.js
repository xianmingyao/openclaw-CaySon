(function(){
  function gm(n){
    var els = document.querySelectorAll('meta');
    for(var i=0;i<els.length;i++){
      var a = els[i].getAttribute('name');
      var p = els[i].getAttribute('property');
      if(a===n || p===n){ return els[i].getAttribute('content'); }
    }
    return null;
  }
  var result = {
    title: document.title,
    description: gm('description'),
    ogTitle: gm('og:title'),
    ogDescription: gm('og:description'),
    ogImage: gm('og:image'),
    ogUrl: gm('og:url'),
    keywords: gm('keywords'),
    canonical: (document.querySelector('link[rel=canonical]')||{}).href,
    h1Texts: Array.from(document.querySelectorAll('h1,h2,h3')).map(function(e){return e.innerText;}).slice(0,20)
  };
  return JSON.stringify(result);
})()