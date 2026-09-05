from pathlib import Path

p=Path('blocked-drag.js')
s=p.read_text()

s=s.replace("const DRAG_START_DISTANCE=4;\nconst EDGE_ZONE=120;", "const DRAG_START_DISTANCE=4;\nconst LONG_PRESS_MS=420;\nconst LONG_PRESS_CANCEL_DISTANCE=10;\nconst EDGE_ZONE=120;")
s=s.replace("let drag=null;\nlet autoFrame=null;", "let drag=null;\nlet pressTimer=null;\nlet autoFrame=null;")
s=s.replace("function cleanup(s){\n  s?.el?.classList.remove('blockedDragging');", "function cleanup(s){\n  clearTimeout(pressTimer);pressTimer=null;\n  s?.el?.classList.remove('blockedDragging');")

old_start="""function onTouchStart(e,el,item){
  if(drag||e.touches.length!==1)return;
  const t=e.changedTouches[0];
  const s=createDragState(el,item,t.clientX,t.clientY,'touch',{touchId:t.identifier});
  if(!s)return;
  drag=s;
  e.stopPropagation();
}"""
new_start="""function onTouchStart(e,el,item){
  if(drag||e.touches.length!==1)return;
  const t=e.changedTouches[0];
  const s=createDragState(el,item,t.clientX,t.clientY,'touch',{touchId:t.identifier});
  if(!s)return;
  drag=s;
  clearTimeout(pressTimer);
  pressTimer=setTimeout(()=>{
    if(drag!==s||s.interacting)return;
    startDrag();
  },LONG_PRESS_MS);
  e.stopPropagation();
}"""
if old_start not in s: raise SystemExit('onTouchStart marker not found')
s=s.replace(old_start,new_start)

old_move="""  if(!s.interacting){
    if(Math.abs(dx)<DRAG_START_DISTANCE)return;
    // Allow normal finger wobble; only an overwhelmingly vertical gesture is ignored.
    if(Math.abs(dy)>Math.abs(dx)*2.5)return;
    startDrag();
    if(!drag?.interacting)return;
  }
  e.preventDefault();"""
new_move="""  if(!s.interacting){
    // Touch movement does NOT start a drag. The user must hold first.
    // A noticeable move before the hold finishes cancels the pending drag.
    if(Math.hypot(dx,dy)>=LONG_PRESS_CANCEL_DISTANCE){
      clearTimeout(pressTimer);pressTimer=null;
      drag=null;
    }
    return;
  }
  e.preventDefault();"""
if old_move not in s: raise SystemExit('touch move marker not found')
s=s.replace(old_move,new_move,1)

s=s.replace("async function onTouchEnd(e){\n  const s=drag;if(!s||s.inputType!=='touch')return;", "async function onTouchEnd(e){\n  const s=drag;if(!s||s.inputType!=='touch')return;\n  clearTimeout(pressTimer);pressTimer=null;")
s=s.replace("function onTouchCancel(e){\n  const s=drag;if(!s||s.inputType!=='touch')return;", "function onTouchCancel(e){\n  const s=drag;if(!s||s.inputType!=='touch')return;\n  clearTimeout(pressTimer);pressTimer=null;")

s=s.replace("if(hint)hint.textContent='枠を左右にドラッグして移動・タップで編集';", "if(hint)hint.textContent='長押ししてから左右に動かして移動・タップで編集';")
s=s.replace("el.title=`${String(item.start_time).slice(0,5)}〜${String(item.end_time).slice(0,5)} 枠を左右にドラッグして時間移動`;", "el.title=`${String(item.start_time).slice(0,5)}〜${String(item.end_time).slice(0,5)} 長押ししてから左右に動かして時間移動`;" )
s=s.replace("function cancelStaleDrag(){\n  if(!drag)return;", "function cancelStaleDrag(){\n  clearTimeout(pressTimer);pressTimer=null;\n  if(!drag)return;")

p.write_text(s)
