from pathlib import Path

p = Path('blocked-drag.js')
s = p.read_text()

s = s.replace('const EDGE_ZONE=96;\nconst MAX_AUTO_SPEED=18;', 'const EDGE_ZONE=120;\nconst MAX_AUTO_SPEED=24;')

s = s.replace('let hydrateTimer=null;\n', 'let hydrateTimer=null;\nlet dragShield=null;\n')

s = s.replace(
".blockedMoveHandle:active{background:#fff1ef;transform:translateY(-50%) scale(.96)}\n`;",
".blockedMoveHandle:active{background:#fff1ef;transform:translateY(-50%) scale(.96)}\n.blockedDragShield{position:fixed;inset:0;z-index:2147483646;background:transparent;touch-action:none!important;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;overscroll-behavior:none;cursor:grabbing}\n`;"
)

anchor = "function createGhost(s){\n"
insert = """function installDragShield(s){
  removeDragShield();
  const shield=document.createElement('div');
  shield.id='blockedDragShield';
  shield.className='blockedDragShield';
  shield.setAttribute('aria-hidden','true');
  shield.addEventListener('pointerdown',e=>e.preventDefault(),{passive:false});
  document.body.appendChild(shield);
  dragShield=shield;
  try{shield.setPointerCapture(s.pointerId)}catch{}
}

function removeDragShield(s){
  if(!dragShield)return;
  try{dragShield.releasePointerCapture(s?.pointerId)}catch{}
  dragShield.remove();
  dragShield=null;
}

"""
if insert not in s:
    s = s.replace(anchor, insert + anchor)

s = s.replace(
"  removeGhost(s);hideDestination();stopAuto();\n}",
"  removeGhost(s);hideDestination();stopAuto();removeDragShield(s);\n}"
)

s = s.replace(
"  document.body.classList.add('bookingDragging');\n  try{navigator.vibrate?.(18)}catch{}",
"  document.body.classList.add('bookingDragging');\n  installDragShield(s);\n  try{navigator.vibrate?.(18)}catch{}"
)

old = """  if(speed){const before=s.scroll.scrollLeft;s.scroll.scrollLeft+=speed;if(before!==s.scroll.scrollLeft)updateVisual()}
  autoFrame=requestAnimationFrame(autoLoop);"""
new = """  if(speed){
    const before=s.scroll.scrollLeft;
    const maxScroll=Math.max(0,s.scroll.scrollWidth-s.scroll.clientWidth);
    const nextScroll=Math.max(0,Math.min(maxScroll,before+speed));
    s.scroll.scrollLeft=nextScroll;
    if(before!==nextScroll)updateVisual();
  }
  autoFrame=requestAnimationFrame(autoLoop);"""
s = s.replace(old, new)

old2 = """  if(immediate){
    s.scroll.scrollLeft+=immediate;
  }
  updateVisual();"""
new2 = """  if(immediate){
    const maxScroll=Math.max(0,s.scroll.scrollWidth-s.scroll.clientWidth);
    s.scroll.scrollLeft=Math.max(0,Math.min(maxScroll,s.scroll.scrollLeft+immediate));
  }
  updateVisual();"""
s = s.replace(old2, new2)

# Keep the full time axis horizontally scrollable on both admin pages.
for html_name, cls, min_width in [
    ('admin.html', '.scheduleCanvas{', '1800px'),
    ('bookings.html', '.timeline{', '1800px'),
]:
    hp = Path(html_name)
    h = hp.read_text()
    # Only widen; do not disturb the rest of the layout.
    if html_name == 'admin.html':
        h = h.replace('min-width:1680px;', f'min-width:{min_width};')
    else:
        h = h.replace('min-width:1740px;', f'min-width:{min_width};')
    hp.write_text(h)

p.write_text(s)
print('added full-screen drag shield and continuous edge auto-scroll')
