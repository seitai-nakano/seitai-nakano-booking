from pathlib import Path
p=Path('blocked-drag.js')
s=p.read_text()
old="""function updateVisual(){
  const s=drag;if(!s?.interacting)return;
  const moved=(s.currentX-s.startX+s.scroll.scrollLeft-s.startScrollLeft)/PX_PER_MINUTE;
  let next=snap(s.originalStart+moved);
  next=Math.max(DAY_START,Math.min(DAY_END-s.duration,next));
  s.newStart=next;
  s.el.style.left=`${(next-DAY_START)*PX_PER_MINUTE}px`;
  const st=minutesToTime(next).slice(0,5);
  const en=minutesToTime(next+s.duration).slice(0,5);
  destination(`${st}–${en}`);
}
"""
new="""function updateVisual(){
  const s=drag;if(!s?.interacting)return;
  const movedMinutes=(s.currentX-s.startX+s.scroll.scrollLeft-s.startScrollLeft)/PX_PER_MINUTE;
  let visualStart=s.originalStart+movedMinutes;
  visualStart=Math.max(DAY_START,Math.min(DAY_END-s.duration,visualStart));
  let snappedStart=snap(visualStart);
  snappedStart=Math.max(DAY_START,Math.min(DAY_END-s.duration,snappedStart));
  s.visualStart=visualStart;
  s.newStart=snappedStart;
  // The actual red block follows the finger continuously.
  s.el.style.left=`${(visualStart-DAY_START)*PX_PER_MINUTE}px`;
  const st=minutesToTime(snappedStart).slice(0,5);
  const en=minutesToTime(snappedStart+s.duration).slice(0,5);
  destination(`${st}–${en}`);
}
"""
if old not in s: raise SystemExit('updateVisual pattern not found')
s=s.replace(old,new)
s=s.replace("  createGhost(s);\n  s.el.classList.add('blockedDragging');","  // Move the actual block itself; do not leave a duplicate ghost behind.\n  s.el.classList.add('blockedDragging');")
old2="""  suppressClickUntil=Date.now()+900;
  cleanup(s);
  if(s.newStart===s.originalStart){restore(s);return}
"""
new2="""  suppressClickUntil=Date.now()+900;
  // Snap the visible block to the final 15-minute slot before confirming.
  s.el.style.left=`${(s.newStart-DAY_START)*PX_PER_MINUTE}px`;
  cleanup(s);
  if(s.newStart===s.originalStart){restore(s);return}
"""
if old2 not in s: raise SystemExit('onUp pattern not found')
s=s.replace(old2,new2)
s=s.replace(".blockedSchedule.blockedDragging,.blockedBlock.blockedDragging{z-index:110!important;opacity:.96;box-shadow:0 0 0 3px rgba(138,74,66,.24),0 9px 26px rgba(0,0,0,.22)!important;transform:translateY(8px) scale(1.02);touch-action:none!important}",".blockedSchedule.blockedDragging,.blockedBlock.blockedDragging{z-index:110!important;opacity:.98;box-shadow:0 0 0 3px rgba(138,74,66,.24),0 9px 26px rgba(0,0,0,.22)!important;transform:translateY(8px) scale(1.02);touch-action:none!important;transition:none!important;will-change:left}")
p.write_text(s)
print('patched continuous actual-block drag')
