from pathlib import Path

# Strengthen shared blocked drag auto-scroll used by bookings.html.
p=Path('blocked-drag.js')
s=p.read_text(encoding='utf-8')
s=s.replace('const EDGE_ZONE=72;','const EDGE_ZONE=96;',1)
s=s.replace('const MAX_AUTO_SPEED=13;','const MAX_AUTO_SPEED=18;',1)
s=s.replace("speed=-(3+p*MAX_AUTO_SPEED);$('dragEdgeLeft')?.classList.add('show');","speed=-(4+p*MAX_AUTO_SPEED);$('dragEdgeLeft')?.classList.add('show');",1)
s=s.replace("speed=3+p*MAX_AUTO_SPEED;$('dragEdgeRight')?.classList.add('show');","speed=4+p*MAX_AUTO_SPEED;$('dragEdgeRight')?.classList.add('show');",1)
p.write_text(s,encoding='utf-8')

# Add the same continuous edge auto-scroll to the direct admin drag handler.
p=Path('admin.html')
s=p.read_text(encoding='utf-8')

old="""    let nextStart=start;
    let finished=false;

    block.classList.add('directDragging');
    try{handle.setPointerCapture(pointerId)}catch{}

    const move=ev=>{
      if(ev.pointerId!==pointerId||finished)return;
      ev.preventDefault();
      ev.stopPropagation();
      const moved=(ev.clientX-startX+scroll.scrollLeft-startScrollLeft)/PX_PER_MINUTE;
      let candidate=Math.round((start+moved)/15)*15;
      candidate=Math.max(DAY_START,Math.min(DAY_END-duration,candidate));
      nextStart=candidate;
      block.style.left=`${(candidate-DAY_START)*PX_PER_MINUTE}px`;
      handle.textContent=directBlockedTime(candidate).slice(0,5);
      handle.style.fontSize='10px';
    };

    const cleanup=()=>{
      block.classList.remove('directDragging');
      handle.textContent='↔';
      handle.style.fontSize='17px';
      handle.removeEventListener('pointermove',move);
      handle.removeEventListener('pointerup',up);
      handle.removeEventListener('pointercancel',cancel);
      try{handle.releasePointerCapture(pointerId)}catch{}
    };
"""

new="""    let nextStart=start;
    let finished=false;
    let currentX=event.clientX;
    let autoFrame=null;

    const updatePosition=()=>{
      const moved=(currentX-startX+scroll.scrollLeft-startScrollLeft)/PX_PER_MINUTE;
      let candidate=Math.round((start+moved)/15)*15;
      candidate=Math.max(DAY_START,Math.min(DAY_END-duration,candidate));
      nextStart=candidate;
      block.style.left=`${(candidate-DAY_START)*PX_PER_MINUTE}px`;
      handle.textContent=directBlockedTime(candidate).slice(0,5);
      handle.style.fontSize='10px';
    };

    const autoScroll=()=>{
      if(finished)return;
      const rect=scroll.getBoundingClientRect();
      const edge=96;
      let speed=0;
      if(currentX<rect.left+edge){
        const p=Math.max(0,Math.min(1,(rect.left+edge-currentX)/edge));
        speed=-(4+p*18);
      }
      else if(currentX>rect.right-edge){
        const p=Math.max(0,Math.min(1,(currentX-(rect.right-edge))/edge));
        speed=4+p*18;
      }
      if(speed){
        const before=scroll.scrollLeft;
        scroll.scrollLeft+=speed;
        if(before!==scroll.scrollLeft)updatePosition();
      }
      autoFrame=requestAnimationFrame(autoScroll);
    };

    block.classList.add('directDragging');
    try{handle.setPointerCapture(pointerId)}catch{}
    autoFrame=requestAnimationFrame(autoScroll);

    const move=ev=>{
      if(ev.pointerId!==pointerId||finished)return;
      ev.preventDefault();
      ev.stopPropagation();
      currentX=ev.clientX;
      updatePosition();
    };

    const cleanup=()=>{
      if(autoFrame){cancelAnimationFrame(autoFrame);autoFrame=null;}
      block.classList.remove('directDragging');
      handle.textContent='↔';
      handle.style.fontSize='17px';
      handle.removeEventListener('pointermove',move);
      handle.removeEventListener('pointerup',up);
      handle.removeEventListener('pointercancel',cancel);
      try{handle.releasePointerCapture(pointerId)}catch{}
    };
"""

if old not in s:
    raise SystemExit('admin direct drag anchor not found')
s=s.replace(old,new,1)

# Update guidance so the behavior is discoverable.
s=s.replace('タップで予定を変更・削除／右端の↔で時間移動','タップで予定を変更・削除／↔で移動（画面端で自動スクロール）',1)

p.write_text(s,encoding='utf-8')
print('patched drag auto-scroll')
