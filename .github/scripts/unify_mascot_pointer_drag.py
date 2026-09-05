from pathlib import Path

p = Path('index.html')
s = p.read_text()

s = s.replace('let touchId=null;', 'let activePointerId=null;')
s = s.replace('touchId=id;', 'activePointerId=id;')
s = s.replace('touchId=null;', 'activePointerId=null;')

old = """  b.addEventListener('touchstart',e=>{
    if(e.touches.length!==1)return;
    const t=e.touches[0];
    begin(t.clientX,t.clientY,t.identifier,e);
  },{passive:false});

  document.addEventListener('touchmove',e=>{
    if(!active||activePointerId===null)return;
    const t=Array.from(e.touches).find(x=>x.identifier===activePointerId);
    if(!t)return;
    move(t.clientX,t.clientY,e);
  },{passive:false,capture:true});

  document.addEventListener('touchend',e=>{
    if(!active||activePointerId===null)return;
    const ended=Array.from(e.changedTouches).some(x=>x.identifier===activePointerId);
    if(ended)finish(e);
  },{passive:false,capture:true});

  document.addEventListener('touchcancel',e=>{
    if(!active)return;
    active=false;
    dragging=false;
    activePointerId=null;
    g.classList.remove('dragging');
    bookingGuideHint();
  },{passive:true,capture:true});

  // PC確認用。モバイルのタッチ処理とは独立。
  b.addEventListener('mousedown',e=>{
    if(e.button!==0)return;
    begin(e.clientX,e.clientY,'mouse',e);
  });
  document.addEventListener('mousemove',e=>{if(active&&activePointerId==='mouse')move(e.clientX,e.clientY,e)});
  document.addEventListener('mouseup',e=>{if(active&&activePointerId==='mouse')finish(e)});

  b.addEventListener('click',e=>{
    e.preventDefault();
    e.stopPropagation();
  });
"""

new = """  // iPhone / Android / PC / tablet / pen: one unified input path.
  if('PointerEvent' in window){
    b.addEventListener('pointerdown',e=>{
      if(e.pointerType==='mouse'&&e.button!==0)return;
      if(active)return;
      if(e.cancelable)e.preventDefault();
      try{b.setPointerCapture(e.pointerId)}catch(_){}
      begin(e.clientX,e.clientY,e.pointerId,e);
    });

    b.addEventListener('pointermove',e=>{
      if(!active||activePointerId!==e.pointerId)return;
      move(e.clientX,e.clientY,e);
    });

    const endPointer=e=>{
      if(!active||activePointerId!==e.pointerId)return;
      finish(e);
      try{if(b.hasPointerCapture?.(e.pointerId))b.releasePointerCapture(e.pointerId)}catch(_){}
    };
    b.addEventListener('pointerup',endPointer);
    b.addEventListener('pointercancel',e=>{
      if(!active||activePointerId!==e.pointerId)return;
      active=false;
      dragging=false;
      activePointerId=null;
      g.classList.remove('dragging');
      bookingGuideHint();
      try{if(b.hasPointerCapture?.(e.pointerId))b.releasePointerCapture(e.pointerId)}catch(_){}
    });
  }else{
    // Legacy fallback for very old browsers.
    b.addEventListener('touchstart',e=>{
      if(e.touches.length!==1)return;
      const t=e.touches[0];
      begin(t.clientX,t.clientY,t.identifier,e);
    },{passive:false});
    document.addEventListener('touchmove',e=>{
      if(!active||activePointerId===null)return;
      const t=Array.from(e.touches).find(x=>x.identifier===activePointerId);
      if(t)move(t.clientX,t.clientY,e);
    },{passive:false,capture:true});
    document.addEventListener('touchend',e=>{
      if(!active||activePointerId===null)return;
      if(Array.from(e.changedTouches).some(x=>x.identifier===activePointerId))finish(e);
    },{passive:false,capture:true});
    document.addEventListener('touchcancel',()=>{
      active=false;dragging=false;activePointerId=null;g.classList.remove('dragging');bookingGuideHint();
    },{passive:true,capture:true});
    b.addEventListener('mousedown',e=>{
      if(e.button!==0)return;
      begin(e.clientX,e.clientY,'mouse',e);
    });
    document.addEventListener('mousemove',e=>{if(active&&activePointerId==='mouse')move(e.clientX,e.clientY,e)});
    document.addEventListener('mouseup',e=>{if(active&&activePointerId==='mouse')finish(e)});
  }

  b.addEventListener('click',e=>{
    e.preventDefault();
    e.stopPropagation();
  });
"""

if old not in s:
    raise SystemExit('target input block not found')

s = s.replace(old, new, 1)
p.write_text(s)
