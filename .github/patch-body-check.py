from pathlib import Path

p=Path('index.html')
s=p.read_text()

old_css=""".menuGuide{margin:0 0 12px;border:1px solid #e7e0d7;border-radius:13px;background:#faf8f5;overflow:hidden}
.menuGuide>summary{list-style:none;cursor:pointer;padding:12px 14px;font-size:13px;font-weight:800;color:#4d4843;position:relative;padding-right:38px}
.menuGuide>summary::-webkit-details-marker{display:none}
.menuGuide>summary::after{content:'＋';position:absolute;right:14px;top:50%;transform:translateY(-50%);font-size:17px;color:#827a72}
.menuGuide[open]>summary::after{content:'−'}
.menuGuideBody{padding:0 14px 13px;border-top:1px solid #eee7df;font-size:12px;line-height:1.75;color:#625d57}
.menuGuideItem{padding:9px 0;border-bottom:1px solid #eee7df}
.menuGuideItem:last-child{border-bottom:0;padding-bottom:0}
.menuGuideItem strong{color:#3f3a35}
"""
new_css=""".bodyCheck{margin:0 0 12px;border:1px solid #e7e0d7;border-radius:14px;background:#faf8f5;overflow:hidden}.bodyCheckIntro{padding:14px}.bodyCheckTitle{font-size:15px;font-weight:800;color:#3f3a35}.bodyCheckSub{margin-top:4px;font-size:12px;line-height:1.6;color:#77716a}.bodyCheckStart{width:100%;margin-top:10px;border:1px solid #cfc6bc;border-radius:11px;background:#fff;color:#49443f;padding:11px;font-weight:800}.bodyCheckPanel{padding:14px;border-top:1px solid #eee7df;background:#fff}.bodyCheckQuestion{font-size:14px;font-weight:800;margin-bottom:9px}.bodyCheckChoices{display:grid;grid-template-columns:1fr 1fr;gap:7px}.bodyCheckChoice{border:1px solid #ddd5cc;border-radius:11px;background:#fff;color:#49443f;padding:11px 8px;font-weight:700;text-align:center}.bodyCheckChoice.active{background:#eee7df;border-color:#61574d;box-shadow:0 0 0 1px #61574d inset}.bodyCheckStep{margin-top:14px}.bodyCheckResult{margin-top:14px;padding:14px;border-radius:12px;background:#edf4ee;border:1px solid #cbdccb}.bodyCheckResultLabel{font-size:11px;color:#667266}.bodyCheckResultName{margin-top:3px;font-size:18px;font-weight:800;color:#394439}.bodyCheckReserve{width:100%;margin-top:10px;border:1px solid #61574d;border-radius:12px;background:#61574d;color:#fff;padding:12px;font-weight:800}.bodyCheckNote{margin-top:8px;font-size:10px;line-height:1.5;color:#88817a}@media(max-width:420px){.bodyCheckChoices{grid-template-columns:1fr}}
"""
if old_css not in s: raise SystemExit('old menu guide css not found')
s=s.replace(old_css,new_css,1)

old_html='''<section class="card"><h2><span class="step">1</span>メニューを選択</h2><details class="menuGuide"><summary>どのメニューを選べばいいかわからない方へ</summary><div class="menuGuideBody"><div class="menuGuideItem"><strong>気になるところを短時間で</strong><br>30分コースが目安です。</div><div class="menuGuideItem"><strong>定期的なケア・部分的な疲れ</strong><br>60分コースが目安です。</div><div class="menuGuideItem"><strong>初めての方・全身をしっかりみてほしい</strong><br>90分コースがおすすめです。</div><div class="menuGuideItem"><strong>全身をじっくり整えたい</strong><br>120分コースがおすすめです。</div><div class="menuGuideItem"><strong>頭・目の疲れも気になる</strong><br>ヘッド付きのコースをお選びください。</div></div></details><div id="menus"><span class="muted">メニューを読み込んでいます…</span></div></section>'''
new_html='''<section class="card" id="menuCard"><h2><span class="step">1</span>メニューを選択</h2><div class="bodyCheck" id="bodyCheck"><div class="bodyCheckIntro"><div class="bodyCheckTitle">メニューに迷ったら お体チェック</div><div class="bodyCheckSub">2つの質問から、今のお悩みに合いそうなコースをご案内します。</div><button class="bodyCheckStart" id="bodyCheckStart" type="button">お体チェックをする</button></div><div class="bodyCheckPanel hidden" id="bodyCheckPanel"><div class="bodyCheckQuestion">1. 今いちばん気になるのは？</div><div class="bodyCheckChoices" id="bodyCheckConcern"><button class="bodyCheckChoice" type="button" data-value="part">首・肩・腰など一部</button><button class="bodyCheckChoice" type="button" data-value="whole">全身の疲れ・だるさ</button><button class="bodyCheckChoice" type="button" data-value="head">頭・目・首肩</button><button class="bodyCheckChoice" type="button" data-value="unsure">複数ある・決めにくい</button></div><div class="bodyCheckStep"><div class="bodyCheckQuestion">2. どれくらいしっかり受けたい？</div><div class="bodyCheckChoices" id="bodyCheckDepth"><button class="bodyCheckChoice" type="button" data-value="short">短めに</button><button class="bodyCheckChoice" type="button" data-value="standard">全身を一通り</button><button class="bodyCheckChoice" type="button" data-value="deep">じっくり</button></div></div><div class="bodyCheckResult hidden" id="bodyCheckResult"><div class="bodyCheckResultLabel">おすすめの目安</div><div class="bodyCheckResultName" id="bodyCheckResultName"></div><button class="bodyCheckReserve" id="bodyCheckReserve" type="button">このメニューで予約する</button><div class="bodyCheckNote">これはメニュー選びの目安で、医療上の診断ではありません。</div></div></div></div><div id="menus"><span class="muted">メニューを読み込んでいます…</span></div></section>'''
if old_html not in s: raise SystemExit('old menu guide html not found')
s=s.replace(old_html,new_html,1)

old="""menus.forEach(menu=>{const b=document.createElement('button');b.className='menu';b.innerHTML=`<div><div class=\"menuName\">${esc(menu.name)}</div>${menu.minutes?`<div class=\"menuSub\">${Number(menu.minutes)}分</div>`:''}</div><div class=\"menuPrice\">${yen(menu.price)}</div>`;b.onclick=()=>{if(bookingInProgress)return;document.querySelectorAll('.menu').forEach(x=>x.classList.remove('active'));b.classList.add('active');selectedMenu=menu;selectedTime=null;$('confirmCard').classList.add('hidden');loadSlots()};$('menus').appendChild(b)})"""
new="""menus.forEach(menu=>{const b=document.createElement('button');b.className='menu';b.dataset.menuId=String(menu.id);b.innerHTML=`<div><div class=\"menuName\">${esc(menu.name)}</div>${menu.minutes?`<div class=\"menuSub\">${Number(menu.minutes)}分</div>`:''}</div><div class=\"menuPrice\">${yen(menu.price)}</div>`;b.onclick=()=>{if(bookingInProgress)return;document.querySelectorAll('.menu').forEach(x=>x.classList.remove('active'));b.classList.add('active');selectedMenu=menu;selectedTime=null;$('confirmCard').classList.add('hidden');loadSlots()};$('menus').appendChild(b)})"""
if old not in s: raise SystemExit('menu render target not found')
s=s.replace(old,new,1)

anchor="""$('date').min=todayJapan();$('manageDate').min=todayJapan();$('date').onchange=()=>{selectedTime=null;loadSlots()};
"""
quiz="""let bodyCheckConcern='',bodyCheckDepth='',bodyCheckMenuId='';
function bodyCheckRecommendation(){
  if(!bodyCheckConcern||!bodyCheckDepth)return null;
  if(bodyCheckConcern==='head'){
    if(bodyCheckDepth==='short')return 'head';
    if(bodyCheckDepth==='standard')return 'm60h';
    return 'm90h';
  }
  if(bodyCheckConcern==='part'){
    if(bodyCheckDepth==='short')return 'm30';
    if(bodyCheckDepth==='standard')return 'm60';
    return 'm90';
  }
  if(bodyCheckConcern==='whole'){
    if(bodyCheckDepth==='short')return 'm60';
    if(bodyCheckDepth==='standard')return 'm90';
    return 'm120';
  }
  if(bodyCheckDepth==='short')return 'm60';
  if(bodyCheckDepth==='standard')return 'm90';
  return 'm120';
}
function renderBodyCheckResult(){
  const wanted=bodyCheckRecommendation();
  if(!wanted){$('bodyCheckResult').classList.add('hidden');return}
  let menu=menus.find(m=>String(m.id)===wanted);
  if(!menu&&wanted==='m90h')menu=menus.find(m=>String(m.id)==='m120h')||menus.find(m=>String(m.id)==='m60h');
  if(!menu)return;
  bodyCheckMenuId=String(menu.id);
  $('bodyCheckResultName').textContent=menu.name;
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
bindBodyCheck('bodyCheckConcern','concern');bindBodyCheck('bodyCheckDepth','depth');
$('bodyCheckReserve').onclick=()=>{
  if(!bodyCheckMenuId)return;
  const button=document.querySelector(`.menu[data-menu-id=\"${CSS.escape(bodyCheckMenuId)}\"]`);
  if(button)button.click();
  $('date').scrollIntoView({behavior:'smooth',block:'center'});
  setTimeout(()=>$('date').focus({preventScroll:true}),350);
};

"""
if anchor not in s: raise SystemExit('quiz anchor not found')
s=s.replace(anchor,quiz+anchor,1)

p.write_text(s)
