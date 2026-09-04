import {createClient} from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm';

const supabase=createClient(
  'https://scjzofjyxmchfjsngqtb.supabase.co',
  'sb_publishable_EGlr-6w0xh4gD8OImboE_Q_V-COJ7t9'
);

const $=id=>document.getElementById(id);
let viewMonth='';
let counts=new Map();
let loading=false;
let ready=false;

function currentJapanMonth(){
  const parts=new Intl.DateTimeFormat('en-US',{
    timeZone:'Asia/Tokyo',year:'numeric',month:'2-digit'
  }).formatToParts(new Date());
  const get=t=>parts.find(p=>p.type===t)?.value||'';
  return `${get('year')}-${get('month')}`;
}

function monthFromDate(date){return /^\d{4}-\d{2}-\d{2}$/.test(date||'')?date.slice(0,7):''}

function shiftMonth(month,delta){
  const[y,m]=(month||currentJapanMonth()).split('-').map(Number);
  const d=new Date(Date.UTC(y,m-1+delta,1));
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth()+1).padStart(2,'0')}`;
}

function nextMonthStart(month){return `${shiftMonth(month,1)}-01`}

function monthDates(month){
  if(!/^\d{4}-\d{2}$/.test(month||''))return[];
  const[y,m]=month.split('-').map(Number);
  const last=new Date(y,m,0).getDate();
  return Array.from({length:last},(_,i)=>`${month}-${String(i+1).padStart(2,'0')}`);
}

function addStyles(){
  if($('adminBookingCalendarStyle'))return;
  const s=document.createElement('style');
  s.id='adminBookingCalendarStyle';
  s.textContent=`
.adminBookingCalendar{margin:10px 0 3px;padding:12px;border:1px solid #e7e0d7;border-radius:14px;background:#faf8f5}
.adminBookingCalendarHead{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:9px}
.adminBookingCalendarMonth{font-size:15px;font-weight:800;text-align:center;flex:1}
.adminBookingCalendarTotal{display:block;margin-top:2px;color:#817970;font-size:10px;font-weight:600}
.adminBookingCalendarNav{width:42px!important;min-width:42px;height:38px;padding:0!important;margin:0!important;border:1px solid #ddd5cc;border-radius:10px;background:#fff;color:#554e48;font-size:20px;font-weight:700}
.adminBookingCalendarWeek,.adminBookingCalendarGrid{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:4px}
.adminBookingCalendarWeek{margin-bottom:4px;color:#8a837d;font-size:10px;text-align:center}
.adminBookingCalendarDay{position:relative;min-width:0;height:55px;padding:5px 2px!important;margin:0!important;border:1px solid #e7e0d7;border-radius:10px;background:#fff;color:#46413d;text-align:center}
.adminBookingCalendarDay.selected{border-color:#61574d;background:#61574d;color:#fff}
.adminBookingCalendarDay.today:not(.selected){box-shadow:inset 0 0 0 1px #9a8e82}
.adminBookingCalendarDay.hasBooking:not(.selected){background:#f4eee8}
.adminBookingCalendarNum{display:block;font-size:14px;font-weight:800;line-height:1.2}
.adminBookingCalendarCount{display:block;margin-top:3px;font-size:9px;font-weight:800;line-height:1.1;color:#8a5e4f}
.adminBookingCalendarDay.selected .adminBookingCalendarCount{color:#fff}
.adminBookingCalendarBlank{height:55px}
.adminBookingCalendarHint{margin-top:8px;color:#827b74;font-size:10px;text-align:center}
@media(max-width:420px){.adminBookingCalendar{padding:10px}.adminBookingCalendarDay{height:52px}.adminBookingCalendarGrid,.adminBookingCalendarWeek{gap:3px}}
`;
  document.head.appendChild(s);
}

function ensureCalendar(){
  const date=$('date');
  if(!date)return null;
  let box=$('adminBookingCalendar');
  if(box)return box;
  addStyles();
  box=document.createElement('div');
  box.id='adminBookingCalendar';
  box.className='adminBookingCalendar';
  box.innerHTML=`
    <div class="adminBookingCalendarHead">
      <button type="button" id="adminBookingCalendarPrev" class="adminBookingCalendarNav" aria-label="前月">‹</button>
      <div class="adminBookingCalendarMonth" id="adminBookingCalendarMonth"></div>
      <button type="button" id="adminBookingCalendarNext" class="adminBookingCalendarNav" aria-label="翌月">›</button>
    </div>
    <div class="adminBookingCalendarWeek"><span>日</span><span>月</span><span>火</span><span>水</span><span>木</span><span>金</span><span>土</span></div>
    <div class="adminBookingCalendarGrid" id="adminBookingCalendarGrid"></div>
    <div class="adminBookingCalendarHint">日付をタップすると、その日の予定に切り替わります</div>`;
  date.insertAdjacentElement('afterend',box);
  $('adminBookingCalendarPrev').addEventListener('click',()=>changeViewMonth(-1));
  $('adminBookingCalendarNext').addEventListener('click',()=>changeViewMonth(1));
  date.addEventListener('change',onSelectedDateChange);
  return box;
}

function todayJapan(){
  const parts=new Intl.DateTimeFormat('en-US',{
    timeZone:'Asia/Tokyo',year:'numeric',month:'2-digit',day:'2-digit'
  }).formatToParts(new Date());
  const get=t=>parts.find(p=>p.type===t)?.value||'';
  return `${get('year')}-${get('month')}-${get('day')}`;
}

function render(){
  if(!ensureCalendar()||!viewMonth)return;
  const[y,m]=viewMonth.split('-').map(Number);
  const total=[...counts.values()].reduce((s,n)=>s+n,0);
  $('adminBookingCalendarMonth').innerHTML=`${y}年${m}月<span class="adminBookingCalendarTotal">予約 ${total}件</span>`;
  const grid=$('adminBookingCalendarGrid');
  grid.innerHTML='';
  const dates=monthDates(viewMonth);
  if(!dates.length)return;
  const first=new Date(`${dates[0]}T00:00:00`).getDay();
  for(let i=0;i<first;i++){
    const blank=document.createElement('span');
    blank.className='adminBookingCalendarBlank';
    grid.appendChild(blank);
  }
  const selected=$('date')?.value||'';
  const today=todayJapan();
  for(const date of dates){
    const count=counts.get(date)||0;
    const b=document.createElement('button');
    b.type='button';
    b.className='adminBookingCalendarDay';
    if(date===selected)b.classList.add('selected');
    if(date===today)b.classList.add('today');
    if(count>0)b.classList.add('hasBooking');
    b.innerHTML=`<span class="adminBookingCalendarNum">${Number(date.slice(-2))}</span>${count?`<span class="adminBookingCalendarCount">${count}件</span>`:''}`;
    b.addEventListener('click',()=>selectDate(date));
    grid.appendChild(b);
  }
}

async function loadMonth(month){
  if(loading||!/^\d{4}-\d{2}$/.test(month||''))return;
  loading=true;
  try{
    const first=`${month}-01`,next=nextMonthStart(month);
    const{data,error}=await supabase.from('nakano_bookings')
      .select('booking_date')
      .gte('booking_date',first)
      .lt('booking_date',next)
      .eq('status','confirmed');
    if(error)throw error;
    counts=new Map();
    for(const row of data||[]){
      const d=String(row.booking_date||'');
      counts.set(d,(counts.get(d)||0)+1);
    }
    viewMonth=month;
    render();
  }catch(e){
    console.warn('予約数カレンダーを読み込めませんでした',e);
  }finally{
    loading=false;
  }
}

async function selectDate(date){
  const input=$('date');
  if(!input)return;
  input.value=date;
  render();
  input.dispatchEvent(new Event('change',{bubbles:true}));
  try{input.scrollIntoView({behavior:'smooth',block:'start'})}catch{}
}

async function changeViewMonth(delta){
  const next=shiftMonth(viewMonth||monthFromDate($('date')?.value)||currentJapanMonth(),delta);
  await loadMonth(next);
}

async function onSelectedDateChange(){
  const month=monthFromDate($('date')?.value);
  if(month&&month!==viewMonth)await loadMonth(month);
  else render();
}

async function start(){
  ensureCalendar();
  const{data:{session}}=await supabase.auth.getSession();
  if(!session)return;
  const month=monthFromDate($('date')?.value)||currentJapanMonth();
  await loadMonth(month);
  ready=true;
}

supabase.auth.onAuthStateChange((_event,session)=>{
  if(session&&!ready)setTimeout(start,120);
});

window.refreshAdminBookingCalendar=async(date)=>{
  const month=monthFromDate(date)||viewMonth||currentJapanMonth();
  await loadMonth(month);
};

setTimeout(start,650);
