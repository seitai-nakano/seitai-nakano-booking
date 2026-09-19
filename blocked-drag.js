import {createClient} from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm';

const supabase=createClient(
  'https://scjzofjyxmchfjsngqtb.supabase.co',
  'sb_publishable_EGlr-6w0xh4gD8OImboE_Q_V-COJ7t9'
);

const DAY_START=8*60;
const DAY_END=22*60;
const PX_PER_MINUTE=2;
const SNAP_MINUTES=15;
const MOVE_THRESHOLD=7;
const EDGE_ZONE=96;
const EDGE_MAX_SPEED=18;

let gesture=null;
let autoFrame=null;
let suppressClickUntil=0;
let commitInFlight=false;

const $=id=>document.getElementById(id);
const blockedSelector='.blockedSchedule,.blockedBlock';
const supportedPage=()=>location.pathname.endsWith('/admin.html')||location.pathname.endsWith('/bookings.html')||location.pathname.endsWith('/');

function timeFromMinutes(n){
  const v=Math.max(0,Math.round(n));
  return `${String(Math.floor(v/60)).padStart(2,'0')}:${String(v%60).padStart(2,'0')}:00`;
}
function snapMinutes(n){return Math.round(n/SNAP_MINUTES)*SNAP_MINUTES}
function clamp(v,min,max){return Math.max(min,Math.min(max,v))}

function addStyles(){
  if($('nakanoBlockedDragStyleV3'))return;
  $('nakanoBlockedDragStyleV2')?.remove();
  const style=document.createElement('style');
  style.id='nakanoBlockedDragStyleV3';
  style.textContent=`
${blockedSelector}{
  -webkit-touch-callout:none!important;
  -webkit-user-select:none!important;
  user-select:none!important;
  touch-action:pan-y!important;
  cursor:grab!important;
  transform:none!important;
  opacity:1!important;
  filter:none!important;
  transition:transform .10s ease,box-shadow .10s ease,opacity .10s ease!important;
}
${blockedSelector}.blockedDragging{
  z-index:160!important;
  opacity:.98!important;
  transform:translateY(-4px) scale(1.025)!important;
  box-shadow:0 3px 0 rgba(138,74,66,.18),0 12px 28px rgba(0,0,0,.24)!important;
  transition:none!important;
  will-change:left,transform!important;
  cursor:grabbing!important;
  touch-action:none!important;
}
`;
  document.head.appendChild(style);
}

function destination(text,show=true){
  let slot=$('dragDestinationSlot');
  const scroll=gesture?.scroll||document.querySelector('.timelineScroll,.scheduleScroll');
  if(!slot&&scroll){
    slot=document.createElement('div');
    slot.id='dragDestinationSlot';
    slot.className='dragDestinationSlot';
    slot.innerHTML='<div class="dragDestinationPill"><span class="dragDestinationLabel">移動先</span><span class="dragDestinationTime">--:--</span></div>';
    scroll.insertAdjacentElement('beforebegin',slot);
  }
  if(!slot)return;
  const time=slot.querySelector('.dragDestinationTime');
  if(time)time.textContent=text;
  slot.classList.toggle('show',show);
}
function hideDestination(){$('dragDestinationSlot')?.classList.remove('show')}

function stopAuto(){
  if(autoFrame){cancelAnimationFrame(autoFrame);autoFrame=null}
}

function stateFromElement(el,e){
  const id=el.dataset.blockedId;
  const scroll=el.closest('.timelineScroll,.scheduleScroll');
  if(!id||!scroll)return null;

  const left=parseFloat(el.style.left)||0;
  const width=Math.max(30,parseFloat(el.style.width)||30);
  const start=DAY_START+left/PX_PER_MINUTE;
  const duration=Math.max(SNAP_MINUTES,snapMinutes(width/PX_PER_MINUTE));

  if(start<DAY_START||duration<=0||duration>DAY_END-DAY_START)return null;

  return{
    el,
    id:String(id),
    scroll,
    pointerId:e.pointerId,
    pointerType:e.pointerType,
    mode:'pending',
    startX:e.clientX,
    startY:e.clientY,
    currentX:e.clientX,
    currentY:e.clientY,
    startScrollLeft:scroll.scrollLeft,
    originalLeft:left,
    originalStart:start,
    duration,
    visualStart:start,
    newStart:snapMinutes(start)
  };
}

function beginDrag(s){
  if(gesture!==s||s.mode!=='pending')return;
  s.mode='drag';
  s.el.classList.add('blockedDragging');
  document.body.classList.add('bookingDragging');
  try{navigator.vibrate?.(18)}catch{}
  const st=timeFromMinutes(s.newStart).slice(0,5);
  const en=timeFromMinutes(s.newStart+s.duration).slice(0,5);
  destination(`${st}–${en}`);
  stopAuto();
  autoFrame=requestAnimationFrame(autoScrollLoop);
}

function updateDragVisual(s){
  if(gesture!==s||s.mode!=='drag')return;
  const dx=s.currentX-s.startX;
  const scrollDelta=s.scroll.scrollLeft-s.startScrollLeft;
  const movedMinutes=(dx+scrollDelta)/PX_PER_MINUTE;
  const maxStart=DAY_END-s.duration;
  const visual=clamp(s.originalStart+movedMinutes,DAY_START,maxStart);
  const snapped=clamp(snapMinutes(visual),DAY_START,maxStart);

  s.visualStart=visual;
  s.newStart=snapped;
  s.el.style.left=`${(visual-DAY_START)*PX_PER_MINUTE}px`;

  const st=timeFromMinutes(snapped).slice(0,5);
  const en=timeFromMinutes(snapped+s.duration).slice(0,5);
  destination(`${st}–${en}`);
}

function autoScrollLoop(){
  const s=gesture;
  if(!s||s.mode!=='drag'){stopAuto();return}

  const rect=s.scroll.getBoundingClientRect();
  const x=s.currentX;
  let speed=0;

  if(x<rect.left+EDGE_ZONE){
    const p=clamp((rect.left+EDGE_ZONE-x)/EDGE_ZONE,0,1);
    speed=-(4+p*EDGE_MAX_SPEED);
  }else if(x>rect.right-EDGE_ZONE){
    const p=clamp((x-(rect.right-EDGE_ZONE))/EDGE_ZONE,0,1);
    speed=4+p*EDGE_MAX_SPEED;
  }

  if(speed){
    const maxScroll=Math.max(0,s.scroll.scrollWidth-s.scroll.clientWidth);
    const before=s.scroll.scrollLeft;
    s.scroll.scrollLeft=clamp(before+speed,0,maxScroll);
    if(s.scroll.scrollLeft!==before)updateDragVisual(s);
  }

  autoFrame=requestAnimationFrame(autoScrollLoop);
}

function cleanup(s){
  stopAuto();
  s?.el?.classList.remove('blockedDragging');
  document.body.classList.remove('bookingDragging');
  hideDestination();
}

function restore(s){
  if(!s)return;
  s.el.style.left=`${s.originalLeft}px`;
}

async function commitDrag(s){
  if(commitInFlight)return;
  commitInFlight=true;
  const snapped=clamp(snapMinutes(s.newStart),DAY_START,DAY_END-s.duration);
  s.el.style.left=`${(snapped-DAY_START)*PX_PER_MINUTE}px`;
  cleanup(s);

  const original=snapMinutes(s.originalStart);
  if(snapped===original){
    restore(s);
    commitInFlight=false;
    return;
  }

  suppressClickUntil=Date.now()+900;

  const oldLabel=timeFromMinutes(original).slice(0,5);
  const newLabel=timeFromMinutes(snapped).slice(0,5);
  const endLabel=timeFromMinutes(snapped+s.duration).slice(0,5);

  if(!confirm(`${oldLabel} → ${newLabel}（〜${endLabel}）に予定を移動しますか？`)){
    restore(s);
    commitInFlight=false;
    return;
  }

  const {error}=await supabase.rpc('nakano_admin_move_blocked_time',{
    p_blocked_id:s.id,
    p_start_time:timeFromMinutes(snapped)
  });

  if(error){
    console.error(error);
    restore(s);
    alert('その時間には移動できません。予約・別の予定を確認してください。');
    commitInFlight=false;
    return;
  }

  setTimeout(()=>location.reload(),120);
}

function startPointer(e,el){
  if(gesture||!e.isPrimary||(e.pointerType==='mouse'&&e.button!==0))return;
  const s=stateFromElement(el,e);
  if(!s)return;
  gesture=s;
  try{el.setPointerCapture?.(e.pointerId)}catch{}
}

function movePointer(e){
  const s=gesture;
  if(!s||s.pointerId!==e.pointerId)return;

  s.currentX=e.clientX;
  s.currentY=e.clientY;
  const dx=s.currentX-s.startX;
  const dy=s.currentY-s.startY;

  if(s.mode==='pending'){
    if(Math.hypot(dx,dy)<MOVE_THRESHOLD)return;

    if(Math.abs(dx)>=Math.abs(dy)){
      beginDrag(s);
    }else{
      s.mode='cancelled';
      return;
    }
  }

  if(s.mode==='drag'){
    if(e.cancelable)e.preventDefault();
    e.stopPropagation();
    updateDragVisual(s);
  }
}

async function endPointer(e){
  const s=gesture;
  if(!s||s.pointerId!==e.pointerId)return;
  gesture=null;

  try{s.el.releasePointerCapture?.(s.pointerId)}catch{}

  if(s.mode==='drag'){
    if(e.cancelable)e.preventDefault();
    e.stopPropagation();
    await commitDrag(s);
    return;
  }

  cleanup(s);
}

function cancelGesture(e){
  const s=gesture;
  if(!s)return;
  if(e?.pointerId!=null&&s.pointerId!==e.pointerId)return;
  gesture=null;
  try{s.el.releasePointerCapture?.(s.pointerId)}catch{}
  if(s.mode==='drag')restore(s);
  cleanup(s);
}

if(supportedPage()){
  addStyles();

  document.addEventListener('pointerdown',e=>{
    const el=e.target.closest?.(blockedSelector);
    if(el)startPointer(e,el);
  },true);

  window.addEventListener('pointermove',movePointer,{passive:false});
  window.addEventListener('pointerup',endPointer,{passive:false});
  window.addEventListener('pointercancel',cancelGesture,{passive:false});

  document.addEventListener('click',e=>{
    if(Date.now()<suppressClickUntil&&e.target.closest?.(blockedSelector)){
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
    }
  },true);

  document.addEventListener('contextmenu',e=>{
    if(e.target.closest?.(blockedSelector))e.preventDefault();
  },true);

  window.addEventListener('blur',()=>cancelGesture());
  document.addEventListener('visibilitychange',()=>{if(document.hidden)cancelGesture()});
}
