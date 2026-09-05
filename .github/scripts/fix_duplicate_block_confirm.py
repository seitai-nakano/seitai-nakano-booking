from pathlib import Path
p=Path('blocked-drag.js')
s=p.read_text()
s=s.replace("let suppressClickUntil=0;", "let suppressClickUntil=0;\nlet ignorePointerUntil=0;\nlet commitInFlight=false;")
s=s.replace("async function commitDrag(s){\n  const snapped=", "async function commitDrag(s){\n  if(commitInFlight)return;\n  commitInFlight=true;\n  const snapped=")
s=s.replace("  if(snapped===original){\n    restore(s);\n    return;\n  }", "  if(snapped===original){\n    restore(s);\n    commitInFlight=false;\n    return;\n  }")
s=s.replace("  if(!confirm(`${oldLabel} → ${newLabel}（〜${endLabel}）に予定を移動しますか？`)){\n    restore(s);\n    return;\n  }", "  if(!confirm(`${oldLabel} → ${newLabel}（〜${endLabel}）に予定を移動しますか？`)){\n    restore(s);\n    commitInFlight=false;\n    return;\n  }")
s=s.replace("    alert('その時間には移動できません。予約・別の予定を確認してください。');\n    return;", "    alert('その時間には移動できません。予約・別の予定を確認してください。');\n    commitInFlight=false;\n    return;")
s=s.replace("function startTouch(e,el){\n  if(gesture||e.touches.length!==1)return;", "function startTouch(e,el){\n  ignorePointerUntil=Date.now()+2200;\n  if(gesture||e.touches.length!==1)return;")
s=s.replace("async function endTouch(e){\n  const s=gesture;", "async function endTouch(e){\n  ignorePointerUntil=Date.now()+2200;\n  const s=gesture;")
s=s.replace("function cancelTouch(e){\n  const s=gesture;", "function cancelTouch(e){\n  ignorePointerUntil=Date.now()+2200;\n  const s=gesture;")
s=s.replace("function startPointer(e,el){\n  if(e.pointerType==='touch'||gesture||(e.pointerType==='mouse'&&e.button!==0))return;", "function startPointer(e,el){\n  if(Date.now()<ignorePointerUntil||e.pointerType==='touch'||gesture||(e.pointerType==='mouse'&&e.button!==0))return;")
assert 'commitInFlight=true' in s
assert 'ignorePointerUntil=Date.now()+2200' in s
p.write_text(s)
