from pathlib import Path
import re

p=Path('blocked-drag.js')
s=p.read_text()

s=re.sub(r"function onDown\(e,el,item\)\{.*?\n\}\n\nfunction onMove\(e\)\{", r'''function onDown(e,el,item){
  if(drag||(e.pointerType==='mouse'&&e.button!==0))return;
  const scroll=el.closest('.timelineScroll,.scheduleScroll');
  if(!scroll||!movable(item))return;
  const r=range(item);
  const captureTarget=el;
  try{captureTarget.setPointerCapture?.(e.pointerId)}catch{}
  drag={
    el,item,scroll,pointerId:e.pointerId,pointerType:e.pointerType||'touch',captureTarget,
    startX:e.clientX,startY:e.clientY,currentX:e.clientX,currentY:e.clientY,
    startScrollLeft:scroll.scrollLeft,
    originalStart:r.start,newStart:r.start,duration:r.duration,
    originalLeft:parseFloat(el.style.left)||((r.start-DAY_START)*PX_PER_MINUTE),
    originalWidth:parseFloat(el.style.width)||Math.max(36,r.duration*PX_PER_MINUTE),
    interacting:false,ghost:null
  };
}

function onMove(e){''', s, flags=re.S)

s=re.sub(r"function onMove\(e\)\{.*?\n\}\n\nasync function onUp\(e\)\{", r'''function onMove(e){
  const s=drag;if(!s||s.pointerId!==e.pointerId)return;
  s.currentX=e.clientX;s.currentY=e.clientY;
  const dx=s.currentX-s.startX,dy=s.currentY-s.startY;
  if(!s.interacting){
    if(Math.abs(dx)<DRAG_START_DISTANCE)return;
    // The red plan block itself is the drag surface. Horizontal intent starts moving immediately.
    if(Math.abs(dx)<Math.abs(dy)*0.7)return;
    startDrag();
    if(!drag?.interacting)return;
  }
  e.preventDefault();
  const rect=s.scroll.getBoundingClientRect();
  let immediate=0;
  if(s.currentX<rect.left+EDGE_ZONE){
    const q=Math.max(0,Math.min(1,(rect.left+EDGE_ZONE-s.currentX)/EDGE_ZONE));
    immediate=-(6+q*16);
  }else if(s.currentX>rect.right-EDGE_ZONE){
    const q=Math.max(0,Math.min(1,(s.currentX-(rect.right-EDGE_ZONE))/EDGE_ZONE));
    immediate=6+q*16;
  }
  if(immediate){
    const maxScroll=Math.max(0,s.scroll.scrollWidth-s.scroll.clientWidth);
    s.scroll.scrollLeft=Math.max(0,Math.min(maxScroll,s.scroll.scrollLeft+immediate));
  }
  updateVisual();
}

async function onUp(e){''', s, flags=re.S)

s=s.replace("  if(!s.interacting)return;\n  suppressClickUntil=Date.now()+900;", "  if(!s.interacting){\n    try{s.captureTarget?.releasePointerCapture?.(s.pointerId)}catch{}\n    return;\n  }\n  suppressClickUntil=Date.now()+900;")

s=re.sub(r"function attach\(el,item\)\{.*?\n\}\n\nasync function hydrate", r'''function attach(el,item){
  // Starting on the red plan block means moving that block; empty schedule space still scrolls normally.
  el.style.touchAction='none';
  el.querySelector('.blockedMoveHandle')?.remove();
  const hint=el.querySelector('.blockedTapHint');
  if(!movable(item)){
    if(hint)hint.textContent='タップで時間変更';
    return;
  }
  if(hint)hint.textContent='枠を左右にドラッグして移動・タップで編集';
  el.title=`${String(item.start_time).slice(0,5)}〜${String(item.end_time).slice(0,5)} 枠を左右にドラッグして時間移動`;
  if(el.dataset.boundBlockMove!=='1'){
    el.dataset.boundBlockMove='1';
    el.addEventListener('pointerdown',e=>onDown(e,el,item));
    el.addEventListener('contextmenu',e=>e.preventDefault());
  }
}

async function hydrate''', s, flags=re.S)

# Keep the card itself visually grabbable and stop Safari from claiming the gesture.
s=s.replace(".blockedSchedule,.blockedBlock{-webkit-touch-callout:none;touch-action:pan-x;cursor:pointer}", ".blockedSchedule,.blockedBlock{-webkit-touch-callout:none;touch-action:none;cursor:grab}")
s=s.replace("cursor:pointer}", "cursor:grab}", 1) if ".blockedSchedule,.blockedBlock" in s else s

required=[
    "el.dataset.boundBlockMove='1'",
    "el.addEventListener('pointerdown',e=>onDown(e,el,item))",
    "el.style.touchAction='none'",
    "枠を左右にドラッグして移動",
]
for marker in required:
    if marker not in s:
        raise SystemExit(f'missing marker: {marker}')

p.write_text(s)
