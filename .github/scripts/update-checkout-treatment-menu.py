from pathlib import Path
p=Path('checkout.html')
s=p.read_text()

def rep(old,new):
    global s
    if old not in s:
        raise SystemExit('missing target: '+old[:120])
    s=s.replace(old,new,1)

rep('input,textarea,button{font:inherit}input,textarea{width:100%;padding:12px;border:1px solid #e1d9d0;border-radius:11px;background:#fff;color:#2f2d2a}',
    'input,textarea,select,button{font:inherit}input,textarea,select{width:100%;padding:12px;border:1px solid #e1d9d0;border-radius:11px;background:#fff;color:#2f2d2a}')

rep('<label>施術料金</label>\n<div class="moneyRow"><div id="treatmentName" style="font-weight:800">施術</div><input id="treatmentAmount" type="number" inputmode="numeric" min="0" step="10"></div>',
    '<label>実際の施術メニュー</label>\n<select id="treatmentMenu"></select>\n<div id="reservedMenuNote" class="muted" style="margin-top:6px"></div>\n\n<label>施術料金</label>\n<div class="moneyRow"><div id="treatmentName" style="font-weight:800">施術</div><input id="treatmentAmount" type="number" inputmode="numeric" min="0" step="10"></div>')

rep('let bookings=[],salesByBooking=new Map(),itemsBySale=new Map(),currentBooking=null,currentSale=null;',
    'let bookings=[],salesByBooking=new Map(),itemsBySale=new Map(),currentBooking=null,currentSale=null,treatmentMenus=[];')

anchor="""function renderProducts(){
  $('products').innerHTML=PRODUCTS.map(p=>`<div class=\"productRow\" data-code=\"${p.code}\" data-name=\"${p.name}\" data-price=\"${p.price}\"><div><div class=\"productName\">${p.name}</div><div class=\"productPrice\">${yen(p.price)}</div></div><input class=\"qty\" type=\"number\" inputmode=\"numeric\" min=\"0\" step=\"1\" value=\"0\" aria-label=\"${p.name} 数量\"><div class=\"lineAmount\">¥0</div></div>`).join('');
  $('products').querySelectorAll('.qty').forEach(x=>x.addEventListener('input',recalc));
}
"""
insert=anchor+"""async function loadTreatmentMenus(){
  if(treatmentMenus.length)return;
  const {data,error}=await supabase.from('nakano_menus').select('id,name,price,minutes,is_active,display_order').eq('is_active',true).order('display_order');
  if(error){console.error(error);treatmentMenus=[];return}
  treatmentMenus=data||[];
}
function renderTreatmentMenuOptions(selectedId='',fallbackName=''){
  const select=$('treatmentMenu');
  const id=String(selectedId||'');
  const found=treatmentMenus.some(m=>String(m.id)===id);
  const fallback=!found&&id&&fallbackName?`<option value=\"${esc(id)}\">${esc(fallbackName)}</option>`:'';
  select.innerHTML=fallback+treatmentMenus.map(m=>`<option value=\"${esc(m.id)}\">${esc(m.name)}　${yen(m.price)}</option>`).join('');
  if(id)select.value=id;
}
"""
rep(anchor,insert)

rep("select('id,booking_date,start_time,minutes,menu_name,price,customer_name,status')",
    "select('id,booking_date,start_time,minutes,menu_id,menu_name,price,customer_name,status')")

old_open="""  $('bookingSummary').textContent=`${b.booking_date} ${String(b.start_time).slice(0,5)}　${b.customer_name||''}`;
  $('treatmentName').textContent=b.menu_name||'施術';
  $('treatmentAmount').value=String(currentSale?.treatment_amount ?? b.price ?? 0);
"""
new_open="""  $('bookingSummary').textContent=`${b.booking_date} ${String(b.start_time).slice(0,5)}　${b.customer_name||''}`;
  $('reservedMenuNote').textContent=`予約時：${b.menu_name||'施術'} ${yen(b.price)}`;
  const selectedMenuId=String(currentSale?.treatment_menu_id ?? b.menu_id ?? '');
  const selectedMenuName=currentSale?.treatment_menu_name ?? b.menu_name ?? '施術';
  renderTreatmentMenuOptions(selectedMenuId,selectedMenuName);
  const selectedMenu=treatmentMenus.find(m=>String(m.id)===selectedMenuId);
  $('treatmentName').textContent=currentSale?.treatment_menu_name||selectedMenu?.name||b.menu_name||'施術';
  $('treatmentAmount').value=String(currentSale?.treatment_amount ?? selectedMenu?.price ?? b.price ?? 0);
"""
rep(old_open,new_open)

rep("const payload={p_booking_id:currentBooking.id,p_treatment_amount:Math.max(0,Number($('treatmentAmount').value)||0),p_adjustment_amount:Number($('adjustment').value)||0,p_memo:$('memo').value.trim()||null,p_items:buildItems()};",
    "const payload={p_booking_id:currentBooking.id,p_treatment_amount:Math.max(0,Number($('treatmentAmount').value)||0),p_adjustment_amount:Number($('adjustment').value)||0,p_memo:$('memo').value.trim()||null,p_items:buildItems(),p_treatment_menu_id:$('treatmentMenu').value||null};")

rep("renderProducts();$('treatmentAmount').addEventListener('input',recalc);",
    "renderProducts();$('treatmentMenu').addEventListener('change',()=>{const m=treatmentMenus.find(x=>String(x.id)===String($('treatmentMenu').value));if(m){$('treatmentName').textContent=m.name;$('treatmentAmount').value=String(m.price);recalc()}});$('treatmentAmount').addEventListener('input',recalc);")

rep("if(session){if(!$('date').value)$('date').value=todayJapan();await loadDay()}",
    "if(session){if(!$('date').value)$('date').value=todayJapan();await loadTreatmentMenus();await loadDay()}")

p.write_text(s)
