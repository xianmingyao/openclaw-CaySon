(() => {
  const getMeta = (name) => {
    const el = document.querySelector('meta[name="' + name + '"]') ||
               document.querySelector('meta[property="' + name + '"]');
    return el ? el.getAttribute('content') : null;
  };
  return JSON.stringify({
    title: document.title,
    description: getMeta('description'),
    ogTitle: getMeta('og:title'),
    ogDescription: getMeta('og:description'),
    ogImage: getMeta('og:image'),
    ogVideo: getMeta('og:video'),
    ogUrl: getMeta('og:url'),
    author: getMeta('author'),
    keywords: getMeta('keywords'),
    canonical: document.querySelector('link[rel=canonical]')?.href,
    bodyText: document.body.innerText.slice(0, 800)
  }, null, 2);
})()