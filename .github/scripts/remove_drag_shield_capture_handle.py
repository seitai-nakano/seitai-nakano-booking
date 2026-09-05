from pathlib import Path

p=Path('blocked-drag.js')
s=p.read_text()

s=s.replace("let dragShield=null;\n","")
s=s.replace(".blockedDragShield{position:fixed;inset:0;z-index:2147483646;background:transparent;touch-action:none!important;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;overscroll-behavior:none;cursor:grabbing}\n","")

start=s.find("function installDragShield(s){")
end=s.find("function createGhost(s){")
if start!=-1 and end!=-1 and end>start:
    s=s[:start]+s[end:]

s=s.replace("  removeGhost(s);hideDestination();stopAuto();removeDragShield(s);\n","  removeGhost(s);hideDestination();stopAuto();\n  try{s?.captureTarget?.releasePointerCapture?.(s.pointerId)}catch{}\n")
s=s.replace("  installDragShield(s);\n","")

old="""  e.preventDefault();\n  e.stopPropagation();\n  drag={\n    el,item,scroll,pointerId:e.pointerId,pointerType:e.pointerType||'touch',\n"""
new="""  e.preventDefault();\n  e.stopPropagation();\n  const captureTarget=e.currentTarget||e.target;\n  try{captureTarget?.setPointerCapture?.(e.pointerId)}catch{}\n  drag={\n    el,item,scroll,pointerId:e.pointerId,pointerType:e.pointerType||'touch',captureTarget,\n"""
if old not in s:
    raise SystemExit('onHandleDown marker not found')
s=s.replace(old,new,1)

# Keep strong edge autoscroll and explicit bounds.
s=s.replace("const EDGE_ZONE=120;","const EDGE_ZONE=120;")
s=s.replace("const MAX_AUTO_SPEED=24;","const MAX_AUTO_SPEED=24;")

p.write_text(s)
print('removed drag shield and restored handle pointer capture')
