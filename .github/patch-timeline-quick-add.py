from pathlib import Path

p=Path('admin.html')
s=p.read_text()

# 15-minute plan inputs
s=s.replace('id="blockedStart"\n  step="1800"','id="blockedStart"\n  step="900"',1)
s=s.replace('id="blockedEnd"\n  step="1800"','id="blockedEnd"\n  step="900"',1)

# State
old="""let editingBooking=null;\n\nlet selectedBlockedDates="""
new="""let editingBooking=null;\nlet timelineQuickMinutes=null;\nlet timelinePreferredTime=null;\n\nlet selectedBlockedDates="""
if old not in s:
    raise SystemExit('state anchor not found')
s=s.replace(old,new,1)

# Helpers before timeline section
anchor="""/* ==========================\n   タイムライン\n========================== */\n"""
helpers=r'''function timelineHHMM(minutes){
  const m=Math.max(DAY_START,Math.min(DAY_END,Number(minutes)||DAY_START));
  return `${String(Math.floor(m/60)).padStart(2,'0')}:${String(m%60).padStart(2,'0')}`;
}

function closeTimelineQuickAdd(){
  const overlay=$('timelineQuickAdd');
  if(overlay)overlay.classList.add('hidden');
}

function ensureTimelineQuickAdd(){
  let overlay=$('timelineQuickAdd');
  if(overlay)return overlay;

  overlay=document.createElement('div');
  overlay.id='timelineQuickAdd';
  overlay.className='hidden';
  Object.assign(overlay.style,{
    position:'fixed',inset:'0',zIndex:'9999',background:'rgba(0,0,0,.28)',
    display:'flex',alignItems:'flex-end',justifyContent:'center',padding:'14px'
  });

  const sheet=document.createElement('div');
  Object.assign(sheet.style,{
    width:'100%',maxWidth:'520px',background:'#fff',borderRadius:'18px',padding:'16px',
    boxShadow:'0 16px 40px rgba(0,0,0,.18)'
  });
  sheet.innerHTML=`
    <div style="font-size:12px;color:#77716a">横スケジュールから追加</div>
    <div id="timelineQuickTitle" style="font-size:19px;font-weight:800;margin:4px 0 12px"></div>
    <button class="primary" id="timelineQuickBooking" type="button">新規予約（手入力）</button>
    <button class="secondary" id="timelineQuickPlan" type="button">予定を入れる</button>
    <button class="secondary" id="timelineQuickClose" type="button">閉じる</button>`;
  overlay.appendChild(sheet);
  document.body.appendChild(overlay);

  overlay.addEventListener('click',event=>{
    if(event.target===overlay)closeTimelineQuickAdd();
  });
  $('timelineQuickClose').onclick=closeTimelineQuickAdd;

  $('timelineQuickBooking').onclick=async()=>{
    const date=$('date').value;
    if(!date||timelineQuickMinutes==null)return;
    const hhmm=timelineHHMM(timelineQuickMinutes);
    timelinePreferredTime=`${hhmm}:00`;
    $('adminBookingDate').value=date;
    $('addMsg').textContent=`${hhmm} を選択しました。メニューとお客様を入力してください。`;
    closeTimelineQuickAdd();
    await loadAdminTimes();
    $('adminBookingDate').closest('.card')?.scrollIntoView({behavior:'smooth',block:'start'});
  };

  $('timelineQuickPlan').onclick=()=>{
    const date=$('date').value;
    if(!date||timelineQuickMinutes==null)return;
    const start=timelineQuickMinutes;
    const end=Math.min(DAY_END,start+30);
    $('blockedMonth').value=monthFromDate(date);
    selectedBlockedDates=new Set([date]);
    renderDaySelector();
    $('blockedStart').value=timelineHHMM(start);
    $('blockedEnd').value=timelineHHMM(end);
    $('blockedMsg').textContent=`${timelineHHMM(start)} からの予定を入力できます。`;
    closeTimelineQuickAdd();
    $('blockedStart').closest('.card')?.scrollIntoView({behavior:'smooth',block:'start'});
  };

  return overlay;
}

function openTimelineQuickAdd(minutes){
  timelineQuickMinutes=Math.max(DAY_START,Math.min(DAY_END-15,minutes));
  const overlay=ensureTimelineQuickAdd();
  $('timelineQuickTitle').textContent=`${$('date').value}　${timelineHHMM(timelineQuickMinutes)}`;
  overlay.classList.remove('hidden');
}

'''
if anchor not in s:
    raise SystemExit('timeline anchor not found')
s=s.replace(anchor,helpers+anchor,1)

# Make empty/cell timeline tappable at 15-minute position
old="""    cell.style.width=\n      `${30*PX_PER_MINUTE}px`;\n\n\n    lane.appendChild(\n      cell\n    );"""
new="""    cell.style.width=\n      `${30*PX_PER_MINUTE}px`;\n\n    cell.style.cursor='pointer';\n    cell.onclick=event=>{\n      event.stopPropagation();\n      const quarter=event.offsetX >= (15*PX_PER_MINUTE) ? 15 : 0;\n      openTimelineQuickAdd(min+quarter);\n    };\n\n\n    lane.appendChild(\n      cell\n    );"""
if old not in s:
    raise SystemExit('timeline cell anchor not found')
s=s.replace(old,new,1)

# Existing plan can also open quick add (useful for manual booking over a plan)
old="""      block.innerHTML=`\n\n        <strong>\n          予約不可\n        </strong>\n\n        <br>\n\n        ${esc(item.memo||'')}\n\n      `;\n\n\n      lane.appendChild("""
new="""      block.innerHTML=`\n\n        <strong>\n          予約不可\n        </strong>\n\n        <br>\n\n        ${esc(item.memo||'')}\n\n      `;\n\n      block.style.cursor='pointer';\n      block.onclick=event=>{\n        event.stopPropagation();\n        openTimelineQuickAdd(start);\n      };\n\n\n      lane.appendChild("""
if old not in s:
    raise SystemExit('blocked block anchor not found')
s=s.replace(old,new,1)

# Stop booking click propagation explicitly
old="""      block.onclick=\n      ()=>{\n\n        openEdit(\n          booking\n        );\n      };"""
new="""      block.onclick=\n      event=>{\n        event.stopPropagation();\n        openEdit(\n          booking\n        );\n      };"""
if old not in s:
    raise SystemExit('booking click anchor not found')
s=s.replace(old,new,1)

# Apply preferred timeline time after available buttons have rendered
old="""    button.onclick=()=>{\n      box.value=value;\n      buttonBox.querySelectorAll('.adminTimeButton').forEach(x=>x.classList.toggle('selected',x===button));\n    };\n    buttonBox.appendChild(button);\n  });\n}"""
new="""    button.onclick=()=>{\n      timelinePreferredTime=null;\n      box.value=value;\n      buttonBox.querySelectorAll('.adminTimeButton').forEach(x=>x.classList.toggle('selected',x===button));\n    };\n    buttonBox.appendChild(button);\n  });\n\n  if(timelinePreferredTime){\n    const wanted=String(timelinePreferredTime);\n    const found=(data||[]).some(slot=>String(slot.start_time)===wanted);\n    if(found){\n      box.value=wanted;\n      buttonBox.querySelectorAll('.adminTimeButton').forEach(button=>{\n        button.classList.toggle('selected',button.textContent===wanted.slice(0,5));\n      });\n      $('addMsg').textContent=`${wanted.slice(0,5)} を選択しました。お客様情報を入力してください。`;\n      timelinePreferredTime=null;\n    }else if(menuId){\n      $('addMsg').textContent=`${wanted.slice(0,5)} はこのメニューでは選択できません。別の時間を選ぶかOPEN/CLOSEをご確認ください。`;\n    }\n  }\n}"""
if old not in s:
    raise SystemExit('admin time button anchor not found')
s=s.replace(old,new,1)

p.write_text(s)
