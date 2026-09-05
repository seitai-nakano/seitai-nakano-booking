from pathlib import Path

p=Path('booking-drag.js')
s=p.read_text()
old="""  // 予定編集はOPEN/CLOSEの営業時間とは別に、23時まで15分刻みで選べるようにする。\n  // これにより22:00〜22:45が抜けて現在値だけ末尾に追加されるiPhone表示崩れを防ぐ。\n  const blockedStarts=[];\n  for(let n=DAY_START;n<=22*60+45;n+=15)blockedStarts.push(minutesToTime(n).slice(0,5));\n  const blockedEnds=[];\n  for(let n=DAY_START+15;n<=23*60;n+=15)blockedEnds.push(minutesToTime(n).slice(0,5));\n  blockedEnds.push('23:59');\n"""
new="""  // 営業時間は22:00まで。予定編集も通常候補は22:00で打ち止めにする。\n  const blockedStarts=[];\n  for(let n=DAY_START;n<=21*60+45;n+=15)blockedStarts.push(minutesToTime(n).slice(0,5));\n  const blockedEnds=[];\n  for(let n=DAY_START+15;n<=22*60;n+=15)blockedEnds.push(minutesToTime(n).slice(0,5));\n"""
if old not in s:
    raise SystemExit('time option block anchor not found')
s=s.replace(old,new,1)
old2="""  const end=displayEndTime(item.end_time);if(![...$('blockedInlineEnd').options].some(o=>o.value===end)){const o=document.createElement('option');o.value=end;o.textContent=end;$('blockedInlineEnd').appendChild(o)}$('blockedInlineEnd').value=end;\n"""
new2="""  const rawEnd=displayEndTime(item.end_time);\n  const wholeDay=String(item.start_time).startsWith('00:00')&&String(item.end_time).startsWith('23:59');\n  const end=wholeDay?'23:59':(timeToMinutes(rawEnd)>DAY_END?'22:00':rawEnd);\n  if(![...$('blockedInlineEnd').options].some(o=>o.value===end)){const o=document.createElement('option');o.value=end;o.textContent=end;$('blockedInlineEnd').appendChild(o)}\n  $('blockedInlineEnd').value=end;\n"""
if old2 not in s:
    raise SystemExit('open editor end anchor not found')
s=s.replace(old2,new2,1)
old3="""  const date=item.blocked_date||selectedDate(),s=timeToMinutes(start),e=end==='23:59'?24*60:timeToMinutes(end);\n  if(!Number.isFinite(s)||!Number.isFinite(e)||e<=s)return'終了時間は開始時間より後にしてください。';\n"""
new3="""  const date=item.blocked_date||selectedDate(),s=timeToMinutes(start),e=end==='23:59'?24*60:timeToMinutes(end);\n  if(!Number.isFinite(s)||!Number.isFinite(e)||e<=s)return'終了時間は開始時間より後にしてください。';\n  const wholeDay=String(item.start_time).startsWith('00:00')&&String(item.end_time).startsWith('23:59');\n  if(!wholeDay&&e>DAY_END)return'終了時間は22:00までにしてください。';\n"""
if old3 not in s:
    raise SystemExit('validation anchor not found')
s=s.replace(old3,new3,1)
p.write_text(s)
print('patched booking-drag.js')
