from pathlib import Path


def replace_one(text, old, new, label):
    if old not in text:
        raise SystemExit(f'{label}: target not found')
    return text.replace(old, new, 1)

# --- admin.html ---
p=Path('admin.html')
s=p.read_text()

s=replace_one(
    s,
    "      block.className=\n        'blockedSchedule';",
    "      block.className=\n        'blockedSchedule';\n\n      block.dataset.blockedId=\n        String(item.id);",
    'admin blocked id'
)

s=replace_one(
    s,
    "      block.style.cursor='pointer';\n      block.onclick=event=>{\n        event.stopPropagation();\n        openTimelineQuickAdd(start);\n      };",
    "      block.style.cursor='grab';\n      block.title='タップで予定を変更・削除／左右ドラッグで時間変更';",
    'admin blocked click conflict'
)

marker="""/* ==========================\n   タイムライン\n========================== */"""
listener="""window.addEventListener('nakano-admin-prefill-booking',async event=>{\n  const detail=event.detail||{};\n  const date=String(detail.date||$('date').value||'');\n  const hhmm=String(detail.start_time||detail.startTime||'').slice(0,5);\n  if(!date||!/^\\d{2}:\\d{2}$/.test(hhmm))return;\n\n  timelinePreferredTime=`${hhmm}:00`;\n  $('adminBookingDate').value=date;\n  $('addMsg').textContent=`${hhmm} を選択しました。メニューとお客様を入力してください。`;\n  closeTimelineQuickAdd();\n  await loadAdminTimes();\n  $('adminBookingDate').closest('.card')?.scrollIntoView({behavior:'smooth',block:'start'});\n});\n\n\n"""
if listener not in s:
    s=replace_one(s,marker,listener+marker,'admin prefill listener')

p.write_text(s)

# --- booking-drag.js ---
p=Path('booking-drag.js')
s=p.read_text()

s=s.replace(
    ".blockedEditorActions{display:grid;grid-template-columns:1fr 1fr 1fr;gap:7px;margin-top:9px}",
    ".blockedEditorActions{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:9px}"
)
s=s.replace(
    ".blockedDelete{background:#fff;color:#9b4138;border:1px solid #d8aaa5}",
    ".blockedDelete{background:#fff;color:#9b4138;border:1px solid #d8aaa5}.blockedBook{background:#fff7ef;color:#7a4d2f;border:1px solid #d9b99f}"
)

old_html="""<div class=\"blockedEditorActions\"><button type=\"button\" class=\"blockedSave\" id=\"blockedInlineSave\">保存</button><button type=\"button\" class=\"blockedClose\" id=\"blockedInlineClose\">閉じる</button><button type=\"button\" class=\"blockedDelete\" id=\"blockedInlineDelete\">削除</button></div>"""
new_html="""<div class=\"blockedEditorActions\"><button type=\"button\" class=\"blockedSave\" id=\"blockedInlineSave\">変更を保存</button><button type=\"button\" class=\"blockedBook\" id=\"blockedInlineBook\">この時間から新規予約</button><button type=\"button\" class=\"blockedDelete\" id=\"blockedInlineDelete\">予定を削除</button><button type=\"button\" class=\"blockedClose\" id=\"blockedInlineClose\">閉じる</button></div>"""
s=replace_one(s,old_html,new_html,'blocked editor buttons')

s=replace_one(
    s,
    "  $('blockedInlineSave').onclick=saveBlockedEditor;\n  $('blockedInlineDelete').onclick=deleteBlockedEditor;",
    "  $('blockedInlineSave').onclick=saveBlockedEditor;\n  $('blockedInlineBook').onclick=bookBlockedAsBooking;\n  $('blockedInlineDelete').onclick=deleteBlockedEditor;",
    'blocked editor handlers'
)

book_fn="""function bookBlockedAsBooking(){\n  const ed=$('blockedInlineEditor'),id=ed?.dataset.blockedId;\n  if(!id)return;\n  const item=blockedRows.find(x=>String(x.id)===String(id));\n  if(!item)return;\n  const date=ed.dataset.blockedDate||item.blocked_date||selectedDate();\n  const start=String($('blockedInlineStart')?.value||item.start_time||'').slice(0,5);\n  closeBlockedEditor();\n  window.dispatchEvent(new CustomEvent('nakano-admin-prefill-booking',{detail:{date,start_time:start,blocked_id:id}}));\n}\n\n"""
if 'function bookBlockedAsBooking()' not in s:
    s=replace_one(s,'async function deleteBlockedEditor(){',book_fn+'async function deleteBlockedEditor(){','book over blocked function')

s=s.replace(
    '予約不可／予定：タップで時間編集 ／ 長押し→左右で移動',
    '予約不可／予定：タップで変更・削除 ／ 左右ドラッグで時間移動'
)
s=s.replace(
    '赤い「予約不可／予定」はタップで時間編集、約0.4秒長押ししてから左右へ動かすと長さを保ったまま15分単位で移動できます。',
    '赤い「予約不可／予定」はタップで変更・削除、左右へドラッグすると長さを保ったまま15分単位で移動できます。予定編集から同じ時間に店側の新規予約も追加できます。'
)
s=s.replace("h.textContent='タップで時間変更'","h.textContent='タップで編集・左右ドラッグで移動'")
s=s.replace("タップで変更`;","タップで編集／左右ドラッグで移動`;" )

p.write_text(s)

# --- blocked-drag.js ---
p=Path('blocked-drag.js')
s=p.read_text()

s=s.replace("const LONG_PRESS_MS=430;\nconst CANCEL_DISTANCE=10;","const DRAG_START_DISTANCE=5;")
s=s.replace(
    ".blockedSchedule,.blockedBlock{-webkit-touch-callout:none;touch-action:pan-x}",
    ".blockedSchedule,.blockedBlock{-webkit-touch-callout:none;touch-action:pan-y;cursor:grab}"
)

old_down="""function onDown(e,el,item){\n  if(drag||(e.pointerType==='mouse'&&e.button!==0))return;\n  const scroll=el.closest('.timelineScroll,.scheduleScroll');\n  if(!scroll||!movable(item))return;\n  const r=range(item);\n  drag={\n    el,item,scroll,pointerId:e.pointerId,\n    startX:e.clientX,startY:e.clientY,currentX:e.clientX,currentY:e.clientY,\n    startScrollLeft:scroll.scrollLeft,\n    originalStart:r.start,newStart:r.start,duration:r.duration,\n    originalLeft:parseFloat(el.style.left)||((r.start-DAY_START)*PX_PER_MINUTE),\n    originalWidth:parseFloat(el.style.width)||Math.max(36,r.duration*PX_PER_MINUTE),\n    interacting:false,ghost:null\n  };\n  clearTimeout(pressTimer);\n  pressTimer=setTimeout(startDrag,LONG_PRESS_MS);\n}\n"""
new_down="""function onDown(e,el,item){\n  if(drag||(e.pointerType==='mouse'&&e.button!==0))return;\n  const scroll=el.closest('.timelineScroll,.scheduleScroll');\n  if(!scroll||!movable(item))return;\n  const r=range(item);\n  drag={\n    el,item,scroll,pointerId:e.pointerId,\n    startX:e.clientX,startY:e.clientY,currentX:e.clientX,currentY:e.clientY,\n    startScrollLeft:scroll.scrollLeft,\n    originalStart:r.start,newStart:r.start,duration:r.duration,\n    originalLeft:parseFloat(el.style.left)||((r.start-DAY_START)*PX_PER_MINUTE),\n    originalWidth:parseFloat(el.style.width)||Math.max(36,r.duration*PX_PER_MINUTE),\n    interacting:false,ghost:null\n  };\n}\n"""
s=replace_one(s,old_down,new_down,'blocked pointerdown')

old_move="""function onMove(e){\n  const s=drag;if(!s||s.pointerId!==e.pointerId)return;\n  s.currentX=e.clientX;s.currentY=e.clientY;\n  if(!s.interacting){\n    if(Math.hypot(s.currentX-s.startX,s.currentY-s.startY)>CANCEL_DISTANCE){\n      clearTimeout(pressTimer);pressTimer=null;drag=null;\n    }\n    return;\n  }\n  e.preventDefault();updateVisual();\n}\n"""
new_move="""function onMove(e){\n  const s=drag;if(!s||s.pointerId!==e.pointerId)return;\n  s.currentX=e.clientX;s.currentY=e.clientY;\n  if(!s.interacting){\n    const dx=s.currentX-s.startX,dy=s.currentY-s.startY;\n    if(Math.hypot(dx,dy)<DRAG_START_DISTANCE)return;\n    if(Math.abs(dy)>Math.abs(dx)*1.25){drag=null;return}\n    startDrag();\n    if(!drag?.interacting)return;\n  }\n  e.preventDefault();updateVisual();\n}\n"""
s=replace_one(s,old_move,new_move,'blocked pointermove')

s=s.replace("if(hint)hint.textContent='タップで編集・長押しで移動';","if(hint)hint.textContent='タップで編集・左右ドラッグで移動';")
s=s.replace("タップで編集／長押しで移動`;","タップで編集／左右ドラッグで移動`;" )

p.write_text(s)
