(function(){
  var input=document.getElementById('hbsearch');
  var panel=document.getElementById('hbresults');
  if(!input||!panel) return;
  var idx=null;
  fetch('assets/search-index.json').then(function(r){return r.json();}).then(function(d){idx=d;}).catch(function(){});
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function snippet(t,q){var lt=t.toLowerCase();var i=lt.indexOf(q);if(i<0)return t.slice(0,90);var s=Math.max(0,i-32);return (s>0?'…':'')+t.slice(s,i+q.length+58)+'…';}
  function run(){
    var q=input.value.trim().toLowerCase();
    if(!idx||q.length<1){panel.hidden=true;panel.innerHTML='';return;}
    var res=[];
    for(var i=0;i<idx.length&&res.length<14;i++){ if(idx[i].t.toLowerCase().indexOf(q)>=0) res.push(idx[i]); }
    if(!res.length){panel.hidden=false;panel.innerHTML='<div class="nores">「'+esc(input.value.trim())+'」に一致する場面はありません</div>';return;}
    panel.hidden=false;
    panel.innerHTML=res.map(function(e){
      return '<a class="sr" href="'+esc(e.url)+'"><span class="sr-t">'+esc(e.title)+'</span> <span class="sr-g">'+esc(e.g)+'</span><span class="sr-s">'+esc(snippet(e.t,q))+'</span></a>';
    }).join('');
  }
  input.addEventListener('input',run);
  input.addEventListener('focus',run);
  input.addEventListener('keydown',function(e){ if(e.key==='Escape'){panel.hidden=true;input.blur();} });
  document.addEventListener('click',function(e){ if(e.target!==input && !panel.contains(e.target)) panel.hidden=true; });
})();
