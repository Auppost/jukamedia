(function(){
  var shots=[].slice.call(document.querySelectorAll('.shot')),thumbs=[].slice.call(document.querySelectorAll('.thumbs button'));
  function show(i){shots.forEach(function(s,n){s.classList.toggle('on',n===i)});thumbs.forEach(function(t,n){t.classList.toggle('on',n===i)})}
  thumbs.forEach(function(t){t.addEventListener('click',function(){show(+t.dataset.i)})});
  var lb=document.querySelector('.lb');if(!lb)return;var im=null,last;
  function close(){lb.hidden=true;document.body.style.overflow='';if(last)last.focus()}
  shots.forEach(function(s){s.addEventListener('click',function(){last=s;if(!im){im=document.createElement('img');im.alt=(document.querySelector('h1')||{}).textContent||'';lb.appendChild(im)}im.src=s.dataset.big;lb.hidden=false;document.body.style.overflow='hidden';lb.querySelector('.x').focus()})});
  lb.addEventListener('click',function(e){if(e.target!==im)close()});
  document.addEventListener('keydown',function(e){if(!lb.hidden&&e.key==='Escape')close()});
})();
