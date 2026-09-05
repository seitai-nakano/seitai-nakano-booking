import {createClient} from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm';

const supabase=createClient(
  'https://scjzofjyxmchfjsngqtb.supabase.co',
  'sb_publishable_EGlr-6w0xh4gD8OImboE_Q_V-COJ7t9'
);

const DAY_START=8*60;
const DAY_END=23*60;
const PX_PER_MINUTE=2;
const SNAP_MINUTES=15;
const DRAG_START_DISTANCE=4;
const LONG_PRESS_MS=420;
const LONG_PRESS_CANCEL_DISTANCE=10;
const EDGE_ZONE=120;
const MAX_AUTO_SPEED=24;

let rows=[];
let rowsDate='';
let drag=null;
let pressTimer=null;
let autoFrame=null;
let suppressClickUntil=0;
let hydrateTimer=null;

const $=id=>document.getElementById(id);
const selectedDate=()=>$('date')?.value||'';
const scheduleScroll=()=>document.querySelector('.timelineScroll,.scheduleScroll');
const supportedPage=()=>location.pathname.endsWith('/admin.html')||location.pathname.endsWith('/bookings.html')||location.pathname.endsWith('/');

function timeToMinutes(t){
  const [h,m]=String(t||'').slice(0,5).split(':').map(Number);
  return h*60+m;
}
function blockEndMinutes(t){return String(t||'').startsWith('23:59')?24*60:timeToMinutes(t)}
function minutesToTime(n){return `${String(Math.floor(n/60)).padStart(2,'0')}:${String(n%60).padStart(2,'0')}:00`}
function snap(v){return Math.round(v/SNAP_MINUTES)*SNAP_MINUTES}
function range(item){const start=timeToMinutes(item?.start_time),end=blockEndMinutes(item?.end_time);return{start,end,duration:end-start}}
function movable(item){const r=range(item);return !!item?.id&&r.duration>0&&r.start>=DAY_START&&r.end<=DAY_END&&!(r.start===0&&r.end>=24*60)}

function addStyles(){
  if($('nakanoBlockedDragStyle'))return;
  const s=document.createElement('style');
  s.id='nakanoBlockedDragStyle';
  s.textContent=`
.blockedSchedule,.blockedBlock{-webkit-touch-callout:none;touch-action:none;cursor:grab;-webkit-user-select:none;user-select:none}
.blockedSchedule.blockedDragging,.blockedBlock.blockedDragging{z-index:110!important;opacity:.98;box-shadow:0 0 0 3px rgba(138,74,66,.24),0 9px 26px rgba(0,0,0,.22)!important;transform:translateY(8px) scale(1.02);touch-action:none!important;transition:none!important;will-change:left;cursor:grabbing}
`;
  document.head.appendChild(s);
}

function destination(text,show=true){
  let slot=$('dragDestinationSlot');
  if(!slot){
    const scroll=scheduleScroll();
    if(!scroll)return;
    slot=document.createElement('div');
    slot.id='dragDestinationSlot';
    slot.className='dragDestinationSlot';
    slot.innerHTML='<div class="dragDestinationPill"><span class="dragDestinationLabel">変更先</span><span class="dragDestinationTime">--:--</span></div>';
    scroll.insertAdjacentElement('beforebegin',slot);
  }
  const t=slot.querySelector('.dragDestinationTime');
  if(t)t.textContent=text;
  slot.classList.toggle('show',show);
}
function hideDestination(){$('dragDestinationSlot')?.classList.remove('show')}
function hideEdges(){$('dragEdgeLeft')?.classList.remove('show');$('dragEdgeRight')?.classList.remove('show')}

function inferRow(el){
  const id=el.dataset.blockedId;
  if(id){const found=rows.find(r=>String(r.id)===String(id));if(found)return found}
  const left=parseFloat(el.style.left)||0;
  const width=parseFloat(el.style.width)||0;
  const start=Math.round(DAY_START+left/PX_PER_MINUTE);
  const duration=Math.max(15,Math.round((width/PX_PER_MINUTE)/15)*15);
  let best=null,bestScore=Infinity;
  for(const r of rows){
    const rr=range(r);
    const score=Math.abs(rr.start-start)*8+Math.abs(rr.duration-duration);
    if(score<bestScore){best=r;bestScore=score}
  }
  return bestScore<=75?best:null;
}

async function fetchRows(force=false){
  const date=selectedDate();
  if(!date)return[];
  if(!force&&rowsDate===date)return rows;
  const {data,error}=await supabase
    .from('nakano_blocked_times')
    .select('id,blocked_date,start_time,end_time,memo')
    .eq('blocked_date',date)
    .order('start_time');
  if(error){console.warn('予約不可時間の取得に失敗',error);return[]}
  rows=data||[];
  rowsDate=date;
  return rows;
}

function stopAuto(){if(autoFrame){cancelAnimationFrame(autoFrame);autoFrame=null}hideEdges()}
function cleanup(s){
  clearTimeout(pressTimer);pressTimer=null;
  s?.el?.classList.remove('blockedDragging');
  document.body.classList.remove('bookingDragging');
  hideDestination();
  stopAuto();
  if(s?.inputType==='pointer'){
    try{s.captureTarget?.releasePointerCapture?.(s.pointerId)}catch{}
  }
}
function restore(s){if(!s)return;s.el.style.left=`${s.originalLeft}px`;s.el.style.width=`${s.originalWidth}px`}

function updateVisual(){
  const s=drag;if(!s?.interacting)return;
  const movedMinutes=(s.currentX-s.startX+s.scroll.scrollLeft-s.startScrollLeft)/PX_PER_MINUTE;
  let visualStart=s.originalStart+movedMinutes;
  visualStart=Math.max(DAY_START,Math.min(DAY_END-s.duration,visualStart));
  let snappedStart=snap(visualStart);
  snappedStart=Math.max(DAY_START,Math.min(DAY_END-s.duration,snappedStart));
  s.visualStart=visualStart;
  s.newStart=snappedStart;
  s.el.style.left=`${(visualStart-DAY_START)*PX_PER_MINUTE}px`;
  const st=minutesToTime(snappedStart).slice(0,5);
  const en=minutesToTime(snappedStart+s.duration).slice(0,5);
  destination(`${st}–${en}`);
}

function autoLoop(){
  const s=drag;if(!s?.interacting){stopAuto();return}
  const rect=s.scroll.getBoundingClientRect(),x=s.currentX;
  const ld=x-rect.left,rd=rect.right-x;
  let speed=0;hideEdges();
  if(ld<EDGE_ZONE){
    const p=Math.max(0,Math.min(1,(EDGE_ZONE-ld)/EDGE_ZONE));
    speed=-(4+p*MAX_AUTO_SPEED);$('dragEdgeLeft')?.classList.add('show');
  }else if(rd<EDGE_ZONE){
    const p=Math.max(0,Math.min(1,(EDGE_ZONE-rd)/EDGE_ZONE));
    speed=4+p*MAX_AUTO_SPEED;$('dragEdgeRight')?.classList.add('show');
  }
  if(speed){
    const before=s.scroll.scrollLeft;
    const maxScroll=Math.max(0,s.scroll.scrollWidth-s.scroll.clientWidth);
    const nextScroll=Math.max(0,Math.min(maxScroll,before+speed));
    s.scroll.scrollLeft=nextScroll;
    if(before!==nextScroll)updateVisual();
  }
  autoFrame=requestAnimationFrame(autoLoop);
}

function startDrag(){
  const s=drag;if(!s||s.interacting)return;
  s.interacting=true;
  $('blockedInlineEditor')?.classList.remove('open');
  s.el.classList.add('blockedDragging');
  document.body.classList.add('bookingDragging');
  try{navigator.vibrate?.(18)}catch{}
  const st=minutesToTime(s.originalStart).slice(0,5),en=minutesToTime(s.originalStart+s.duration).slice(0,5);
  destination(`${st}–${en}`);
  autoFrame=requestAnimationFrame(autoLoop);
}

function createDragState(el,item,x,y,inputType,extra={}){
  const scroll=el.closest('.timelineScroll,.scheduleScroll');
  if(!scroll||!movable(item))return null;
  const r=range(item);
  return{
    el,item,scroll,inputType,...extra,
    startX:x,startY:y,currentX:x,currentY:y,
    startScrollLeft:scroll.scrollLeft,
    originalStart:r.start,newStart:r.start,duration:r.duration,
    originalLeft:parseFloat(el.style.left)||((r.start-DAY_START)*PX_PER_MINUTE),
    originalWidth:parseFloat(el.style.width)||Math.max(36,r.duration*PX_PER_MINUTE),
    interacting:false
  };
}

function edgeNudge(s){
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
}

async function finishDrag(s){
  if(!s?.interacting)return;
  suppressClickUntil=Date.now()+900;
  s.el.style.left=`${(s.newStart-DAY_START)*PX_PER_MINUTE}px`;
  cleanup(s);
  if(s.newStart===s.originalStart){restore(s);return}
  const oldStart=minutesToTime(s.originalStart).slice(0,5);
  const newStart=minutesToTime(s.newStart).slice(0,5);
  const newEnd=minutesToTime(s.newStart+s.duration).slice(0,5);
  if(!confirm(`${oldStart} → ${newStart}（〜${newEnd}）に予約不可／予定を移動しますか？`)){restore(s);return}
  const {error}=await supabase.rpc('nakano_admin_move_blocked_time',{
    p_blocked_id:String(s.item.id),
    p_start_time:minutesToTime(s.newStart)
  });
  if(error){
    console.error(error);
    alert('その時間には移動できません。予約・別の予定を確認してください。');
    restore(s);return;
  }
  setTimeout(()=>location.reload(),160);
}

// iPhone / touch devices: use native Touch Events instead of Pointer Events.
function onTouchStart(e,el,item){
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
}

function findTouch(list,id){
  for(let i=0;i<list.length;i++)if(list[i].identifier===id)return list[i];
  return null;
}

function onTouchMove(e){
  const s=drag;if(!s||s.inputType!=='touch')return;
  const t=findTouch(e.touches,s.touchId)||findTouch(e.changedTouches,s.touchId);
  if(!t)return;
  s.currentX=t.clientX;s.currentY=t.clientY;
  const dx=s.currentX-s.startX,dy=s.currentY-s.startY;
  if(!s.interacting){
    // Touch movement does NOT start a drag. The user must hold first.
    // A noticeable move before the hold finishes cancels the pending drag.
    if(Math.hypot(dx,dy)>=LONG_PRESS_CANCEL_DISTANCE){
      clearTimeout(pressTimer);pressTimer=null;
      drag=null;
    }
    return;
  }
  e.preventDefault();
  e.stopPropagation();
  edgeNudge(s);
  updateVisual();
}

async function onTouchEnd(e){
  const s=drag;if(!s||s.inputType!=='touch')return;
  clearTimeout(pressTimer);pressTimer=null;
  const t=findTouch(e.changedTouches,s.touchId);
  if(!t)return;
  if(s.interacting)e.preventDefault();
  drag=null;
  if(!s.interacting)return;
  await finishDrag(s);
}

function onTouchCancel(e){
  const s=drag;if(!s||s.inputType!=='touch')return;
  clearTimeout(pressTimer);pressTimer=null;
  const t=findTouch(e.changedTouches,s.touchId);
  if(!t)return;
  drag=null;
  if(s.interacting){restore(s);cleanup(s)}
}

// Mouse / pen: Pointer Events remain fine and give precise desktop dragging.
function onPointerDown(e,el,item){
  if(e.pointerType==='touch'||drag||(e.pointerType==='mouse'&&e.button!==0))return;
  const s=createDragState(el,item,e.clientX,e.clientY,'pointer',{
    pointerId:e.pointerId,captureTarget:el,pointerType:e.pointerType||'mouse'
  });
  if(!s)return;
  try{el.setPointerCapture?.(e.pointerId)}catch{}
  drag=s;
}

function onPointerMove(e){
  const s=drag;if(!s||s.inputType!=='pointer'||s.pointerId!==e.pointerId)return;
  s.currentX=e.clientX;s.currentY=e.clientY;
  const dx=s.currentX-s.startX,dy=s.currentY-s.startY;
  if(!s.interacting){
    if(Math.abs(dx)<DRAG_START_DISTANCE)return;
    if(Math.abs(dy)>Math.abs(dx)*2.5)return;
    startDrag();
    if(!drag?.interacting)return;
  }
  e.preventDefault();
  edgeNudge(s);
  updateVisual();
}

async function onPointerUp(e){
  const s=drag;if(!s||s.inputType!=='pointer'||s.pointerId!==e.pointerId)return;
  drag=null;
  if(!s.interacting){
    try{s.captureTarget?.releasePointerCapture?.(s.pointerId)}catch{}
    return;
  }
  await finishDrag(s);
}

function onPointerCancel(e){
  const s=drag;if(!s||s.inputType!=='pointer'||s.pointerId!==e.pointerId)return;
  drag=null;
  if(s.interacting){restore(s);cleanup(s)}
}

function attach(el,item){
  el.style.touchAction='none';
  el.querySelector('.blockedMoveHandle')?.remove();
  const hint=el.querySelector('.blockedTapHint');
  if(!movable(item)){
    if(hint)hint.textContent='タップで時間変更';
    return;
  }
  if(hint)hint.textContent='長押ししてから左右に動かして移動・タップで編集';
  el.title=`${String(item.start_time).slice(0,5)}〜${String(item.end_time).slice(0,5)} 長押ししてから左右に動かして時間移動`;
  if(el.dataset.boundBlockMove!=='1'){
    el.dataset.boundBlockMove='1';
    el.addEventListener('touchstart',e=>onTouchStart(e,el,item),{passive:false});
    el.addEventListener('pointerdown',e=>onPointerDown(e,el,item));
    el.addEventListener('contextmenu',e=>e.preventDefault());
  }
}

async function hydrate(force=false){
  if(!supportedPage())return;
  await fetchRows(force);
  document.querySelectorAll('.blockedSchedule,.blockedBlock').forEach(el=>{
    const item=inferRow(el);if(item)attach(el,item);
  });
}

function queueHydrate(force=false){
  clearTimeout(hydrateTimer);
  hydrateTimer=setTimeout(()=>hydrate(force),120);
}

function cancelStaleDrag(){
  clearTimeout(pressTimer);pressTimer=null;
  if(!drag)return;
  const s=drag;drag=null;
  if(s.interacting){restore(s);cleanup(s)}
  else if(s.inputType==='pointer')try{s.captureTarget?.releasePointerCapture?.(s.pointerId)}catch{}
}

if(supportedPage()){
  addStyles();
  queueHydrate(true);
  document.addEventListener('click',e=>{
    if(Date.now()<suppressClickUntil&&e.target.closest('.blockedSchedule,.blockedBlock')){
      e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();
    }
  },true);
  $('date')?.addEventListener('change',()=>{rowsDate='';cancelStaleDrag();queueHydrate(true)});
  new MutationObserver(()=>queueHydrate()).observe(document.body,{childList:true,subtree:true});
  window.addEventListener('touchmove',onTouchMove,{passive:false,capture:true});
  window.addEventListener('touchend',onTouchEnd,{passive:false,capture:true});
  window.addEventListener('touchcancel',onTouchCancel,{passive:false,capture:true});
  window.addEventListener('pointermove',onPointerMove,{passive:false});
  window.addEventListener('pointerup',onPointerUp,{passive:false});
  window.addEventListener('pointercancel',onPointerCancel,{passive:false});
  window.addEventListener('blur',cancelStaleDrag);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)cancelStaleDrag()});
}