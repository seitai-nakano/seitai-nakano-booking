from pathlib import Path
import re

# admin.html: pass selected customer id into admin booking RPC
p = Path('admin.html')
s = p.read_text()
old = """    p_customer_name:\n      $('customerName')\n        .value\n        .trim(),\n\n    p_phone:"""
new = """    p_customer_name:\n      $('customerName')\n        .value\n        .trim(),\n\n    p_customer_id:\n      $('customerSelect').value\n      ||\n      null,\n\n    p_phone:"""
if old not in s:
    raise SystemExit('admin payload target not found')
s = s.replace(old, new, 1)
p.write_text(s)

# customers.html: add manual merge button to booking history and handler
p = Path('customers.html')
s = p.read_text()
old = '<details class="foldSection"><summary>予約履歴</summary><div class="foldInner"><div id="bookingHistory"></div></div></details>'
new = '<details class="foldSection"><summary>予約履歴</summary><div class="foldInner"><div id="bookingHistory"></div><button class="secondary" id="mergeUnlinkedBookings" type="button">未統合の手入力予約をこの顧客にまとめる</button><div id="mergeBookingMsg" class="msg"></div></div></details>'
if old not in s:
    raise SystemExit('customers booking history target not found')
s = s.replace(old, new, 1)

anchor = "async function loadKarte(){"
handler = """$('mergeUnlinkedBookings').onclick=async()=>{if(!selectedCustomer)return;if(!confirm(`${selectedCustomer.customer_name}さんと同じ名前の未統合手入力予約を、この顧客の予約履歴にまとめますか？`))return;$('mergeBookingMsg').textContent='統合しています…';const{data,error}=await supabase.rpc('nakano_admin_merge_unlinked_bookings',{p_customer_id:selectedCustomer.id});if(error){console.error(error);$('mergeBookingMsg').textContent='統合できませんでした。';return}const count=Number(data)||0;$('mergeBookingMsg').textContent=count?`${count}件の手入力予約を統合しました。`:'統合できる未統合予約はありませんでした。';await loadBookingHistory()};\n"""
if anchor not in s:
    raise SystemExit('customers handler anchor not found')
s = s.replace(anchor, handler + anchor, 1)
p.write_text(s)
