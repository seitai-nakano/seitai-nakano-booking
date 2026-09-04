from pathlib import Path

p=Path('admin.html')
s=p.read_text()

old='''<label>予約時間</label>\n\n<select id="adminTime">\n<option value="">\n空き時間を選択\n</option>\n</select>'''
new='''<label>予約時間</label>\n\n<select id="adminTime" class="adminTimeSelect" aria-label="予約時間">\n<option value="">\n空き時間を選択\n</option>\n</select>\n<div id="adminTimeButtons" class="adminTimeButtons" aria-label="空き時間一覧"></div>\n<div class="muted adminTimeHelp">空いている時間をタップしてください。</div>'''
if s.count(old)!=1: raise SystemExit('time select html mismatch')
s=s.replace(old,new,1)

old='''<label>電話番号</label>\n<input\n  id="phone"\n  inputmode="tel"\n>'''
new='''<label>電話番号 <span class="muted" style="font-weight:400">（任意）</span></label>\n<input\n  id="phone"\n  inputmode="tel"\n  placeholder="不明なら空欄でOK"\n>'''
if s.count(old)!=1: raise SystemExit('phone html mismatch')
s=s.replace(old,new,1)

css_anchor='''.customerBox{\n  margin-bottom:12px;\n  padding:12px;\n  border-radius:13px;\n  background:#faf8f5\n}\n'''
css_add='''.customerBox{\n  margin-bottom:12px;\n  padding:12px;\n  border-radius:13px;\n  background:#faf8f5\n}\n\n.adminTimeSelect{position:absolute!important;width:1px!important;height:1px!important;opacity:0!important;pointer-events:none!important;margin:0!important;padding:0!important}\n.adminTimeButtons{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px;max-height:280px;overflow-y:auto;-webkit-overflow-scrolling:touch;margin:7px 0 5px;padding:2px}\n.adminTimeButton{min-width:0;min-height:46px;padding:9px 3px;border:1px solid #ddd5cc;border-radius:11px;background:#fff;color:#49443f;font-size:14px;font-weight:800}\n.adminTimeButton.selected{border-color:#61574d;background:#61574d;color:#fff}\n.adminTimeButton:active{transform:scale(.98)}\n.adminTimeEmpty{grid-column:1/-1;padding:12px;border-radius:11px;background:#faf8f5;color:#817a73;font-size:12px;text-align:center}\n.adminTimeHelp{margin:0 0 10px!important;font-size:11px!important}\n@media(max-width:420px){.adminTimeButtons{grid-template-columns:repeat(3,minmax(0,1fr));max-height:300px}.adminTimeButton{min-height:48px;font-size:15px}}\n'''
if s.count(css_anchor)!=1: raise SystemExit('css anchor mismatch')
s=s.replace(css_anchor,css_add,1)

old='''async function loadAdminTimes(){\n\n  const box=\n    $('adminTime');\n\n\n  box.innerHTML=\n    '<option value="">空き時間を選択</option>';\n\n\n  const data=\n    await getAvailableTimes(\n      $('menu').value,\n      $('adminBookingDate').value\n    );\n\n\n  data.forEach(\n    slot=>{\n\n      const option=\n        document.createElement(\n          'option'\n        );\n\n\n      option.value=\n        slot.start_time;\n\n\n      option.textContent=\n        String(\n          slot.start_time\n        )\n        .slice(\n          0,\n          5\n        );\n\n\n      box.appendChild(\n        option\n      );\n    }\n  );\n}'''
new='''async function loadAdminTimes(){\n\n  const box=$('adminTime');\n  const buttonBox=$('adminTimeButtons');\n  const previous=box.value;\n\n  box.innerHTML='<option value="">空き時間を選択</option>';\n  if(buttonBox)buttonBox.innerHTML='<div class="adminTimeEmpty">空き時間を読み込んでいます…</div>';\n\n  const data=await getAvailableTimes(\n    $('menu').value,\n    $('adminBookingDate').value\n  );\n\n  data.forEach(slot=>{\n    const option=document.createElement('option');\n    option.value=slot.start_time;\n    option.textContent=String(slot.start_time).slice(0,5);\n    box.appendChild(option);\n  });\n\n  if(previous&&data.some(slot=>String(slot.start_time)===String(previous)))box.value=previous;\n\n  if(!buttonBox)return;\n  buttonBox.innerHTML='';\n  if(!data.length){\n    buttonBox.innerHTML='<div class="adminTimeEmpty">選択できる空き時間がありません。</div>';\n    return;\n  }\n\n  data.forEach(slot=>{\n    const value=String(slot.start_time);\n    const button=document.createElement('button');\n    button.type='button';\n    button.className='adminTimeButton'+(box.value===value?' selected':'');\n    button.textContent=value.slice(0,5);\n    button.onclick=()=>{\n      box.value=value;\n      buttonBox.querySelectorAll('.adminTimeButton').forEach(x=>x.classList.toggle('selected',x===button));\n    };\n    buttonBox.appendChild(button);\n  });\n}'''
if s.count(old)!=1: raise SystemExit('loadAdminTimes mismatch')
s=s.replace(old,new,1)

old="""    ||\n    !payload.p_customer_name\n    ||\n    !payload.p_phone\n  ){\n\n    $('addMsg').textContent=\n      '日付・時間・メニュー・お名前・電話番号を入力してください。';"""
new="""    ||\n    !payload.p_customer_name\n  ){\n\n    $('addMsg').textContent=\n      '日付・時間・メニュー・お名前を入力してください。';"""
if s.count(old)!=1: raise SystemExit('add validation mismatch')
s=s.replace(old,new,1)

old="""  const {error}=\n    await supabase.rpc(\n      'nakano_create_booking',\n      payload\n    );"""
new="""  const {data:bookingId,error}=\n    await supabase.rpc(\n      'nakano_admin_create_booking',\n      payload\n    );"""
if s.count(old)!=1: raise SystemExit('admin rpc mismatch')
s=s.replace(old,new,1)

old="""  $('customerSelect').value='';\n  $('customerName').value='';\n  $('phone').value='';\n  $('memo').value='';\n\n\n  await loadCustomers();\n\n  await loadDay();\n\n  await loadAdminTimes();"""
new="""  const bookedDate=payload.p_date;\n  $('date').value=bookedDate;\n  $('month').value=monthFromDate(bookedDate);\n  $('blockedMonth').value=monthFromDate(bookedDate);\n  $('adminBookingDate').value=bookedDate;\n\n  $('customerSelect').value='';\n  $('customerName').value='';\n  $('phone').value='';\n  $('memo').value='';\n  $('adminTime').value='';\n\n  await loadCustomers();\n  await loadDay();\n  await loadAdminTimes();\n  if(typeof window.refreshMonthlyBookings==='function')await window.refreshMonthlyBookings();\n  if(typeof window.refreshAdminBookingCalendar==='function')await window.refreshAdminBookingCalendar(bookedDate);\n  $('scheduleMsg').textContent=bookingId?'予約を反映しました。':'';\n  setTimeout(()=>{if($('scheduleMsg').textContent==='予約を反映しました。')$('scheduleMsg').textContent=''},1800);"""
if s.count(old)!=1: raise SystemExit('post add refresh mismatch')
s=s.replace(old,new,1)

# Allow blank phone when editing an admin-created booking too.
old="""    ||\n    !payload.p_customer_name\n    ||\n    !payload.p_phone\n  ){\n\n    $('editMsg').textContent="""
new="""    ||\n    !payload.p_customer_name\n  ){\n\n    $('editMsg').textContent="""
if s.count(old)!=1: raise SystemExit('edit validation mismatch')
s=s.replace(old,new,1)

p.write_text(s)

p=Path('booking-drag.js')
s=p.read_text()
anchor="""setTimeout(()=>{scrollToCurrentTime(true);improveAdminLayout();enhanceQuarterTimes();addQuarterGuides();installQuarterBulkControls();refreshQuarterUI();loadMonthlyBookings();hydrateBlockedBlocks(true)},520);"""
replacement=anchor+"\nwindow.refreshMonthlyBookings=loadMonthlyBookings;"
if s.count(anchor)!=1: raise SystemExit('booking-drag expose anchor mismatch')
s=s.replace(anchor,replacement,1)
p.write_text(s)

p=Path('admin-booking-calendar.js')
s=p.read_text()
anchor="""setTimeout(start,650);"""
replacement="""window.refreshAdminBookingCalendar=async(date)=>{\n  const month=monthFromDate(date)||viewMonth||currentJapanMonth();\n  await loadMonth(month);\n};\n\nsetTimeout(start,650);"""
if s.count(anchor)!=1: raise SystemExit('calendar expose anchor mismatch')
s=s.replace(anchor,replacement,1)
p.write_text(s)
