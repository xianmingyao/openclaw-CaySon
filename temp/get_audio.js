(function(){
  try {
    var entries = performance.getEntriesByType('resource') || [];
    var candidates = [];
    for(var i=0;i<entries.length;i++){
      var n = entries[i].name || '';
      if(n.indexOf('media')!==-1 || n.indexOf('audio')!==-1 || n.indexOf('.m4a')!==-1 || n.indexOf('.mp3')!==-1 || n.indexOf('.aac')!==-1){
        candidates.push({
          name: n,
          duration: entries[i].duration,
          transferSize: entries[i].transferSize,
          type: entries[i].initiatorType
        });
      }
    }
    return JSON.stringify({
      count: candidates.length,
      items: candidates.slice(0,20)
    });
  } catch(e){
    return 'ERROR: ' + e.message;
  }
})()