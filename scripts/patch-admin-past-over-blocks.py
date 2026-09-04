from pathlib import Path
import re

p=Path('admin.html')
s=p.read_text()
pattern=r"async function loadAdminTimes\(\)\{.*?\n\}\n\n\n\$\('menu'\)\.onchange="
repl="""async function loadAdminTimes(){

  const box=$('adminTime');
  const buttonBox=$('adminTimeButtons');
  const previous=box.value;
  const date=$('adminBookingDate').value;
  const menuId=$('menu').value;

  box.innerHTML='<option value=\"\">空き時間を選択</option>';

  if(!date||!menuId){
    if(buttonBox)buttonBox.innerHTML='<div class=\"adminTimeEmpty\">日付とメニューを選択してください。</div>';
    return;
  }

  if(buttonBox)buttonBox.innerHTML='<div class=\"adminTimeEmpty\">時間を読み込んでいます…</div>';

  const {data,error}=await supabase.rpc(
    'nakano_admin_available_slots',
    {p_date:date,p_menu_id:menuId}
  );

  if(error){
    console.error(error);
    if(buttonBox)buttonBox.innerHTML='<div class=\"adminTimeEmpty\">時間を読み込めませんでした。</div>';
    return;
  }

  (data||[]).forEach(slot=>{
    const option=document.createElement('option');
    option.value=slot.start_time;
    option.textContent=String(slot.start_time).slice(0,5);
    box.appendChild(option);
  });

  if(previous&&(data||[]).some(slot=>String(slot.start_time)===String(previous)))box.value=previous;

  if(!buttonBox)return;
  buttonBox.innerHTML='';
  if(!(data||[]).length){
    buttonBox.innerHTML='<div class=\"adminTimeEmpty\">選択できる時間がありません。</div>';
    return;
  }

  (data||[]).forEach(slot=>{
    const value=String(slot.start_time);
    const button=document.createElement('button');
    button.type='button';
    button.className='adminTimeButton'+(box.value===value?' selected':'');
    button.textContent=value.slice(0,5);
    button.onclick=()=>{
      box.value=value;
      buttonBox.querySelectorAll('.adminTimeButton').forEach(x=>x.classList.toggle('selected',x===button));
    };
    buttonBox.appendChild(button);
  });
}


$('menu').onchange="""
ns,n=re.subn(pattern,repl,s,count=1,flags=re.S)
if n!=1:
    raise SystemExit(f'loadAdminTimes patch matches={n}')
p.write_text(ns)
