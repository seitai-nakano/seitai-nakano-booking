from pathlib import Path

booking = Path('booking-drag.js')
s = booking.read_text()

repls = [
(
".blockedEditorActions{display:grid;grid-template-columns:1fr 1fr 1fr;gap:7px;margin-top:9px}",
".blockedEditorActions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;margin-top:9px}"
),
(
".blockedDelete{background:#fff;color:#9b4138;border:1px solid #d8aaa5}.blockedEditorMsg",
".blockedDelete{background:#fff;color:#9b4138;border:1px solid #d8aaa5}.blockedBook{background:#edf4ee;color:#526152;border:1px solid #cbdccb}.blockedEditorMsg"
),
(
"予約：本体を下→左右で開始時刻 ／ 右端 ↔ で長さ変更　・　予約不可／予定：タップで時間編集 ／ 長押し→左右で移動",
"予約：本体を下→左右で開始時刻 ／ 右端 ↔ で長さ変更　・　予約不可／予定：タップで編集・削除 ／ 左右ドラッグで時間移動"
),
(
"赤い「予約不可／予定」はタップで時間編集、約0.4秒長押ししてから左右へ動かすと長さを保ったまま15分単位で移動できます。",
"赤い「予約不可／予定」はタップで編集・削除、左右へドラッグすると長さを保ったまま15分単位で移動できます。編集画面の「この時間に新規予約」から、予定を残したまま店側予約を追加できます。"
),
(
"<div class=\"blockedEditorActions\"><button type=\"button\" class=\"blockedSave\" id=\"blockedInlineSave\">保存</button><button type=\"button\" class=\"blockedClose\" id=\"blockedInlineClose\">閉じる</button><button type=\"button\" class=\"blockedDelete\" id=\"blockedInlineDelete\">削除</button></div>",
"<div class=\"blockedEditorActions\"><button type=\"button\" class=\"blockedSave\" id=\"blockedInlineSave\">保存</button><button type=\"button\" class=\"blockedBook\" id=\"blockedInlineBook\">この時間に新規予約</button><button type=\"button\" class=\"blockedClose\" id=\"blockedInlineClose\">閉じる</button><button type=\"button\" class=\"blockedDelete\" id=\"blockedInlineDelete\">削除</button></div>"
),
(
"  $('blockedInlineSave').onclick=saveBlockedEditor;\n  $('blockedInlineDelete').onclick=deleteBlockedEditor;",
"  $('blockedInlineSave').onclick=saveBlockedEditor;\n  $('blockedInlineBook').onclick=bookFromBlockedEditor;\n  $('blockedInlineDelete').onclick=deleteBlockedEditor;"
),
]

for old, new in repls:
    if old not in s:
        raise SystemExit(f'booking-drag target not found: {old[:80]}')
    s = s.replace(old, new, 1)

needle = "async function validateBlockedRange(item,start,end){"
if needle not in s:
    raise SystemExit('validateBlockedRange anchor not found')
insert = """function bookFromBlockedEditor(){
  const ed=$('blockedInlineEditor'),id=ed?.dataset.blockedId;
  if(!id)return;
  const item=blockedRows.find(x=>String(x.id)===String(id));
  if(!item)return;
  const date=item.blocked_date||selectedDate();
  let mins=timeToMinutes(item.start_time);
  if(!Number.isFinite(mins)||mins<DAY_START||mins>LAST_VISIBLE_START)mins=DAY_START;
  const hhmm=minutesToTime(mins).slice(0,5);
  closeBlockedEditor();
  window.dispatchEvent(new CustomEvent('nakano-admin-prefill-booking',{detail:{date,start_time:`${hhmm}:00`,allow_blocked:true}}));
}
"""
s = s.replace(needle, insert + needle, 1)
booking.write_text(s)

blocked = Path('blocked-drag.js')
b = blocked.read_text()
if "touch-action:pan-y;cursor:grab" not in b:
    raise SystemExit('blocked touch-action target not found')
b = b.replace("touch-action:pan-y;cursor:grab", "touch-action:none;cursor:grab", 1)

old = """    originalWidth:parseFloat(el.style.width)||Math.max(36,r.duration*PX_PER_MINUTE),
    interacting:false,ghost:null
  };
}"""
new = """    originalWidth:parseFloat(el.style.width)||Math.max(36,r.duration*PX_PER_MINUTE),
    interacting:false,ghost:null
  };
  // Capture immediately so horizontal schedule scrolling cannot steal a planned-item drag.
  try{el.setPointerCapture(e.pointerId)}catch{}
}"""
if old not in b:
    raise SystemExit('blocked onDown target not found')
b = b.replace(old, new, 1)

blocked.write_text(b)
