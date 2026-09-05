import {createClient} from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm';

const supabase=createClient(
  'https://scjzofjyxmchfjsngqtb.supabase.co',
  'sb_publishable_EGlr-6w0xh4gD8OImboE_Q_V-COJ7t9'
);

const DAY_START=8*60;
const DAY_END=23*60;
const PX_PER_MINUTE=2;
const SNAP_MINUTES=15;
const DRAG_START_DISTANCE=5;
const TOUCH_HOLD_TO_DRAG_MS=240;
const SCROLL_INTENT_DISTANCE=8;
const EDGE_ZONE=96;
const MAX_AUTO_SPEED=18;

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
.blockedSchedule,.blockedBlock{-webkit-touch-callout:none;touch-action:pan-x;cursor:pointer}
.blockedSchedule.blockedDragging,.blockedBlock.blockedDragging{z-index:110!important;opacity:.96;box-shadow:0 0 0 3px rgba(138,74,66,.24),0 9px 26px rgba(0,0,0,.22)!important;transform:translateY(8px) scale(1.02);touch-action:none!important}
.blockedDragGhost{pointer-events:none!important;z-index:4!important;opacity:.45!important;border:2px dashed rgba(138,74,66,.62)!important;background:rgba(244,223,220,.40)!important;box-shadow:none!important}
.blockedMoveHandle{position:absolute;right:2px;top:50%;transform:translateY(-50%);z-index:30;width:28px;height:34px;border:1px solid rgba(120,70,64,.30);border-radius:9px;background:rgba(255,255,255,.88);display:flex;align-items:center;justify-content:center;color:#8a4a42;font-size:15px;font-weight:900;line-height:1;touch-action:none!important;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;cursor:ew-resize;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.blockedMoveHandle:active{background:#fff1ef;transform:translateY(-50%) scale(.96)}
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

function createGhost(s){
  const g=s.el.cloneNode(true);
  g.classList.remove('blockedSelected','blockedDragging');
  g.classList.add('blockedDragGhost');
  g.style.left=`${s.originalLeft}px`;
  g.style.width=`${s.originalWidth}px`;
  g.removeAttribute('id');
  s.el.parentElement?.insertBefore(g,s.el);
  s.ghost=g;
}
function removeGhost(s){if(s?.ghost){s.ghost.remove();s.ghost=null}}
function stopAuto(){if(autoFrame){cancelAnimationFrame(autoFrame);autoFrame=null}hideEdges()}
function cleanup(s){
  clearTimeout(pressTimer);pressTimer=null;
  s?.el?.classList.remove('blockedDragging');
  document.body.classList.remove('bookingDragging');
  removeGhost(s);hideDestination();stopAuto();
}
function restore(s){if(!s)return;s.el.style.left=`${s.originalLeft}px`;s.el.style.width=`${s.originalWidth}px`}

function updateVisual(){
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
  if(speed){const before=s.scroll.scrollLeft;s.scroll.scrollLeft+=speed;if(before!==s.scroll.scrollLeft)updateVisual()}
  autoFrame=requestAnimationFrame(autoLoop);
}

function startDrag(){
  const s=drag;if(!s||s.interacting)return;
  s.interacting=true;
  $('blockedInlineEditor')?.classList.remove('open');
  createGhost(s);
  s.el.classList.add('blockedDragging');
  document.body.classList.add('bookingDragging');
  try{navigator.vibrate?.(18)}catch{}
  const st=minutesToTime(s.originalStart).slice(0,5),en=minutesToTime(s.originalStart+s.duration).slice(0,5);
  destination(`${st}–${en}`);
  autoFrame=requestAnimationFrame(autoLoop);
}

function ensureMoveHandle(el,item){
  let h=el.querySelector('.blockedMoveHandle');
  if(!movable(item)){if(h)h.remove();return null}
  if(h)return h;
  h=document.createElement('span');
  h.className='blockedMoveHandle';
  h.textContent='↔';
  h.title='ここを左右に動かして予定時間を変更';
  h.setAttribute('aria-label','予定時間を左右に移動');
  h.addEventListener('click',e=>{e.preventDefault();e.stopPropagation()});
  el.appendChild(h);
  return h;
}

function onHandleDown(e,el,item){
  if(drag||(e.pointerType==='mouse'&&e.button!==0))return;
  const scroll=el.closest('.timelineScroll,.scheduleScroll');
  if(!scroll||!movable(item))return;
  const r=range(item);
  e.preventDefault();
  e.stopPropagation();
  drag={
    el,item,scroll,pointerId:e.pointerId,pointerType:e.pointerType||'touch',
    startX:e.clientX,startY:e.clientY,currentX:e.clientX,currentY:e.clientY,
    startScrollLeft:scroll.scrollLeft,
    originalStart:r.start,newStart:r.start,duration:r.duration,
    originalLeft:parseFloat(el.style.left)||((r.start-DAY_START)*PX_PER_MINUTE),
    originalWidth:parseFloat(el.style.width)||Math.max(36,r.duration*PX_PER_MINUTE),
    interacting:false,ghost:null
  };
  startDrag();
}

function onDown(e,el,item){
  if(drag||(e.pointerType==='mouse'&&e.button!==0))return;
  const scroll=el.closest('.timelineScroll,.scheduleScroll');
  if(!scroll||!movable(item))return;
  const r=range(item);
  drag={
    el,item,scroll,pointerId:e.pointerId,pointerType:e.pointerType||'touch',
    startX:e.clientX,startY:e.clientY,currentX:e.clientX,currentY:e.clientY,
    startScrollLeft:scroll.scrollLeft,
    originalStart:r.start,newStart:r.start,duration:r.duration,
    originalLeft:parseFloat(el.style.left)||((r.start-DAY_START)*PX_PER_MINUTE),
    originalWidth:parseFloat(el.style.width)||Math.max(36,r.duration*PX_PER_MINUTE),
    interacting:false,ghost:null
  };

  // Touch: ordinary horizontal swipe must remain native schedule scrolling.
  // Only a short hold arms moving the red blocked/plan card.
  clearTimeout(pressTimer);
  if(e.pointerType!=='mouse'){
    const pointerId=e.pointerId;
    pressTimer=setTimeout(()=>{
      if(drag&&drag.pointerId===pointerId&&!drag.interacting)startDrag();
    },TOUCH_HOLD_TO_DRAG_MS);
  }
}

function onMove(e){
  const s=drag;if(!s||s.pointerId!==e.pointerId)return;
  s.currentX=e.clientX;s.currentY=e.clientY;
  if(!s.interacting){
    const dx=s.currentX-s.startX,dy=s.currentY-s.startY;

    if(s.pointerType==='mouse'){
      if(Math.hypot(dx,dy)<DRAG_START_DISTANCE)return;
      if(Math.abs(dy)>Math.abs(dx)*1.25){clearTimeout(pressTimer);pressTimer=null;drag=null;return}
      startDrag();
      if(!drag?.interacting)return;
    }else{
      // Before the hold fires, a clear horizontal gesture belongs to native scrolling.
      if(Math.abs(dx)>=SCROLL_INTENT_DISTANCE&&Math.abs(dx)>Math.abs(dy)*1.1){
        clearTimeout(pressTimer);pressTimer=null;drag=null;return;
      }
      // Vertical movement also cancels the pending card drag.
      if(Math.abs(dy)>=12&&Math.abs(dy)>=Math.abs(dx)){
        clearTimeout(pressTimer);pressTimer=null;drag=null;return;
      }
      return;
    }
  }
  e.preventDefault();
  // iPhone/Safari: scroll immediately while the finger is near either edge.
  // The RAF loop below continues scrolling even when the finger is held still.
  const rect=s.scroll.getBoundingClientRect();
  let immediate=0;
  if(s.currentX<rect.left+EDGE_ZONE){
    const p=Math.max(0,Math.min(1,(rect.left+EDGE_ZONE-s.currentX)/EDGE_ZONE));
    immediate=-(6+p*16);
  }else if(s.currentX>rect.right-EDGE_ZONE){
    const p=Math.max(0,Math.min(1,(s.currentX-(rect.right-EDGE_ZONE))/EDGE_ZONE));
    immediate=6+p*16;
  }
  if(immediate){
    s.scroll.scrollLeft+=immediate;
  }
  updateVisual();
}

async function onUp(e){
  const s=drag;if(!s||s.pointerId!==e.pointerId)return;
  clearTimeout(pressTimer);pressTimer=null;drag=null;
  if(!s.interacting)return;
  suppressClickUntil=Date.now()+900;
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

function onCancel(e){
  const s=drag;if(!s||s.pointerId!==e.pointerId)return;
  clearTimeout(pressTimer);pressTimer=null;drag=null;
  if(s.interacting){restore(s);cleanup(s)}
}

function attach(el,item){
  el.style.touchAction='pan-x';
  const hint=el.querySelector('.blockedTapHint');
  if(!movable(item)){
    if(hint)hint.textContent='タップで時間変更';
    ensureMoveHandle(el,item);
    return;
  }
  if(hint)hint.textContent='タップで編集・↔を左右に動かして移動';
  el.title=`${String(item.start_time).slice(0,5)}〜${String(item.end_time).slice(0,5)} タップで編集／↔で時間移動`;
  const handle=ensureMoveHandle(el,item);
  if(handle&&handle.dataset.boundMove!=='1'){
    handle.dataset.boundMove='1';
    handle.addEventListener('pointerdown',e=>onHandleDown(e,el,item));
    handle.addEventListener('contextmenu',e=>e.preventDefault());
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

if(supportedPage()){
  addStyles();
  queueHydrate(true);
  document.addEventListener('click',e=>{
    if(Date.now()<suppressClickUntil&&e.target.closest('.blockedSchedule,.blockedBlock')){
      e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();
    }
  },true);
  $('date')?.addEventListener('change',()=>{rowsDate='';queueHydrate(true)});
  new MutationObserver(()=>queueHydrate()).observe(document.body,{childList:true,subtree:true});
  window.addEventListener('pointermove',onMove,{passive:false});
  window.addEventListener('pointerup',onUp,{passive:false});
  window.addEventListener('pointercancel',onCancel,{passive:false});
}
