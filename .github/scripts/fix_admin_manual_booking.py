from pathlib import Path

path = Path('admin.html')
s = path.read_text(encoding='utf-8')

old = '''<label>予約時間</label>

<select id="adminTime" class="adminTimeSelect" aria-label="予約時間">
<option value="">
空き時間を選択
</option>
</select>
<div id="adminTimeButtons" class="adminTimeButtons" aria-label="空き時間一覧"></div>
<div class="muted adminTimeHelp">空いている時間をタップしてください。</div>'''
new = '''<label>予約時間</label>
<input
  type="time"
  id="adminTimeManual"
  step="900"
>
<div class="muted adminTimeHelp">15分単位で直接指定できます。下の候補をタップしても入力されます。</div>

<select id="adminTime" class="adminTimeSelect" aria-label="予約時間候補">
<option value="">
空き時間を選択
</option>
</select>
<div id="adminTimeButtons" class="adminTimeButtons" aria-label="空き時間一覧"></div>
<div class="muted adminTimeHelp">候補はOPEN枠から表示しています。</div>'''
if old not in s:
    raise SystemExit('reservation time HTML anchor not found')
s = s.replace(old, new, 1)

old = '''  const box=$('adminTime');
  const buttonBox=$('adminTimeButtons');
  const previous=box.value;
  const date=$('adminBookingDate').value;
  const menuId=$('menu').value;

  box.innerHTML='<option value="">空き時間を選択</option>';'''
new = '''  const box=$('adminTime');
  const manual=$('adminTimeManual');
  const buttonBox=$('adminTimeButtons');
  const previous=box.value;
  const date=$('adminBookingDate').value;
  const menuId=$('menu').value;

  box.innerHTML='<option value="">空き時間を選択</option>';

  // 「この時間から新規予約」で渡された時刻は、候補RPCの成否に関係なく
  // 管理者の直接入力欄へ先に保持する。
  if(timelinePreferredTime&&manual){
    manual.value=String(timelinePreferredTime).slice(0,5);
  }'''
if old not in s:
    raise SystemExit('loadAdminTimes anchor not found')
s = s.replace(old, new, 1)

old = '''    button.onclick=()=>{
      timelinePreferredTime=null;
      box.value=value;
      buttonBox.querySelectorAll('.adminTimeButton').forEach(x=>x.classList.toggle('selected',x===button));
    };'''
new = '''    button.onclick=()=>{
      timelinePreferredTime=null;
      box.value=value;
      if(manual)manual.value=value.slice(0,5);
      buttonBox.querySelectorAll('.adminTimeButton').forEach(x=>x.classList.toggle('selected',x===button));
    };'''
if old not in s:
    raise SystemExit('time button anchor not found')
s = s.replace(old, new, 1)

old = '''    if(found){
      box.value=wanted;
      buttonBox.querySelectorAll('.adminTimeButton').forEach(button=>{'''
new = '''    if(found){
      box.value=wanted;
      if(manual)manual.value=wanted.slice(0,5);
      buttonBox.querySelectorAll('.adminTimeButton').forEach(button=>{'''
if old not in s:
    raise SystemExit('preferred time anchor not found')
s = s.replace(old, new, 1)

old = '''    p_start_time:
      $('adminTime').value,'''
new = '''    p_start_time:
      $('adminTimeManual').value
      ?
      `${$('adminTimeManual').value}:00`
      :
      $('adminTime').value,'''
if old not in s:
    raise SystemExit('payload time anchor not found')
s = s.replace(old, new, 1)

old = '''    $('addMsg').textContent=
      '予約を追加できませんでした。';'''
new = '''    const raw=String(error?.message||'');
    let friendly='予約を追加できませんでした。';

    if(raw.includes('CLOSE')){
      friendly='この時間はCLOSEです。OPENにしてから予約してください。';
    }
    else if(raw.includes('別の予約')||raw.includes('already been booked')){
      friendly='すでに別の予約が入っている時間です。';
    }
    else if(raw.includes('15分')){
      friendly='予約時間は15分単位で指定してください。';
    }
    else if(raw.includes('22:00')||raw.includes('22時')){
      friendly='22:00までに終了する時間を指定してください。';
    }
    else if(raw.includes('管理者ログイン')){
      friendly='ログイン状態が切れています。管理画面を開き直してログインしてください。';
    }
    else if(raw.includes('電話番号')){
      friendly='電話番号を確認してください。';
    }

    $('addMsg').textContent=friendly;'''
if old not in s:
    raise SystemExit('error message anchor not found')
s = s.replace(old, new, 1)

old = '''  $('memo').value='';
  $('adminTime').value='';'''
new = '''  $('memo').value='';
  $('adminTime').value='';
  $('adminTimeManual').value='';'''
if old not in s:
    raise SystemExit('success clear anchor not found')
s = s.replace(old, new, 1)

# Give immediate feedback when the administrator types a manual time.
anchor = "$('adminBookingDate').onchange=\nloadAdminTimes;\n"
insert = """$('adminBookingDate').onchange=\nloadAdminTimes;\n\n\n$('adminTimeManual').onchange=\n()=>{\n  const value=$('adminTimeManual').value;\n  if(!value)return;\n  timelinePreferredTime=null;\n  const candidate=`${value}:00`;\n  const box=$('adminTime');\n  if([...box.options].some(option=>option.value===candidate)){\n    box.value=candidate;\n    $('adminTimeButtons').querySelectorAll('.adminTimeButton').forEach(button=>{\n      button.classList.toggle('selected',button.textContent===value);\n    });\n  }\n  else{\n    box.value='';\n    $('adminTimeButtons').querySelectorAll('.adminTimeButton').forEach(button=>button.classList.remove('selected'));\n  }\n};\n"""
if anchor not in s:
    raise SystemExit('manual time event anchor not found')
s = s.replace(anchor, insert, 1)

# Marker for deployment/debugging without exposing technical details in the UI.
s = s.replace('<title>整体なかの｜管理トップ</title>', '<title>整体なかの｜管理トップ</title>\n<meta name="nakano-admin-build" content="2026-09-05-manual-booking-v2">', 1)

path.write_text(s, encoding='utf-8')
print('patched admin manual booking')
