from pathlib import Path
p=Path('blocked-drag.js')
s=p.read_text(encoding='utf-8')
s=s.replace("const DRAG_START_DISTANCE=5;", "const DRAG_START_DISTANCE=5;\nconst TOUCH_HOLD_TO_DRAG_MS=240;\nconst SCROLL_INTENT_DISTANCE=8;")
s=s.replace(".blockedSchedule,.blockedBlock{-webkit-touch-callout:none;touch-action:none;cursor:grab}", ".blockedSchedule,.blockedBlock{-webkit-touch-callout:none;touch-action:pan-x;cursor:grab}")
old="""function onDown(e,el,item){
  if(drag||(e.pointerType==='mouse'&&e.button!==0))return;
  const scroll=el.closest('.timelineScroll,.scheduleScroll');
  if(!scroll||!movable(item))return;
  const r=range(item);
  drag={
    el,item,scroll,pointerId:e.pointerId,
    startX:e.clientX,startY:e.clientY,currentX:e.clientX,currentY:e.clientY,
    startScrollLeft:scroll.scrollLeft,
    originalStart:r.start,newStart:r.start,duration:r.duration,
    originalLeft:parseFloat(el.style.left)||((r.start-DAY_START)*PX_PER_MINUTE),
    originalWidth:parseFloat(el.style.width)||Math.max(36,r.duration*PX_PER_MINUTE),
    interacting:false,ghost:null
  };
  // Capture immediately so iPhone/Android/desktop keep sending the same pointer
  // even when the finger or mouse moves across the horizontally scrollable schedule.
  try{el.setPointerCapture(e.pointerId)}catch{}
}
"""
new="""function onDown(e,el,item){
  if(drag||(e.pointerType==='mouse'&&e.button!==0))return;
  const scroll=el.closest('.timelineScroll,.scheduleScroll');
  if(!scroll||!movable(item))return;
  const r=range(item);
  drag={
    el,item,scroll,pointerId:e.pointerId,pointerType:e.pointerType||'touch',
    startX:e.clientX,startY:e.clientY,currentX:e.clientX,currentY:e.clientY,
    startScrollLeft:scroll.scrollLeft,
    originalStart:r.start,newStart:r.start,duration:r.duration,
    originalLeft:parseFloat(el.style.left)||((r.start-DAY_START)*PX_PER_MINUTE),
    originalWidth:parseFloat(el.style.width)||Math.max(36,r.duration*PX_PER_MINUTE),
    interacting:false,ghost:null
  };

  // Touch: ordinary horizontal swipe must remain native schedule scrolling.
  // Only a short hold arms moving the red blocked/plan card.
  clearTimeout(pressTimer);
  if(e.pointerType!=='mouse'){
    const pointerId=e.pointerId;
    pressTimer=setTimeout(()=>{
      if(drag&&drag.pointerId===pointerId&&!drag.interacting)startDrag();
    },TOUCH_HOLD_TO_DRAG_MS);
  }
}
"""
if old not in s: raise SystemExit('onDown anchor missing')
s=s.replace(old,new,1)
old="""function onMove(e){
  const s=drag;if(!s||s.pointerId!==e.pointerId)return;
  s.currentX=e.clientX;s.currentY=e.clientY;
  if(!s.interacting){
    const dx=s.currentX-s.startX,dy=s.currentY-s.startY;
    if(Math.hypot(dx,dy)<DRAG_START_DISTANCE)return;
    if(Math.abs(dy)>Math.abs(dx)*1.25){drag=null;return}
    startDrag();
    if(!drag?.interacting)return;
  }
  e.preventDefault();updateVisual();
}
"""
new="""function onMove(e){
  const s=drag;if(!s||s.pointerId!==e.pointerId)return;
  s.currentX=e.clientX;s.currentY=e.clientY;
  if(!s.interacting){
    const dx=s.currentX-s.startX,dy=s.currentY-s.startY;

    if(s.pointerType==='mouse'){
      if(Math.hypot(dx,dy)<DRAG_START_DISTANCE)return;
      if(Math.abs(dy)>Math.abs(dx)*1.25){clearTimeout(pressTimer);pressTimer=null;drag=null;return}
      startDrag();
      if(!drag?.interacting)return;
    }else{
      // Before the hold fires, a clear horizontal gesture belongs to native scrolling.
      if(Math.abs(dx)>=SCROLL_INTENT_DISTANCE&&Math.abs(dx)>Math.abs(dy)*1.1){
        clearTimeout(pressTimer);pressTimer=null;drag=null;return;
      }
      // Vertical movement also cancels the pending card drag.
      if(Math.abs(dy)>=12&&Math.abs(dy)>=Math.abs(dx)){
        clearTimeout(pressTimer);pressTimer=null;drag=null;return;
      }
      return;
    }
  }
  e.preventDefault();updateVisual();
}
"""
if old not in s: raise SystemExit('onMove anchor missing')
s=s.replace(old,new,1)
s=s.replace("el.style.touchAction='none';", "el.style.touchAction='pan-x';", 1)
s=s.replace("if(hint)hint.textContent='タップで編集・左右ドラッグで移動';", "if(hint)hint.textContent='タップで編集・長押しして左右で移動';", 1)
s=s.replace("el.title=`${String(item.start_time).slice(0,5)}〜${String(item.end_time).slice(0,5)} タップで編集／左右ドラッグで移動`;", "el.title=`${String(item.start_time).slice(0,5)}〜${String(item.end_time).slice(0,5)} タップで編集／長押しして左右で移動`;", 1)
p.write_text(s,encoding='utf-8')
print('patched blocked drag vs horizontal scroll')
