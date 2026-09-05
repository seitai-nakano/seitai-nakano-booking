from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

css='''\n/* conversational body check */\n.bodyCheckChat{display:grid;gap:10px;margin-bottom:12px}\n.bodyCheckBubble{max-width:88%;padding:10px 12px;border-radius:14px;font-size:13px;line-height:1.65}\n.bodyCheckBubble.guide{justify-self:start;background:#f2eee9;color:#49443f;border:1px solid #e3dbd2;border-bottom-left-radius:5px}\n.bodyCheckBubble.user{justify-self:end;background:#61574d;color:#fff;border-bottom-right-radius:5px}\n.bodyCheckSpeaker{font-size:10px;font-weight:800;color:#827a72;margin:0 0 4px 2px}\n.bodyCheckProgress{font-size:11px;color:#8b837b;margin-bottom:8px}\n.bodyCheckQuestionNow{font-size:15px;font-weight:800;line-height:1.55;color:#3f3a35;margin-bottom:10px}\n.bodyCheckAnswerList{display:grid;gap:7px}\n.bodyCheckAnswer{width:100%;border:1px solid #d8d0c7;border-radius:11px;background:#fff;color:#49443f;padding:11px 12px;font-weight:700;text-align:left}\n.bodyCheckAnswer:active{background:#f3eee8}\n.bodyCheckAnalyzing{padding:16px 12px;text-align:center;border-radius:12px;background:#faf8f5;color:#625c56;font-size:13px;line-height:1.7}\n.bodyCheckDots{display:inline-flex;gap:4px;margin-right:7px;vertical-align:middle}\n.bodyCheckDots i{display:block;width:5px;height:5px;border-radius:50%;background:#776e66;animation:bodyCheckDot 1s infinite ease-in-out}\n.bodyCheckDots i:nth-child(2){animation-delay:.15s}.bodyCheckDots i:nth-child(3){animation-delay:.3s}\n@keyframes bodyCheckDot{0%,60%,100%{opacity:.25;transform:translateY(0)}30%{opacity:1;transform:translateY(-2px)}}\n.bodyCheckResultSummary{margin:8px 0 12px;padding:11px 12px;border-radius:11px;background:#fff;border:1px solid #d8e2d8;font-size:12px;line-height:1.7;color:#536053}\n.bodyCheckRestart{width:100%;margin-top:10px;border:0;background:transparent;color:#77716a;text-decoration:underline;font-size:12px;padding:7px}\n'''
if '/* conversational body check */' not in s:
    s=s.replace('</style>',css+'\n</style>',1)

new_js=r'''let bodyCheckConcern='',bodyCheckSeverity='',bodyCheckDepth='',bodyCheckStepIndex=0;
const bodyCheckAnswers=[];
const bodyCheckQuestions=[
  {
    key:'concern',
    text:'今、いちばん気になっているのはどれですか？',
    options:[
      ['part','首・肩・腰など一部がつらい'],
      ['whole','全身の疲れ・だるさ'],
      ['head','頭・目・首肩がつらい'],
      ['unsure','いくつか気になる・決めにくい']
    ]
  },
  {
    key:'severity',
    text:'つらさは今、どのくらいですか？',
    options:[
      ['mild','少し気になる程度'],
      ['ongoing','ずっと続いている・繰り返す'],
      ['strong','かなりつらい・しっかりケアしたい']
    ]
  },
  {
    key:'depth',
    text:'今日はどれくらいしっかり受けたいですか？',
    options:[
      ['short','短めに整えたい'],
      ['standard','全身を一通りみてほしい'],
      ['deep','時間をかけてじっくり受けたい']
    ]
  }
];

function bodyCheckRecommendations(){
  if(!bodyCheckConcern||!bodyCheckSeverity||!bodyCheckDepth)return [];

  // 「じっくり」は全ケースでヘッド付き、120分＋ヘッドを最優先。
  if(bodyCheckDepth==='deep')return ['m120h','m90h','m60h'];

  // 「全身を一通り」は全ケースでヘッド付き。
  if(bodyCheckDepth==='standard'){
    if(bodyCheckConcern==='head'){
      return bodyCheckSeverity==='strong'
        ? ['m90h','m120h','m60h']
        : ['m60h','m90h','m120h'];
    }
    if(bodyCheckConcern==='whole'||bodyCheckConcern==='unsure'||bodyCheckSeverity==='strong'){
      return ['m90h','m120h','m60h'];
    }
    return ['m60h','m90h','m120h'];
  }

  // 短め希望は症状とつらさで順番を調整。
  if(bodyCheckConcern==='head'){
    return bodyCheckSeverity==='strong'
      ? ['m60h','m90h','head']
      : ['head','m60h','m90h'];
  }
  if(bodyCheckConcern==='part'){
    return bodyCheckSeverity==='strong'
      ? ['m60','m90','m30']
      : ['m30','m60','m90'];
  }
  if(bodyCheckConcern==='whole'||bodyCheckConcern==='unsure'){
    return bodyCheckSeverity==='strong'
      ? ['m90','m60','m120']
      : ['m60','m90','m30'];
  }
  return ['m60','m90','m30'];
}

function bodyCheckSummaryText(){
  const c={part:'部分的なつらさ',whole:'全身の疲れ・だるさ',head:'頭・目・首肩のつらさ',unsure:'複数のお悩み'}[bodyCheckConcern]||'今のお悩み';
  const s={mild:'軽めのつらさ',ongoing:'続いているつらさ',strong:'強めのつらさ'}[bodyCheckSeverity]||'';
  const d={short:'短めのケア',standard:'全身を一通り',deep:'じっくりしたケア'}[bodyCheckDepth]||'';
  return `${c}・${s}・${d}という回答から、受けやすさと施術範囲のバランスで候補を選びました。`;
}

function chooseBodyCheckMenu(menuId){
  const button=document.querySelector(`.menu[data-menu-id="${CSS.escape(String(menuId))}"]`);
  if(button)button.click();
  $('date').scrollIntoView({behavior:'smooth',block:'center'});
  setTimeout(()=>$('date').focus({preventScroll:true}),350);
}

function bodyCheckMenuNameFromId(id){
  return menus.find(m=>String(m.id)===String(id));
}

function renderBodyCheckResult(){
  const ids=bodyCheckRecommendations();
  const seen=new Set(),recommended=[];
  for(const id of ids){
    const menu=bodyCheckMenuNameFromId(id);
    if(menu&&!seen.has(String(menu.id))){
      seen.add(String(menu.id));
      recommended.push(menu);
    }
  }
  if(!recommended.length){
    setTimeout(renderBodyCheckResult,120);
    return;
  }
  $('bodyCheckAnalyzing').classList.add('hidden');
  const result=$('bodyCheckResult');
  $('bodyCheckResultSummary').textContent=bodyCheckSummaryText();
  const list=$('bodyCheckResultList');
  list.innerHTML='';
  recommended.slice(0,3).forEach((menu,index)=>{
    const item=document.createElement('div');
    item.className='bodyCheckResultItem';
    item.innerHTML=`<div class="bodyCheckResultTop"><div><div class="bodyCheckRank">おすすめ${index+1}</div><div class="bodyCheckResultItemName">${esc(menu.name)}</div></div><div class="bodyCheckResultPrice">${yen(menu.price)}</div></div><button class="bodyCheckReserve" type="button">このメニューで予約する</button>`;
    item.querySelector('.bodyCheckReserve').onclick=()=>chooseBodyCheckMenu(menu.id);
    list.appendChild(item);
  });
  result.classList.remove('hidden');
}

function bodyCheckAddBubble(kind,text,speaker=''){
  const chat=$('bodyCheckChat');
  const wrap=document.createElement('div');
  if(speaker){
    const sp=document.createElement('div');
    sp.className='bodyCheckSpeaker';
    sp.textContent=speaker;
    chat.appendChild(sp);
  }
  wrap.className=`bodyCheckBubble ${kind}`;
  wrap.textContent=text;
  chat.appendChild(wrap);
  wrap.scrollIntoView({behavior:'smooth',block:'nearest'});
}

function showBodyCheckQuestion(index){
  bodyCheckStepIndex=index;
  const q=bodyCheckQuestions[index];
  if(!q){
    $('bodyCheckQuestionArea').classList.add('hidden');
    $('bodyCheckAnalyzing').classList.remove('hidden');
    setTimeout(renderBodyCheckResult,650);
    return;
  }
  const area=$('bodyCheckQuestionArea');
  area.classList.remove('hidden');
  area.innerHTML=`<div class="bodyCheckProgress">${index+1} / ${bodyCheckQuestions.length}</div><div class="bodyCheckQuestionNow">${esc(q.text)}</div><div class="bodyCheckAnswerList"></div>`;
  const list=area.querySelector('.bodyCheckAnswerList');
  q.options.forEach(([value,label])=>{
    const b=document.createElement('button');
    b.type='button';
    b.className='bodyCheckAnswer';
    b.textContent=label;
    b.onclick=()=>{
      if(q.key==='concern')bodyCheckConcern=value;
      if(q.key==='severity')bodyCheckSeverity=value;
      if(q.key==='depth')bodyCheckDepth=value;
      bodyCheckAnswers[index]=label;
      bodyCheckAddBubble('user',label);
      area.classList.add('hidden');
      setTimeout(()=>{
        if(index+1<bodyCheckQuestions.length){
          bodyCheckAddBubble('guide',bodyCheckQuestions[index+1].text,'お体チェック');
        }
        showBodyCheckQuestion(index+1);
      },220);
    };
    list.appendChild(b);
  });
}

function startBodyCheck(){
  bodyCheckConcern='';bodyCheckSeverity='';bodyCheckDepth='';bodyCheckStepIndex=0;
  bodyCheckAnswers.length=0;
  $('bodyCheckResult').classList.add('hidden');
  $('bodyCheckAnalyzing').classList.add('hidden');
  $('bodyCheckChat').innerHTML='';
  $('bodyCheckPanel').classList.remove('hidden');
  $('bodyCheckStart').textContent='最初からやり直す';
  bodyCheckAddBubble('guide','いくつか質問します。今のお体に近いものを選んでください。','お体チェック');
  setTimeout(()=>{
    bodyCheckAddBubble('guide',bodyCheckQuestions[0].text,'お体チェック');
    showBodyCheckQuestion(0);
  },180);
}

// 既存の一括表示型チェックを、1問ずつ進む会話形式に置き換える。
$('bodyCheck').innerHTML=`
  <div class="bodyCheckIntro">
    <div class="bodyCheckTitle">メニューに迷ったら お体チェック</div>
    <div class="bodyCheckSub">質問に答えると、今のお悩みに合いそうなメニューをおすすめ順にご案内します。</div>
    <button class="bodyCheckStart" id="bodyCheckStart" type="button">お体チェックを始める</button>
  </div>
  <div class="bodyCheckPanel hidden" id="bodyCheckPanel">
    <div class="bodyCheckChat" id="bodyCheckChat"></div>
    <div id="bodyCheckQuestionArea"></div>
    <div class="bodyCheckAnalyzing hidden" id="bodyCheckAnalyzing"><span class="bodyCheckDots"><i></i><i></i><i></i></span>回答内容からおすすめを選んでいます…</div>
    <div class="bodyCheckResult hidden" id="bodyCheckResult">
      <div class="bodyCheckResultLabel">あなたへのおすすめ候補</div>
      <div class="bodyCheckResultSummary" id="bodyCheckResultSummary"></div>
      <div class="bodyCheckResultList" id="bodyCheckResultList"></div>
      <div class="bodyCheckNote">メニュー選びのための自動チェックです。医療上の診断ではありません。</div>
      <button class="bodyCheckRestart" id="bodyCheckRestart" type="button">もう一度チェックする</button>
    </div>
  </div>`;
$('bodyCheckStart').onclick=startBodyCheck;
$('bodyCheckRestart').onclick=startBodyCheck;

'''

pattern=r"let bodyCheckConcern='',bodyCheckDepth='';.*?(?=\$\('date'\)\.min=)"
if not re.search(pattern,s,flags=re.S):
    raise SystemExit('body check JS block not found')
s=re.sub(pattern,new_js,s,count=1,flags=re.S)

p.write_text(s,encoding='utf-8')
