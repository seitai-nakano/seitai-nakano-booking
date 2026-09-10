import {createClient} from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm';

const supabase=createClient('https://scjzofjyxmchfjsngqtb.supabase.co','sb_publishable_EGlr-6w0xh4gD8OImboE_Q_V-COJ7t9');
const $=id=>document.getElementById(id);
const PRODUCTS=[
  {code:'seraphy_9000',name:'セラフィー',price:9000},
  {code:'seraphy_15000',name:'セラフィー',price:15000},
  {code:'impact_6000',name:'インパクト',price:6000}
];
let menus=[],manualSales=[],manualItems=new Map(),current=null;
const yen=n=>'¥'+Math.round(Number(n)||0).toLocaleString('ja-JP');
const esc=v=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#039;');

function ensureUI(){
  if($('manualCheckoutCard'))return;
  const editor=$('editor');
  if(!editor)return;
  const card=document.createElement('section');
  card.id='manualCheckoutCard';card.className='card';
  card.innerHTML=`<div class="editorTitle"><div><h2>手入力会計</h2><div class="muted">予約がない会計・店販だけの会計も登録できます</div></div><button id="manualNew" class="primary" type="button" style="width:auto;padding:9px 12px">＋ 手入力</button></div><div id="manualList" style="margin-top:8px"></div><div id="manualListMsg" class="status"></div>`;
  editor.insertAdjacentElement('beforebegin',card);

  const form=document.createElement('section');
  form.id='manualEditor';form.className='card hidden';
  form.innerHTML=`<div class="editorTitle"><div><h2 id="manualTitle">手入力会計</h2><div id="manualDateLabel" class="muted"></div></div><button id="manualClose" class="secondary" type="button" style="width:auto;padding:8px 11px">閉じる</button></div>
  <div class="notice" style="margin-top:10px">この会計は予約売上には入りません。会計済み実売上にだけ反映されます。</div>
  <label>お客様名</label><input id="manualCustomerName" placeholder="未入力でも保存できます">
  <label>実際の施術メニュー</label><select id="manualTreatmentMenu"></select>
  <label>施術料金</label><div class="moneyRow"><div id="manualTreatmentName" style="font-weight:800">施術なし</div><input id="manualTreatmentAmount" type="number" inputmode="numeric" min="0" step="10" value="0"></div>
  <label>店舗販売品</label><div id="manualProducts"></div>
  <label>その他調整額</label><div class="moneyRow"><div class="muted">値引きはマイナスで入力できます</div><input id="manualAdjustment" type="number" inputmode="numeric" step="10" value="0"></div>
  <label>会計メモ（店内のみ）</label><textarea id="manualMemo" placeholder="例：予約なし来店、店販のみ等"></textarea>
  <div class="totalBox"><div class="totalLabel">会計合計</div><div id="manualTotal" class="total">¥0</div></div>
  <div class="actions"><button id="manualSave" class="primary" type="button">会計を保存</button><button id="manualDelete" class="danger hidden" type="button">会計データ削除</button></div><div id="manualSaveMsg" class="status"></div>`;
  editor.insertAdjacentElement('beforebegin',form);
  renderProducts();
  $('manualNew').onclick=()=>openManual(null);
  $('manualClose').onclick=()=>form.classList.add('hidden');
  $('manualSave').onclick=saveManual;
  $('manualDelete').onclick=deleteManual;
  $('manualTreatmentMenu').onchange=()=>{const m=menus.find(x=>String(x.id)===String($('manualTreatmentMenu').value));$('manualTreatmentName').textContent=m?.name||'施術なし';$('manualTreatmentAmount').value=String(m?.price||0);recalc()};
  $('manualTreatmentAmount').oninput=recalc;$('manualAdjustment').oninput=recalc;
  $('date')?.addEventListener('change',()=>{form.classList.add('hidden');setTimeout(loadManualSales,40)});
}

function renderProducts(){
  $('manualProducts').innerHTML=PRODUCTS.map(p=>`<div class="productRow" data-code="${p.code}" data-name="${p.name}" data-price="${p.price}"><div><div class="productName">${p.name}</div><div class="productPrice">${yen(p.price)}</div></div><input class="qty" type="number" inputmode="numeric" min="0" step="1" value="0"><div class="lineAmount">¥0</div></div>`).join('');
  $('manualProducts').querySelectorAll('.qty').forEach(x=>x.addEventListener('input',recalc));
}

async function loadMenus(){
  if(menus.length)return;
  const {data,error}=await supabase.from('nakano_menus').select('id,name,price,minutes,is_active,display_order').eq('is_active',true).order('display_order');
  if(!error)menus=data||[];
}
function menuOptions(selected=''){
  $('manualTreatmentMenu').innerHTML='<option value="">施術なし（店販のみ）</option>'+menus.map(m=>`<option value="${esc(m.id)}">${esc(m.name)}　${yen(m.price)}</option>`).join('');
  $('manualTreatmentMenu').value=selected||'';
}
function recalc(){
  const treatment=Math.max(0,Number($('manualTreatmentAmount').value)||0),adjust=Number($('manualAdjustment').value)||0;let retail=0;
  $('manualProducts').querySelectorAll('.productRow').forEach(r=>{const q=Math.max(0,Number(r.querySelector('.qty').value)||0),a=q*Number(r.dataset.price);r.querySelector('.lineAmount').textContent=yen(a);retail+=a});
  $('manualTotal').textContent=yen(treatment+retail+adjust);
}
function buildItems(){return [...$('manualProducts').querySelectorAll('.productRow')].map(r=>({code:r.dataset.code,name:r.dataset.name,unit_price:Number(r.dataset.price),quantity:Math.max(0,Number(r.querySelector('.qty').value)||0)})).filter(x=>x.quantity>0)}

async function loadManualSales(){
  ensureUI();const date=$('date')?.value;if(!date)return;
  const {data:{session}}=await supabase.auth.getSession();if(!session)return;
  $('manualList').innerHTML='<div class="loading">手入力会計を読み込んでいます…</div>';$('manualListMsg').textContent='';
  const {data,error}=await supabase.from('nakano_sales').select('*').eq('sale_date',date).is('booking_id',null).order('checked_out_at');
  if(error){console.error(error);$('manualList').innerHTML='';$('manualListMsg').textContent='手入力会計を読み込めませんでした。';return}
  manualSales=data||[];manualItems=new Map();
  const ids=manualSales.map(x=>x.id);
  if(ids.length){const r=await supabase.from('nakano_sale_items').select('*').in('sale_id',ids);if(!r.error)for(const i of r.data||[]){const a=manualItems.get(String(i.sale_id))||[];a.push(i);manualItems.set(String(i.sale_id),a)}}
  $('manualList').innerHTML=manualSales.length?manualSales.map(s=>`<div class="bookingRow manualSaleRow" data-id="${esc(s.id)}"><div class="bookingTop"><div><div class="bookingTime">手入力　${esc(s.customer_name||'')}</div><div class="bookingName">${esc(s.treatment_menu_name||'施術なし')}</div><div class="bookingMeta">会計済み ${yen(s.total_amount)}</div></div><span class="badge done">手入力</span></div></div>`).join(''):'<div class="muted" style="padding:10px 0">この日の手入力会計はありません。</div>';
  document.querySelectorAll('.manualSaleRow').forEach(r=>r.onclick=()=>openManual(r.dataset.id));
}

async function openManual(id){
  ensureUI();await loadMenus();current=id?manualSales.find(x=>String(x.id)===String(id))||null:null;
  const date=$('date')?.value;if(!date)return;
  $('manualDateLabel').textContent=`会計日：${date}`;$('manualTitle').textContent=current?'手入力会計を修正':'手入力会計を追加';
  $('manualCustomerName').value=current?.customer_name==='手入力'?'':current?.customer_name||'';
  menuOptions(current?.treatment_menu_id||'');
  const m=menus.find(x=>String(x.id)===String(current?.treatment_menu_id||''));
  $('manualTreatmentName').textContent=current?.treatment_menu_name||m?.name||'施術なし';
  $('manualTreatmentAmount').value=String(current?.treatment_amount??0);$('manualAdjustment').value=String(current?.adjustment_amount??0);$('manualMemo').value=current?.memo||'';
  $('manualProducts').querySelectorAll('.qty').forEach(x=>x.value='0');
  if(current){for(const i of manualItems.get(String(current.id))||[]){const row=[...$('manualProducts').querySelectorAll('.productRow')].find(r=>r.dataset.code===i.item_code);if(row)row.querySelector('.qty').value=String(i.quantity||0)}}
  $('manualDelete').classList.toggle('hidden',!current);$('manualSave').textContent=current?'会計を修正して保存':'会計を保存';$('manualSaveMsg').textContent='';$('manualEditor').classList.remove('hidden');recalc();$('manualEditor').scrollIntoView({behavior:'smooth',block:'start'});
}

async function saveManual(){
  const date=$('date')?.value;if(!date)return;$('manualSave').disabled=true;$('manualSaveMsg').textContent='保存しています…';
  const payload={p_sale_date:date,p_customer_name:$('manualCustomerName').value.trim(),p_treatment_amount:Math.max(0,Number($('manualTreatmentAmount').value)||0),p_adjustment_amount:Number($('manualAdjustment').value)||0,p_memo:$('manualMemo').value.trim()||null,p_items:buildItems(),p_treatment_menu_id:$('manualTreatmentMenu').value||null,p_sale_id:current?.id||null};
  const {error}=await supabase.rpc('nakano_admin_save_manual_checkout',payload);$('manualSave').disabled=false;
  if(error){console.error(error);$('manualSaveMsg').textContent='会計を保存できませんでした。';return}
  $('manualSaveMsg').textContent='保存しました。';current=null;await loadManualSales();setTimeout(()=>$('manualEditor').classList.add('hidden'),350);
}
async function deleteManual(){
  if(!current||!confirm('この手入力会計を削除しますか？'))return;
  $('manualDelete').disabled=true;const {error}=await supabase.from('nakano_sales').delete().eq('id',current.id).is('booking_id',null);$('manualDelete').disabled=false;
  if(error){$('manualSaveMsg').textContent='削除できませんでした。';return}
  current=null;$('manualEditor').classList.add('hidden');await loadManualSales();
}

async function boot(){ensureUI();await loadMenus();setTimeout(loadManualSales,500)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
supabase.auth.onAuthStateChange(()=>setTimeout(loadManualSales,120));
