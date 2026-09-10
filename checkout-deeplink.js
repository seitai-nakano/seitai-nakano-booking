import{createClient}from'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm';
const supabase=createClient('https://scjzofjyxmchfjsngqtb.supabase.co','sb_publishable_EGlr-6w0xh4gD8OImboE_Q_V-COJ7t9');
const bookingId=new URLSearchParams(location.search).get('booking');
let tried=false;

const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function waitForRow(id,timeout=6000){
  const start=Date.now();
  while(Date.now()-start<timeout){
    const row=document.querySelector(`.bookingRow[data-id="${CSS.escape(id)}"]`);
    if(row)return row;
    await sleep(120);
  }
  return null;
}

async function openBookingCheckout(){
  if(!bookingId||tried)return;
  const {data:{session}}=await supabase.auth.getSession();
  if(!session)return;
  tried=true;
  const {data:booking,error}=await supabase.from('nakano_bookings').select('id,booking_date,status').eq('id',bookingId).maybeSingle();
  if(error||!booking||booking.status!=='confirmed')return;
  const date=document.getElementById('date');
  if(!date)return;
  date.value=booking.booking_date;
  date.dispatchEvent(new Event('change',{bubbles:true}));
  const row=await waitForRow(String(booking.id));
  if(row){
    row.click();
    const u=new URL(location.href);u.searchParams.delete('booking');history.replaceState(null,'',u.href);
  }
}

if(bookingId){
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(openBookingCheckout,300));
  else setTimeout(openBookingCheckout,300);
  supabase.auth.onAuthStateChange(()=>setTimeout(openBookingCheckout,250));
}