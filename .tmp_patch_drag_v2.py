from pathlib import Path
p=Path('index.html')
s=p.read_text()
marker='bookingGuideInstallDrag();\n</script>'
assert marker in s
new=r'''
function bookingGuideInstallDirectDrag(){
  const g=$('bookingGuide'), old=$('bookingGuideMascotBtn');
  if(!g||!old||manageToken)return;

  const b=old.cloneNode(true);
  old.replaceWith(b);

  const margin=8;
  const words=['よいしょ、よいしょ','ついていくよ','ここかな？','どこにする？','いっしょに行くね'];
  let active=false,dragged=false,startX=0,startY=0,startLeft=0,startTop=0,lastWord=0,wordIndex=0;

  const clamp=(v,min,max)=>Math.max(min,Math.min(max,v));
  const place=(left,top)=>{
    const w=g.offsetWidth||82,h=g.offsetHeight||82;
    const x=clamp(left,margin,Math.max(margin,innerWidth-w-margin));
    const y=clamp(top,margin,Math.max(margin,innerHeight-h-margin));
    g.style.transform='none';
    g.style.left=`${Math.round(x)}px`;
    g.style.top=`${Math.round(y)}px`;
    g.style.right='auto';
    g.style.bottom='auto';
    bookingGuideSides();
  };

  const restore=()=>{
    let saved=null;
    try{saved=JSON.parse(localStorage.getItem('nakano_booking_guide_direct_pos_v1')||'null')}catch(_){}
    if(saved&&Number.isFinite(saved.left)&&Number.isFinite(saved.top)){
      place(saved.left,saved.top);
      return;
    }
    const r=g.getBoundingClientRect();
    place(r.left,r.top);
  };

  const begin=(x,y,e)=>{
    if(e?.cancelable)e.preventDefault();
    const r=g.getBoundingClientRect();
    active=true;dragged=false;
    startX=x;startY=y;startLeft=r.left;startTop=r.top;
    lastWord=0;wordIndex=0;
    clearTimeout(bookingGuideTimer);
    g.classList.remove('open','thinking','done');
    bookingGuideHint('つかまえたよ');
  };

  const move=(x,y,e)=>{
    if(!active)return;
    if(e?.cancelable)e.preventDefault();
    const dx=x-startX,dy=y-startY;
    if(!dragged&&Math.hypot(dx,dy)<3)return;
    dragged=true;
    g.classList.add('dragging');
    place(startLeft+dx,startTop+dy);
    const now=performance.now();
    if(now-lastWord>500){bookingGuideHint(words[wordIndex++%words.length]);lastWord=now}
  };

  const finish=(e)=>{
    if(!active)return;
    if(e?.cancelable)e.preventDefault();
    active=false;
    g.classList.remove('dragging');
    if(dragged){
      const r=g.getBoundingClientRect();
      try{localStorage.setItem('nakano_booking_guide_direct_pos_v1',JSON.stringify({left:r.left,top:r.top}))}catch(_){}
      bookingGuideHint('ここで待ってるね',1800);
      return;
    }
    bookingGuideSides();
    const open=!g.classList.contains('open');
    g.classList.toggle('open',open);
    g.classList.remove('thinking','done');
    bookingGuideHint();
  };

  b.addEventListener('touchstart',e=>{
    if(e.touches.length!==1)return;
    const t=e.touches[0];
    begin(t.clientX,t.clientY,e);
  },{passive:false});
  b.addEventListener('touchmove',e=>{
    if(e.touches.length!==1)return;
    const t=e.touches[0];
    move(t.clientX,t.clientY,e);
  },{passive:false});
  b.addEventListener('touchend',finish,{passive:false});
  b.addEventListener('touchcancel',()=>{active=false;dragged=false;g.classList.remove('dragging');bookingGuideHint()},{passive:true});

  b.addEventListener('pointerdown',e=>{
    if(e.pointerType==='touch'||e.button!==0)return;
    begin(e.clientX,e.clientY,e);
  });
  window.addEventListener('pointermove',e=>{if(e.pointerType!=='touch')move(e.clientX,e.clientY,e)});
  window.addEventListener('pointerup',e=>{if(e.pointerType!=='touch')finish(e)});

  b.addEventListener('click',e=>{e.preventDefault();e.stopPropagation()});
  restore();
  addEventListener('resize',restore,{passive:true});
}
bookingGuideInstallDirectDrag();
'''
s=s.replace(marker,'bookingGuideInstallDrag();\n'+new+'\n</script>',1)
p.write_text(s)
