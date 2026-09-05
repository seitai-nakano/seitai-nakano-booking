from pathlib import Path
import re

p=Path('index.html')
s=p.read_text()

old_html='''<div class="bodyCheckResult hidden" id="bodyCheckResult"><div class="bodyCheckResultLabel">おすすめの目安</div><div class="bodyCheckResultName" id="bodyCheckResultName"></div><button class="bodyCheckReserve" id="bodyCheckReserve" type="button">このメニューで予約する</button><div class="bodyCheckNote">これはメニュー選びの目安で、医療上の診断ではありません。</div></div>'''
new_html='''<div class="bodyCheckResult hidden" id="bodyCheckResult"><div class="bodyCheckResultLabel">今のお悩みに合いそうなメニュー</div><div class="bodyCheckResultList" id="bodyCheckResultList"></div><div class="bodyCheckNote">おすすめ順の目安です。気になるメニューを選んでそのまま予約できます。医療上の診断ではありません。</div></div>'''
if old_html not in s:
    raise SystemExit('body check result HTML marker not found')
s=s.replace(old_html,new_html,1)

css='''
.bodyCheckResultList{display:grid;gap:9px;margin-top:10px}
.bodyCheckResultItem{padding:12px;border:1px solid #d8e2d8;border-radius:12px;background:#fff}
.bodyCheckResultTop{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
.bodyCheckRank{font-size:10px;font-weight:800;color:#667266}
.bodyCheckResultItemName{margin-top:2px;font-size:16px;font-weight:800;color:#394439}
.bodyCheckResultPrice{font-size:14px;font-weight:800;color:#4c584c;white-space:nowrap;padding-top:14px}
.bodyCheckResultItem .bodyCheckReserve{margin-top:9px}
'''
if '.bodyCheckResultList{' not in s:
    s=s.replace('</style>',css+'\n</style>',1)

new_js=r'''let bodyCheckConcern='',bodyCheckDepth='';
function bodyCheckRecommendations(){
  if(!bodyCheckConcern||!bodyCheckDepth)return [];
  const table={
    head:{
      short:['head','m60h','m90h'],
      standard:['m60h','m90h','head'],
      deep:['m90h','m120h','m60h']
    },
    part:{
      short:['m30','m60','m90'],
      standard:['m60','m90','m30'],
      deep:['m90','m120','m60']
    },
    whole:{
      short:['m60','m90','m120'],
      standard:['m90','m120','m60'],
      deep:['m120','m90','m60']
    },
    unsure:{
      short:['m60','m90','m30'],
      standard:['m90','m60','m120'],
      deep:['m120','m90','m60']
    }
  };
  return table[bodyCheckConcern]?.[bodyCheckDepth]||[];
}
function chooseBodyCheckMenu(menuId){
  const button=document.querySelector(`.menu[data-menu-id="${CSS.escape(String(menuId))}"]`);
  if(button)button.click();
  $('date').scrollIntoView({behavior:'smooth',block:'center'});
  setTimeout(()=>$('date').focus({preventScroll:true}),350);
}
function renderBodyCheckResult(){
  const ids=bodyCheckRecommendations();
  if(!ids.length){$('bodyCheckResult').classList.add('hidden');return}
  const seen=new Set(),recommended=[];
  for(const id of ids){
    const menu=menus.find(m=>String(m.id)===String(id));
    if(menu&&!seen.has(String(menu.id))){seen.add(String(menu.id));recommended.push(menu)}
  }
  if(!recommended.length){$('bodyCheckResult').classList.add('hidden');return}
  const list=$('bodyCheckResultList');
  list.innerHTML='';
  recommended.slice(0,3).forEach((menu,index)=>{
    const item=document.createElement('div');
    item.className='bodyCheckResultItem';
    item.innerHTML=`<div class="bodyCheckResultTop"><div><div class="bodyCheckRank">おすすめ${index+1}</div><div class="bodyCheckResultItemName">${esc(menu.name)}</div></div><div class="bodyCheckResultPrice">${yen(menu.price)}</div></div><button class="bodyCheckReserve" type="button">このメニューで予約する</button>`;
    item.querySelector('.bodyCheckReserve').onclick=()=>chooseBodyCheckMenu(menu.id);
    list.appendChild(item);
  });
  $('bodyCheckResult').classList.remove('hidden');
}
$('bodyCheckStart').onclick=()=>{$('bodyCheckPanel').classList.toggle('hidden')};
function bindBodyCheck(groupId,key){
  $(groupId).querySelectorAll('.bodyCheckChoice').forEach(b=>b.onclick=()=>{
    $(groupId).querySelectorAll('.bodyCheckChoice').forEach(x=>x.classList.toggle('active',x===b));
    if(key==='concern')bodyCheckConcern=b.dataset.value;else bodyCheckDepth=b.dataset.value;
    renderBodyCheckResult();
  });
}
bindBodyCheck('bodyCheckConcern','concern');bindBodyCheck('bodyCheckDepth','depth');'''

pat=r"let bodyCheckConcern='',bodyCheckDepth='',bodyCheckMenuId='';.*?\n\n\$\('date'\)\.min="
m=re.search(pat,s,re.S)
if not m:
    raise SystemExit('body check JS block marker not found')
s=s[:m.start()]+new_js+"\n\n$('date').min="+s[m.end():]

p.write_text(s)
print('patched multiple body-check recommendations')
