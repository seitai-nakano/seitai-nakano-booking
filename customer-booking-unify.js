import {createClient} from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm';

const supabase=createClient(
  'https://scjzofjyxmchfjsngqtb.supabase.co',
  'sb_publishable_EGlr-6w0xh4gD8OImboE_Q_V-COJ7t9'
);

let currentCustomerId=null;

function ensureBox(){
  const history=document.getElementById('bookingHistory');
  if(!history)return null;
  let box=document.getElementById('manualBookingUnifyBox');
  if(box)return box;
  box=document.createElement('div');
  box.id='manualBookingUnifyBox';
  box.style.display='none';
  box.style.margin='10px 0 12px';
  box.style.padding='12px';
  box.style.border='1px solid #e4d7c9';
  box.style.borderRadius='12px';
  box.style.background='#fbf8f4';
  history.parentElement?.insertBefore(box,history);
  return box;
}

async function refreshBox(){
  const box=ensureBox();
  if(!box||!currentCustomerId)return;
  const {data:customer,error:customerError}=await supabase
    .from('nakano_customers')
    .select('id,customer_name')
    .eq('id',currentCustomerId)
    .maybeSingle();
  if(customerError||!customer){box.style.display='none';return}

  const {data:count,error}=await supabase.rpc(
    'nakano_admin_unassigned_booking_count',
    {p_customer_id:currentCustomerId}
  );
  if(error||!Number(count)){
    box.style.display='none';
    box.innerHTML='';
    return;
  }

  box.style.display='block';
  box.innerHTML=`
    <div style="font-weight:800;margin-bottom:4px">手入力予約の統合</div>
    <div style="font-size:12px;line-height:1.6;color:#77716a;margin-bottom:9px">
      「${escapeHtml(customer.customer_name)}」名義で、まだ顧客に紐付いていない手入力予約が ${Number(count)}件あります。
    </div>
    <button id="linkManualBookings" type="button" style="width:100%;padding:11px;border:1px solid #d8d0c7;border-radius:11px;background:#fff;color:#4d4843;font:inherit;font-weight:700">
      ${Number(count)}件をこの顧客に統合
    </button>
    <div id="linkManualBookingsMsg" style="margin-top:7px;font-size:12px;color:#46714d"></div>`;

  document.getElementById('linkManualBookings').onclick=async()=>{
    if(!confirm(`${customer.customer_name}さんの手入力予約 ${Number(count)}件を、この顧客の予約履歴に統合しますか？`))return;
    const button=document.getElementById('linkManualBookings');
    const msg=document.getElementById('linkManualBookingsMsg');
    button.disabled=true;
    msg.textContent='統合しています…';
    const {data:linked,error:linkError}=await supabase.rpc(
      'nakano_admin_link_unassigned_bookings',
      {p_customer_id:currentCustomerId}
    );
    if(linkError){
      console.error(linkError);
      msg.textContent='統合できませんでした。';
      button.disabled=false;
      return;
    }
    msg.textContent=`${Number(linked)||0}件を統合しました。`;
    setTimeout(()=>{
      const item=document.querySelector(`.customerItem[data-id="${CSS.escape(String(currentCustomerId))}"]`);
      if(item)item.click();
      refreshBox();
    },250);
  };
}

function escapeHtml(v){
  return String(v??'')
    .replaceAll('&','&amp;')
    .replaceAll('<','&lt;')
    .replaceAll('>','&gt;')
    .replaceAll('"','&quot;')
    .replaceAll("'",'&#039;');
}

document.addEventListener('click',event=>{
  const item=event.target.closest?.('.customerItem[data-id]');
  if(!item)return;
  currentCustomerId=item.dataset.id||null;
  if(currentCustomerId)setTimeout(refreshBox,180);
},true);

setTimeout(()=>ensureBox(),500);
