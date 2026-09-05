from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')
pattern = re.compile(
    r"// 既存の一括表示型チェックを、1問ずつ進む会話形式に置き換える。\n"
    r"\$\('bodyCheck'\)\.innerHTML=`.*?\n"
    r"\$\('bodyCheckRestart'\)\.onclick=startBodyCheck;",
    re.S,
)
replacement = r"""// お体チェックは専用ページで実施。予約ページ側は軽い導線だけにする。
$('bodyCheck').innerHTML=`
  <div class="bodyCheckIntro">
    <div class="bodyCheckTitle">メニューに迷ったら お体チェック</div>
    <div class="bodyCheckSub">3つの質問から、今のお体に合いそうなコースをご案内します。</div>
    <a class="bodyCheckStart" href="./body-check.html" style="display:block;text-align:center;text-decoration:none">お体チェックを始める</a>
  </div>`;

// 診断ページから戻った場合は、おすすめされたメニューを一度だけ自動選択する。
function selectRecommendedMenuFromQuery(){
  const url=new URL(location.href);
  const menuId=url.searchParams.get('menu');
  if(!menuId)return;
  const menusRoot=$('menus');
  const select=()=>{
    const button=Array.from(menusRoot.querySelectorAll('.menu')).find(b=>b.dataset.menuId===String(menuId));
    if(!button)return false;
    button.click();
    url.searchParams.delete('menu');
    history.replaceState(null,'',url.pathname+(url.search||'')+(url.hash||''));
    setTimeout(()=>button.scrollIntoView({behavior:'smooth',block:'center'}),120);
    return true;
  };
  if(select())return;
  const observer=new MutationObserver(()=>{if(select())observer.disconnect()});
  observer.observe(menusRoot,{childList:true,subtree:true});
  setTimeout(()=>observer.disconnect(),5000);
}
selectRecommendedMenuFromQuery();"""
new_text, count = pattern.subn(lambda m: replacement, text, count=1)
if count != 1:
    raise SystemExit(f'expected 1 body-check block, found {count}')
path.write_text(new_text, encoding='utf-8')
