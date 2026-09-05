from pathlib import Path

p=Path('blocked-drag.js')
s=p.read_text(encoding='utf-8')

old=""".blockedSchedule,.blockedBlock{-webkit-touch-callout:none;touch-action:pan-x;cursor:grab}\n.blockedSchedule.blockedDragging,.blockedBlock.blockedDragging{z-index:110!important;opacity:.96;box-shadow:0 0 0 3px rgba(138,74,66,.24),0 9px 26px rgba(0,0,0,.22)!important;transform:translateY(8px) scale(1.02);touch-action:none!important}\n.blockedDragGhost{pointer-events:none!important;z-index:4!important;opacity:.45!important;border:2px dashed rgba(138,74,66,.62)!important;background:rgba(244,223,220,.40)!important;box-shadow:none!important}\n"""
new=""".blockedSchedule,.blockedBlock{-webkit-touch-callout:none;touch-action:pan-x;cursor:pointer}\n.blockedSchedule.blockedDragging,.blockedBlock.blockedDragging{z-index:110!important;opacity:.96;box-shadow:0 0 0 3px rgba(138,74,66,.24),0 9px 26px rgba(0,0,0,.22)!important;transform:translateY(8px) scale(1.02);touch-action:none!important}\n.blockedDragGhost{pointer-events:none!important;z-index:4!important;opacity:.45!important;border:2px dashed rgba(138,74,66,.62)!important;background:rgba(244,223,220,.40)!important;box-shadow:none!important}\n.blockedMoveHandle{position:absolute;right:2px;top:50%;transform:translateY(-50%);z-index:30;width:28px;height:34px;border:1px solid rgba(120,70,64,.30);border-radius:9px;background:rgba(255,255,255,.88);display:flex;align-items:center;justify-content:center;color:#8a4a42;font-size:15px;font-weight:900;line-height:1;touch-action:none!important;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;cursor:ew-resize;box-shadow:0 1px 4px rgba(0,0,0,.08)}\n.blockedMoveHandle:active{background:#fff1ef;transform:translateY(-50%) scale(.96)}\n"""
if old not in s:
    raise SystemExit('style anchor not found')
s=s.replace(old,new,1)

anchor="""function onDown(e,el,item){\n"""
if anchor not in s:
    raise SystemExit('onDown anchor not found')
# Add a dedicated handle starter before onDown.
insert="""function ensureMoveHandle(el,item){\n  let h=el.querySelector('.blockedMoveHandle');\n  if(!movable(item)){if(h)h.remove();return null}\n  if(h)return h;\n  h=document.createElement('span');\n  h.className='blockedMoveHandle';\n  h.textContent='↔';\n  h.title='ここを左右に動かして予定時間を変更';\n  h.setAttribute('aria-label','予定時間を左右に移動');\n  h.addEventListener('click',e=>{e.preventDefault();e.stopPropagation()});\n  el.appendChild(h);\n  return h;\n}\n\nfunction onHandleDown(e,el,item){\n  if(drag||(e.pointerType==='mouse'&&e.button!==0))return;\n  const scroll=el.closest('.timelineScroll,.scheduleScroll');\n  if(!scroll||!movable(item))return;\n  const r=range(item);\n  e.preventDefault();\n  e.stopPropagation();\n  drag={\n    el,item,scroll,pointerId:e.pointerId,pointerType:e.pointerType||'touch',\n    startX:e.clientX,startY:e.clientY,currentX:e.clientX,currentY:e.clientY,\n    startScrollLeft:scroll.scrollLeft,\n    originalStart:r.start,newStart:r.start,duration:r.duration,\n    originalLeft:parseFloat(el.style.left)||((r.start-DAY_START)*PX_PER_MINUTE),\n    originalWidth:parseFloat(el.style.width)||Math.max(36,r.duration*PX_PER_MINUTE),\n    interacting:false,ghost:null\n  };\n  startDrag();\n}\n\n"""
s=s.replace(anchor,insert+anchor,1)

old_attach="""function attach(el,item){\n  if(el.dataset.blockedLongDrag==='1')return;\n  el.dataset.blockedLongDrag='1';\n  el.style.touchAction='pan-x';\n  const hint=el.querySelector('.blockedTapHint');\n  if(!movable(item)){\n    if(hint)hint.textContent='タップで時間変更';\n    return;\n  }\n  if(hint)hint.textContent='タップで編集・左右ドラッグで移動';\n  el.title=`${String(item.start_time).slice(0,5)}〜${String(item.end_time).slice(0,5)} タップで編集／左右ドラッグで移動`;\n  el.addEventListener('pointerdown',e=>onDown(e,el,item));\n  el.addEventListener('contextmenu',e=>e.preventDefault());\n}\n"""
new_attach="""function attach(el,item){\n  el.style.touchAction='pan-x';\n  const hint=el.querySelector('.blockedTapHint');\n  if(!movable(item)){\n    if(hint)hint.textContent='タップで時間変更';\n    ensureMoveHandle(el,item);\n    return;\n  }\n  if(hint)hint.textContent='タップで編集・↔を左右に動かして移動';\n  el.title=`${String(item.start_time).slice(0,5)}〜${String(item.end_time).slice(0,5)} タップで編集／↔で時間移動`;\n  const handle=ensureMoveHandle(el,item);\n  if(handle&&handle.dataset.boundMove!=='1'){\n    handle.dataset.boundMove='1';\n    handle.addEventListener('pointerdown',e=>onHandleDown(e,el,item));\n    handle.addEventListener('contextmenu',e=>e.preventDefault());\n  }\n}\n"""
if old_attach not in s:
    raise SystemExit('attach anchor not found')
s=s.replace(old_attach,new_attach,1)

# Update any user-facing guidance if present.
s=s.replace('タップで編集・左右ドラッグで移動','タップで編集・↔を左右に動かして移動')
s=s.replace('タップで変更・削除 ／ 左右ドラッグで時間移動','タップで変更・削除 ／ ↔で時間移動')
s=s.replace('左右へドラッグすると長さを保ったまま15分単位で移動できます。','右端の↔を左右へ動かすと、長さを保ったまま15分単位で移動できます。')

p.write_text(s,encoding='utf-8')
print('patched blocked drag handle')
