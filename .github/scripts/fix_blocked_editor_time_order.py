from pathlib import Path

p=Path('booking-drag.js')
s=p.read_text()
old="""  const startOpts=quarterTimes().map(t=>`<option value=\"${t.slice(0,5)}\">${t.slice(0,5)}</option>`).join('');
  const endOpts=[...quarterTimes().slice(1).map(t=>t.slice(0,5)),'23:00','23:59'].filter((v,i,a)=>a.indexOf(v)===i).map(t=>`<option value=\"${t}\">${t}</option>`).join('');
"""
new="""  // 予定編集はOPEN/CLOSEの営業時間とは別に、23時まで15分刻みで選べるようにする。
  // これにより22:00〜22:45が抜けて現在値だけ末尾に追加されるiPhone表示崩れを防ぐ。
  const blockedStarts=[];
  for(let n=DAY_START;n<=22*60+45;n+=15)blockedStarts.push(minutesToTime(n).slice(0,5));
  const blockedEnds=[];
  for(let n=DAY_START+15;n<=23*60;n+=15)blockedEnds.push(minutesToTime(n).slice(0,5));
  blockedEnds.push('23:59');
  const startOpts=blockedStarts.map(t=>`<option value=\"${t}\">${t}</option>`).join('');
  const endOpts=blockedEnds.map(t=>`<option value=\"${t}\">${t}</option>`).join('');
"""
if old not in s:
    raise SystemExit('target not found')
p.write_text(s.replace(old,new,1))
