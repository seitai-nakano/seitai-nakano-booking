import {createClient} from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm';

const supabase=createClient('https://scjzofjyxmchfjsngqtb.supabase.co','sb_publishable_EGlr-6w0xh4gD8OImboE_Q_V-COJ7t9');
const $=id=>document.getElementById(id);
const yen=n=>'¥'+Math.round(Number(n)||0).toLocaleString('ja-JP');
const esc=v=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#039;');
let rows=[];
let sales=new Map();
let loadTimer=null;

function todayJapan(){
  const p=new Intl.DateTimeFormat('en-US',{timeZone:'Asia/Tokyo',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());
  const g=t=>p.find(x=>x.type===t)?.value;
  return `${g('year')}-${g('month')}-${g('day')}`;
}

function ensureUI(){
  if($('pastCheckoutCard'))return;
  const editor=$('editor');
  if(!editor)return;
  const card=document.createElement('section');
  card.id='pastCheckoutCard';
  card.className='card';
  card.innerHTML=`
    <div class="editorTitle"><div><h2>過去の予約から会計</h2><div class="muted">管理者が手動で入れた過去予約も、その予約に紐づけて会計できます</div></div></div>
    <label>予約を探す</label>
    <input id="pastCheckoutSearch" placeholder="お客様名・日付・メニュー">
    <label style="display:flex;align-items:center;gap:8px;font-weight:700"><input id="pastCheckoutOpenOnly" type="checkbox" checked style="width:auto;margin:0"> 未会計のみ表示</label>
    <div id="pastCheckoutCount" class="muted" style="margin-top:8px"></div>
    <div id="pastCheckoutList" style="margin-top:4px"><div class="loading">読み込んでいます…</div></div>
    <div id="pastCheckoutMsg" class="status"></div>`;
  editor.insertAdjacentElement('beforebegin',card);
  $('pastCheckoutSearch').addEventListener('input',render);
  $('pastCheckoutOpenOnly').addEventListener('change',render);
}

async function loadPast(){
  ensureUI();
  const {data:{session}}=await supabase.auth.getSession();
  if(!session||!$('pastCheckoutList'))return;
  $('pastCheckoutList').innerHTML='<div class="loading">過去予約を読み込んでいます…</div>';
  $('pastCheckoutMsg').textContent='';
  const {data:bs,error:be}=await supabase.from('nakano_bookings')
    .select('id,booking_date,start_time,minutes,menu_name,price,customer_name,phone,status')
    .eq('status','confirmed').lte('booking_date',todayJapan())
    .order('booking_date',{ascending:false}).order('start_time',{ascending:false}).limit(300);
  if(be){console.error(be);$('pastCheckoutList').innerHTML='';$('pastCheckoutMsg').textContent='過去予約を読み込めませんでした。';return}
  rows=bs||[];
  sales=new Map();
  if(rows.length){
    const ids=rows.map(x=>x.id);
    const {data:ss,error:se}=await supabase.from('nakano_sales').select('booking_id,total_amount').in('booking_id',ids);
    if(se){console.error(se)}else for(const s of ss||[])sales.set(String(s.booking_id),s);
  }
  render();
}

function render(){
  if(!$('pastCheckoutList'))return;
  const q=($('pastCheckoutSearch').value||'').trim().toLowerCase();
  const openOnly=$('pastCheckoutOpenOnly').checked;
  const filtered=rows.filter(b=>{
    if(openOnly&&sales.has(String(b.id)))return false;
    if(!q)return true;
    const text=[b.customer_name,b.phone,b.booking_date,b.menu_name].filter(Boolean).join(' ').toLowerCase();
    return text.includes(q);
  });
  $('pastCheckoutCount').textContent=`${filtered.length}件${openOnly?'（未会計）':''}`;
  $('pastCheckoutList').innerHTML=filtered.length?filtered.map(b=>{
    const s=sales.get(String(b.id));
    return `<div class="bookingRow pastCheckoutRow" data-id="${esc(b.id)}" data-date="${esc(b.booking_date)}"><div class="bookingTop"><div><div class="bookingTime">${esc(b.booking_date)} ${esc(String(b.start_time).slice(0,5))}　${esc(b.customer_name||'')}</div><div class="bookingName">${esc(b.menu_name||'')}</div><div class="bookingMeta">予約料金 ${yen(b.price)}・${Number(b.minutes)||0}分</div></div><span class="badge ${s?'done':'open'}">${s?`会計済 ${yen(s.total_amount)}`:'未会計'}</span></div></div>`;
  }).join(''):'<div class="muted" style="padding:10px 0">該当する予約はありません。</div>';
  document.querySelectorAll('.pastCheckoutRow').forEach(el=>el.addEventListener('click',()=>openBooking(el.dataset.id,el.dataset.date)));
}

async function openBooking(id,date){
  const dateInput=$('date');
  if(!dateInput)return;
  dateInput.value=date;
  dateInput.dispatchEvent(new Event('change',{bubbles:true}));
  $('pastCheckoutMsg').textContent='予約を開いています…';
  for(let i=0;i<40;i++){
    await new Promise(r=>setTimeout(r,80));
    const target=[...document.querySelectorAll('#list .bookingRow')].find(x=>String(x.dataset.id)===String(id));
    if(target){
      $('pastCheckoutMsg').textContent='';
      target.click();
      return;
    }
  }
  $('pastCheckoutMsg').textContent='予約を開けませんでした。予約日から選び直してください。';
}

function scheduleReload(){
  clearTimeout(loadTimer);
  loadTimer=setTimeout(loadPast,250);
}

function boot(){
  ensureUI();
  loadPast();
  $('save')?.addEventListener('click',()=>setTimeout(scheduleReload,700));
  $('deleteSale')?.addEventListener('click',()=>setTimeout(scheduleReload,700));
}

if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
supabase.auth.onAuthStateChange(()=>setTimeout(loadPast,150));
