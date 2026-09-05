import {createClient} from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm';

const supabase=createClient(
  'https://scjzofjyxmchfjsngqtb.supabase.co',
  'sb_publishable_EGlr-6w0xh4gD8OImboE_Q_V-COJ7t9'
);

const DAY_START=8*60;
const PX_PER_MINUTE=2;
const SNAP_MINUTES=15;
const LONG_PRESS_MS=450;
const MOVE_THRESHOLD=12;
const EDGE_ZONE=96;
const EDGE_MAX_SPEED=18;

let gesture=null;
let pressTimer=null;
let autoFrame=null;
let suppressClickUntil=0;
let ignorePointerUntil=0;
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
function findTouch(list,id){
  for(let i=0;i<list.length;i++)if(list[i].identifier===id)return list[i];
  return null;
}

function addStyles(){
  if($('nakanoBlockedDragStyleV2'))return;
  const style=document.createElement('style');
  style.id='nakanoBlockedDragStyleV2';
  style.textContent=`
${blockedSelector}{
  -webkit-touch-callout:none!important;
  -webkit-user-select:none!important;
  user-select:none!important;
  touch-action:none!important;
  cursor:grab!important;
  transform:none!important;
  box-shadow:none!important;
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
function hideDestination(){
  $('dragDestinationSlot')?.classList.remove('show');
}

function stopAuto(){
  if(autoFrame){cancelAnimationFrame(autoFrame);autoFrame=null}
}

function stateFromElement(el,x,y,inputType,extra={}){
  const id=el.dataset.blockedId;
  const scroll=el.closest('.timelineScroll,.scheduleScroll');
  if(!id||!scroll)return null;

  const left=parseFloat(el.style.left)||0;
  const width=Math.max(30,parseFloat(el.style.width)||30);
  const start=DAY_START+left/PX_PER_MINUTE;
  const duration=Math.max(SNAP_MINUTES,snapMinutes(width/PX_PER_MINUTE));
  const timelineEnd=DAY_START+scroll.scrollWidth/PX_PER_MINUTE;

  if(start<DAY_START||duration<=0||start+duration>timelineEnd+SNAP_MINUTES)return null;

  return{
    el,
    id:String(id),
    scroll,
    inputType,
    ...extra,
    mode:'pending',
    startX:x,
    startY:y,
    currentX:x,
    currentY:y,
    startScrollLeft:scroll.scrollLeft,
    originalLeft:left,
    originalStart:start,
    duration,
    timelineEnd,
    visualStart:start,
    newStart:snapMinutes(start)
  };
}

function clearPress(){
  if(pressTimer){clearTimeout(pressTimer);pressTimer=null}
}

function beginDrag(s){
  if(gesture!==s||s.mode!=='pending')return;
  s.mode='drag';
  s.startX=s.currentX;
  s.startY=s.currentY;
  s.startScrollLeft=s.scroll.scrollLeft;
  s.originalStart=DAY_START+s.originalLeft/PX_PER_MINUTE;
  s.visualStart=s.originalStart;
  s.newStart=snapMinutes(s.originalStart);
  s.el.classList.add('blockedDragging');
  document.body.classList.add('bookingDragging');
  try{navigator.vibrate?.(25)}catch{}
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
  const maxStart=s.timelineEnd-s.duration;
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
  clearPress();
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
  const snapped=clamp(snapMinutes(s.newStart),DAY_START,s.timelineEnd-s.duration);
  s.el.style.left=`${(snapped-DAY_START)*PX_PER_MINUTE}px`;
  cleanup(s);
  suppressClickUntil=Date.now()+900;

  const original=snapMinutes(s.originalStart);
  if(snapped===original){
    restore(s);
    commitInFlight=false;
    return;
  }

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

function startTouch(e,el){
  ignorePointerUntil=Date.now()+2200;
  if(gesture||e.touches.length!==1)return;
  const t=e.changedTouches[0];
  const s=stateFromElement(el,t.clientX,t.clientY,'touch',{touchId:t.identifier});
  if(!s)return;
  gesture=s;
  clearPress();
  pressTimer=setTimeout(()=>beginDrag(s),LONG_PRESS_MS);
}

function moveTouch(e){
  const s=gesture;
  if(!s||s.inputType!=='touch')return;
  const t=findTouch(e.touches,s.touchId)||findTouch(e.changedTouches,s.touchId);
  if(!t)return;

  s.currentX=t.clientX;
  s.currentY=t.clientY;
  const dx=s.currentX-s.startX;
  const dy=s.currentY-s.startY;

  if(s.mode==='pending'){
    if(Math.abs(dx)>=MOVE_THRESHOLD&&Math.abs(dx)>=Math.abs(dy)){
      clearPress();
      s.mode='scroll';
    }else if(Math.abs(dy)>=MOVE_THRESHOLD&&Math.abs(dy)>Math.abs(dx)){
      clearPress();
      s.mode='cancelled';
      return;
    }else{
      return;
    }
  }

  if(s.mode==='scroll'){
    e.preventDefault();
    e.stopPropagation();
    const maxScroll=Math.max(0,s.scroll.scrollWidth-s.scroll.clientWidth);
    // Requested direction: moving the finger to the right moves the viewport to later/right times.
    s.scroll.scrollLeft=clamp(s.startScrollLeft+dx,0,maxScroll);
    return;
  }

  if(s.mode==='drag'){
    e.preventDefault();
    e.stopPropagation();
    updateDragVisual(s);
  }
}

async function endTouch(e){
  ignorePointerUntil=Date.now()+2200;
  const s=gesture;
  if(!s||s.inputType!=='touch')return;
  const t=findTouch(e.changedTouches,s.touchId);
  if(!t)return;

  clearPress();
  gesture=null;

  if(s.mode==='drag'){
    e.preventDefault();
    await commitDrag(s);
    return;
  }

  if(s.mode==='scroll'){
    e.preventDefault();
    suppressClickUntil=Date.now()+500;
  }
}

function cancelTouch(e){
  ignorePointerUntil=Date.now()+2200;
  const s=gesture;
  if(!s||s.inputType!=='touch')return;
  const t=findTouch(e.changedTouches,s.touchId);
  if(!t)return;
  gesture=null;
  clearPress();
  if(s.mode==='drag')restore(s);
  cleanup(s);
}

function startPointer(e,el){
  if(Date.now()<ignorePointerUntil||e.pointerType==='touch'||gesture||(e.pointerType==='mouse'&&e.button!==0))return;
  const s=stateFromElement(el,e.clientX,e.clientY,'pointer',{pointerId:e.pointerId});
  if(!s)return;
  s.mode='drag';
  gesture=s;
  try{el.setPointerCapture?.(e.pointerId)}catch{}
  s.el.classList.add('blockedDragging');
  document.body.classList.add('bookingDragging');
  autoFrame=requestAnimationFrame(autoScrollLoop);
}

function movePointer(e){
  const s=gesture;
  if(!s||s.inputType!=='pointer'||s.pointerId!==e.pointerId)return;
  s.currentX=e.clientX;
  s.currentY=e.clientY;
  e.preventDefault();
  updateDragVisual(s);
}

async function endPointer(e){
  const s=gesture;
  if(!s||s.inputType!=='pointer'||s.pointerId!==e.pointerId)return;
  gesture=null;
  try{s.el.releasePointerCapture?.(s.pointerId)}catch{}
  await commitDrag(s);
}

function cancelGesture(){
  const s=gesture;
  gesture=null;
  clearPress();
  if(s?.mode==='drag')restore(s);
  cleanup(s);
}

if(supportedPage()){
  addStyles();

  document.addEventListener('touchstart',e=>{
    const el=e.target.closest?.(blockedSelector);
    if(el)startTouch(e,el);
  },{passive:true,capture:true});

  document.addEventListener('touchmove',moveTouch,{passive:false,capture:true});
  document.addEventListener('touchend',endTouch,{passive:false,capture:true});
  document.addEventListener('touchcancel',cancelTouch,{passive:false,capture:true});

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

  window.addEventListener('blur',cancelGesture);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)cancelGesture()});
}
