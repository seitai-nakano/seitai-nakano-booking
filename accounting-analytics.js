import {createClient} from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm';
const supabase=createClient('https://scjzofjyxmchfjsngqtb.supabase.co','sb_publishable_EGlr-6w0xh4gD8OImboE_Q_V-COJ7t9');
const $=id=>document.getElementById(id);
const yen=n=>'¥'+Math.round(Number(n)||0).toLocaleString('ja-JP');
function nextMonthStart(month){const[y,m]=month.split('-').map(Number),d=new Date(Date.UTC(y,m,1));return `${d.getUTCFullYear()}-${String(d.getUTCMonth()+1).padStart(2,'0')}-01`}
function ensureUI(){
  if($('actualSalesCard'))return;
  const metrics=document.querySelector('.metrics')?.closest('section.card');
  if(!metrics)return;
  const card=document.createElement('section');card.className='card';card.id='actualSalesCard';
  card.innerHTML=`<div class="sectionHeader"><div><h2>会計済み実売上</h2><div class="muted">店舗会計を保存した分だけ集計</div></div><a href="./checkout.html" class="back" style="padding:7px 10px">会計画面</a></div><div class="metrics"><div class="metric"><div class="metricLabel">実売上</div><div id="actualSales" class="metricValue">¥0</div><div class="metricSub">会計済みのみ</div></div><div class="metric"><div class="metricLabel">会計件数</div><div id="actualCount" class="metricValue">0件</div><div class="metricSub">会計保存済み</div></div><div class="metric"><div class="metricLabel">施術売上</div><div id="actualTreatment" class="metricValue">¥0</div><div class="metricSub">会計時の施術料金</div></div><div class="metric"><div class="metricLabel">店販売上</div><div id="actualRetail" class="metricValue">¥0</div><div class="metricSub">セラフィー・インパクト等</div></div></div><div id="actualAdjust" class="muted" style="margin-top:9px"></div><div id="actualProducts" style="margin-top:10px"></div><div id="actualStatus" class="status"></div>`;
  metrics.insertAdjacentElement('afterend',card);
}
async function load(){
  ensureUI();const month=$('month')?.value;if(!/^\d{4}-\d{2}$/.test(month||''))return;
  const {data:{session}}=await supabase.auth.getSession();if(!session)return;
  const first=`${month}-01`,next=nextMonthStart(month);$('actualStatus').textContent='会計売上を集計しています…';
  const {data:sales,error}=await supabase.from('nakano_sales').select('id,sale_date,treatment_amount,adjustment_amount,total_amount').gte('sale_date',first).lt('sale_date',next).order('sale_date');
  if(error){console.error(error);$('actualStatus').textContent='会計売上を読み込めませんでした。';return}
  const rows=sales||[],saleIds=rows.map(x=>x.id);let items=[];
  if(saleIds.length){const r=await supabase.from('nakano_sale_items').select('sale_id,item_code,item_name,unit_price,quantity,amount').in('sale_id',saleIds);if(r.error){console.error(r.error)}else items=r.data||[]}
  const total=rows.reduce((s,x)=>s+(Number(x.total_amount)||0),0),treatment=rows.reduce((s,x)=>s+(Number(x.treatment_amount)||0),0),adjust=rows.reduce((s,x)=>s+(Number(x.adjustment_amount)||0),0),retail=items.reduce((s,x)=>s+(Number(x.amount)||0),0);
  $('actualSales').textContent=yen(total);$('actualCount').textContent=`${rows.length}件`;$('actualTreatment').textContent=yen(treatment);$('actualRetail').textContent=yen(retail);$('actualAdjust').textContent=adjust?`その他調整額 合計 ${adjust>=0?'+':''}${yen(adjust)}`:'';
  const map=new Map();for(const i of items){const key=`${i.item_name}|${i.unit_price}`,cur=map.get(key)||{name:i.item_name,price:Number(i.unit_price)||0,qty:0,amount:0};cur.qty+=Number(i.quantity)||0;cur.amount+=Number(i.amount)||0;map.set(key,cur)}
  const products=[...map.values()].sort((a,b)=>b.amount-a.amount);
  $('actualProducts').innerHTML=products.length?`<div class="notice"><strong>店販内訳</strong><br>${products.map(x=>`${x.name} ${yen(x.price)} × ${x.qty} = ${yen(x.amount)}`).join('<br>')}</div>`:'';$('actualStatus').textContent='';
}
function bind(){ensureUI();$('month')?.addEventListener('change',()=>setTimeout(load,30));$('prevMonth')?.addEventListener('click',()=>setTimeout(load,80));$('nextMonth')?.addEventListener('click',()=>setTimeout(load,80));supabase.auth.onAuthStateChange(()=>setTimeout(load,100));setTimeout(load,450)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind);else bind();