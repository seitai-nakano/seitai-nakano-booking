from pathlib import Path

p = Path('index.html')
s = p.read_text()

marker = '<script>\nconst BOOKING_GUIDE_DEFAULT_HINT='
start = s.index(marker)
end = s.index('</script>', start) + len('</script>')

clean_script = r'''<script>
const BOOKING_GUIDE_DEFAULT_HINT='紹介してくれるなら、ぼくをタップしてね';
let bookingGuideHintTimer=null;

function bookingGuideHint(text=BOOKING_GUIDE_DEFAULT_HINT,ms=0){
  const el=$('bookingGuideAlways');
  if(!el)return;
  clearTimeout(bookingGuideHintTimer);
  el.textContent=text;
  if(ms>0)bookingGuideHintTimer=setTimeout(()=>{el.textContent=BOOKING_GUIDE_DEFAULT_HINT},ms);
}

function bookingGuideSides(){
  const g=$('bookingGuide'),b=$('bookingGuideMascotBtn');
  if(!g||!b)return;
  const r=b.getBoundingClientRect();
  g.classList.toggle('guideLeft',r.left+r.width/2<innerWidth/2);
  g.classList.toggle('guideTop',r.top<145);
}

function bookingGuideInstallDrag(){
  const g=$('bookingGuide');
  const b=$('bookingGuideMascotBtn');
  const share=$('bookingGuideShare');
  if(!g||!b||manageToken)return;

  // bookingGuideInit() が付けた通常クリックだけ解除し、操作処理はここ一本にする。
  b.onclick=null;
  if(share)share.onclick=shareSeitaiNakano;

  const MARGIN=8;
  const THRESHOLD=5;
  const words=['よいしょ、よいしょ','ついていくよ','ここかな？','どこにする？','いっしょに行くね'];

  let active=false;
  let dragging=false;
  let touchId=null;
  let startX=0,startY=0;
  let startGuideLeft=0,startGuideTop=0;
  let buttonOffsetX=0,buttonOffsetY=0;
  let buttonW=0,buttonH=0;
  let lastWordAt=0,wordIndex=0;

  const setGuidePosition=(left,top)=>{
    const minLeft=MARGIN-buttonOffsetX;
    const maxLeft=innerWidth-MARGIN-buttonW-buttonOffsetX;
    const minTop=MARGIN-buttonOffsetY;
    const maxTop=innerHeight-MARGIN-buttonH-buttonOffsetY;
    const x=Math.max(minLeft,Math.min(maxLeft,left));
    const y=Math.max(minTop,Math.min(maxTop,top));
    g.style.transform='none';
    g.style.right='auto';
    g.style.bottom='auto';
    g.style.left=`${Math.round(x)}px`;
    g.style.top=`${Math.round(y)}px`;
  };

  const savePosition=()=>{
    const r=g.getBoundingClientRect();
    try{localStorage.setItem('nakano_booking_guide_drag_pos_v2',JSON.stringify({left:r.left,top:r.top}))}catch(_){}
  };

  const restorePosition=()=>{
    let saved=null;
    try{saved=JSON.parse(localStorage.getItem('nakano_booking_guide_drag_pos_v2')||'null')}catch(_){}
    if(!saved||!Number.isFinite(saved.left)||!Number.isFinite(saved.top)){
      bookingGuideSides();
      return;
    }
    const gr=g.getBoundingClientRect(),br=b.getBoundingClientRect();
    buttonOffsetX=br.left-gr.left;
    buttonOffsetY=br.top-gr.top;
    buttonW=br.width;
    buttonH=br.height;
    setGuidePosition(saved.left,saved.top);
    bookingGuideSides();
  };

  const begin=(x,y,id,e)=>{
    if(active)return;
    if(e?.cancelable)e.preventDefault();
    const gr=g.getBoundingClientRect();
    const br=b.getBoundingClientRect();
    active=true;
    dragging=false;
    touchId=id;
    startX=x;
    startY=y;
    startGuideLeft=gr.left;
    startGuideTop=gr.top;
    buttonOffsetX=br.left-gr.left;
    buttonOffsetY=br.top-gr.top;
    buttonW=br.width;
    buttonH=br.height;
    lastWordAt=0;
    wordIndex=0;
    clearTimeout(bookingGuideTimer);
  };

  const move=(x,y,e)=>{
    if(!active)return;
    if(e?.cancelable)e.preventDefault();
    const dx=x-startX,dy=y-startY;
    if(!dragging&&Math.hypot(dx,dy)<THRESHOLD)return;
    if(!dragging){
      dragging=true;
      g.classList.add('dragging');
      g.classList.remove('open','thinking','done');
      bookingGuideHint('よいしょ、よいしょ');
    }
    setGuidePosition(startGuideLeft+dx,startGuideTop+dy);
    bookingGuideSides();
    const now=performance.now();
    if(now-lastWordAt>650){
      bookingGuideHint(words[wordIndex++%words.length]);
      lastWordAt=now;
    }
  };

  const finish=(e)=>{
    if(!active)return;
    if(e?.cancelable)e.preventDefault();
    active=false;
    touchId=null;
    g.classList.remove('dragging');
    if(dragging){
      dragging=false;
      savePosition();
      bookingGuideSides();
      bookingGuideHint('ここで待ってるね',1800);
      return;
    }
    const open=!g.classList.contains('open');
    g.classList.toggle('open',open);
    g.classList.remove('thinking','done');
    bookingGuideHint();
  };

  b.addEventListener('touchstart',e=>{
    if(e.touches.length!==1)return;
    const t=e.touches[0];
    begin(t.clientX,t.clientY,t.identifier,e);
  },{passive:false});

  document.addEventListener('touchmove',e=>{
    if(!active||touchId===null)return;
    const t=Array.from(e.touches).find(x=>x.identifier===touchId);
    if(!t)return;
    move(t.clientX,t.clientY,e);
  },{passive:false,capture:true});

  document.addEventListener('touchend',e=>{
    if(!active||touchId===null)return;
    const ended=Array.from(e.changedTouches).some(x=>x.identifier===touchId);
    if(ended)finish(e);
  },{passive:false,capture:true});

  document.addEventListener('touchcancel',e=>{
    if(!active)return;
    active=false;
    dragging=false;
    touchId=null;
    g.classList.remove('dragging');
    bookingGuideHint();
  },{passive:true,capture:true});

  // PC確認用。モバイルのタッチ処理とは独立。
  b.addEventListener('mousedown',e=>{
    if(e.button!==0)return;
    begin(e.clientX,e.clientY,'mouse',e);
  });
  document.addEventListener('mousemove',e=>{if(active&&touchId==='mouse')move(e.clientX,e.clientY,e)});
  document.addEventListener('mouseup',e=>{if(active&&touchId==='mouse')finish(e)});

  b.addEventListener('click',e=>{
    e.preventDefault();
    e.stopPropagation();
  });

  requestAnimationFrame(restorePosition);
  addEventListener('resize',restorePosition,{passive:true});
}

bookingGuideInstallDrag();
</script>'''

s = s[:start] + clean_script + s[end:]

css = '''\n/* single-source mascot drag */\n.bookingGuideMascotBtn{touch-action:none!important;-webkit-touch-callout:none!important;-webkit-user-select:none!important;user-select:none!important}\n.bookingGuide.dragging .bookingGuideMascotBtn{animation:none!important;cursor:grabbing}\n'''
if '/* single-source mascot drag */' not in s:
    s = s.replace('</style>', css + '</style>', 1)

p.write_text(s)
