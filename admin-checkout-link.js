import{createClient}from'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm';
const supabase=createClient('https://scjzofjyxmchfjsngqtb.supabase.co','sb_publishable_EGlr-6w0xh4gD8OImboE_Q_V-COJ7t9');
const $=id=>document.getElementById(id);
let checkedOut=new Set();
let refreshToken=0;

function addStyles(){
  if(document.getElementById('adminCheckoutStateStyle'))return;
  const style=document.createElement('style');
  style.id='adminCheckoutStateStyle';
  style.textContent=`
    .bookingBlock.checkoutDone{background:#dedbd7!important;border-color:#aaa49d!important;color:#6c6762!important;box-shadow:none!important}
    .bookingBlock.checkoutDone .bookingTime,.bookingBlock.checkoutDone .bookingMenu{color:#77716a!important}
    .bookingBlock.checkoutDone::after{content:'会計済';position:absolute;right:5px;top:5px;padding:2px 5px;border-radius:999px;background:#c8c4bf;color:#5f5a55;font-size:9px;font-weight:800}
    #editCheckoutButton{margin-top:8px}
  `;
  document.head.appendChild(style);
}

function applyTimelineState(){
  document.querySelectorAll('.bookingBlock[data-booking-id]').forEach(block=>{
    const id=String(block.dataset.bookingId||'');
    block.classList.toggle('checkoutDone',checkedOut.has(id));
  });
}

async function refreshCheckoutState(){
  const token=++refreshToken;
  const date=$('date')?.value;
  if(!date)return;
  const {data:{session}}=await supabase.auth.getSession();
  if(!session)return;
  const {data:bookings,error:be}=await supabase.from('nakano_bookings').select('id').eq('booking_date',date).eq('status','confirmed');
  if(be||token!==refreshToken)return;
  const ids=(bookings||[]).map(x=>x.id);
  if(!ids.length){checkedOut=new Set();applyTimelineState();return}
  const {data:sales,error:se}=await supabase.from('nakano_sales').select('booking_id').in('booking_id',ids);
  if(se||token!==refreshToken)return;
  checkedOut=new Set((sales||[]).map(x=>String(x.booking_id)));
  applyTimelineState();
}

function ensureCheckoutButton(bookingId){
  const card=$('editCard');
  if(!card||card.classList.contains('hidden'))return;
  let btn=$('editCheckoutButton');
  if(!btn){
    btn=document.createElement('button');
    btn.id='editCheckoutButton';
    btn.type='button';
    btn.className='primary';
    const anchor=$('cancelBookingFromEdit')||$('saveEdit')||$('editMsg');
    if(anchor?.parentNode)anchor.parentNode.insertBefore(btn,anchor.nextSibling);else card.appendChild(btn);
  }
  btn.dataset.bookingId=bookingId;
  btn.textContent=checkedOut.has(String(bookingId))?'会計済みを開く':'会計する';
  btn.onclick=()=>{
    const id=btn.dataset.bookingId;
    if(!id)return;
    const u=new URL('./checkout.html',location.href);
    u.searchParams.set('booking',id);
    location.href=u.href;
  };
}

function bind(){
  addStyles();
  $('date')?.addEventListener('change',()=>setTimeout(refreshCheckoutState,250));
  document.addEventListener('click',e=>{
    const block=e.target.closest?.('.bookingBlock[data-booking-id]');
    if(!block)return;
    const id=String(block.dataset.bookingId||'');
    if(!id)return;
    setTimeout(()=>ensureCheckoutButton(id),30);
  },true);
  const canvas=$('scheduleCanvas');
  if(canvas){
    new MutationObserver(()=>applyTimelineState()).observe(canvas,{childList:true,subtree:true});
  }
  supabase.auth.onAuthStateChange(()=>setTimeout(refreshCheckoutState,200));
  setTimeout(refreshCheckoutState,500);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind);else bind();