(()=>{
  const CUSTOMER_PAGES=['/','/index.html','/nakano_index_complete.html'];
  const path=location.pathname;
  const isCustomerPage=CUSTOMER_PAGES.some(p=>path.endsWith(p));

  if('serviceWorker' in navigator){
    window.addEventListener('load',()=>{
      navigator.serviceWorker.register('./sw.js',{scope:'./'}).catch(err=>console.warn('PWA registration failed',err));
    },{once:true});
  }

  let installPrompt=null;
  let installCard=null;
  let guide=null;

  const isStandalone=()=>window.matchMedia?.('(display-mode: standalone)').matches===true||window.navigator.standalone===true;
  const ua=navigator.userAgent||'';
  const isIOS=/iPad|iPhone|iPod/.test(ua)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1);
  const openedForInstall=new URL(location.href).searchParams.get('install')==='1';

  function addStyles(){
    if(document.getElementById('nakanoInstallStyle'))return;
    const style=document.createElement('style');
    style.id='nakanoInstallStyle';
    style.textContent=`
      .nakanoInstallCard{margin:10px 0 14px;padding:12px 13px;border:1px solid #ded4ca;border-radius:14px;background:#fffaf5;display:flex;align-items:center;justify-content:space-between;gap:10px;box-shadow:0 2px 8px rgba(69,51,37,.05)}
      .nakanoInstallCopy{min-width:0}.nakanoInstallTitle{font-size:13px;font-weight:800;color:#4b433c}.nakanoInstallSub{margin-top:2px;font-size:11px;line-height:1.5;color:#81776e}
      .nakanoInstallBtn{flex:0 0 auto;width:auto!important;margin:0!important;padding:9px 11px!important;border:1px solid #61574d!important;border-radius:10px!important;background:#61574d!important;color:#fff!important;font-size:12px!important;font-weight:800!important;white-space:nowrap}
      .nakanoInstallGuide{position:fixed;inset:0;z-index:99999;display:flex;align-items:flex-end;justify-content:center;padding:14px;background:rgba(35,31,27,.38)}
      .nakanoInstallGuide.hidden{display:none!important}.nakanoInstallSheet{width:min(520px,100%);padding:18px;border-radius:20px;background:#fff;color:#342f2b;box-shadow:0 16px 50px rgba(0,0,0,.24)}
      .nakanoInstallSheetTitle{font-size:18px;font-weight:900}.nakanoInstallSheetSub{margin-top:5px;color:#77716a;font-size:12px;line-height:1.65}
      .nakanoInstallSteps{display:grid;gap:9px;margin-top:14px}.nakanoInstallStep{display:flex;align-items:flex-start;gap:10px;padding:11px;border-radius:12px;background:#faf8f5;font-size:13px;line-height:1.6}.nakanoInstallNo{display:flex;align-items:center;justify-content:center;flex:0 0 26px;width:26px;height:26px;border-radius:50%;background:#61574d;color:#fff;font-size:12px;font-weight:900}.nakanoInstallShare{font-size:17px;font-weight:900;color:#61574d}.nakanoInstallClose{width:100%;margin-top:13px;padding:12px;border:1px solid #ddd5cc;border-radius:12px;background:#fff;color:#49443f;font:inherit;font-weight:800}
      @media(max-width:380px){.nakanoInstallCard{align-items:flex-start;flex-direction:column}.nakanoInstallBtn{width:100%!important}}
    `;
    document.head.appendChild(style);
  }

  function removeInstallCard(){installCard?.remove();installCard=null}
  function closeGuide(){guide?.classList.add('hidden')}

  function showGuide(){
    if(!guide){
      guide=document.createElement('div');
      guide.className='nakanoInstallGuide hidden';
      guide.innerHTML=`
        <div class="nakanoInstallSheet" role="dialog" aria-modal="true" aria-label="ホーム画面に追加する方法">
          <div class="nakanoInstallSheetTitle">ホーム画面に追加</div>
          <div class="nakanoInstallSheetSub">一度追加すると、次回からアイコンを1回タップするだけで予約画面を開けます。</div>
          <div class="nakanoInstallSteps">
            <div class="nakanoInstallStep"><span class="nakanoInstallNo">1</span><div>${isIOS?'<span class="nakanoInstallShare">□↑</span> 画面下の「共有」ボタンをタップ':'ブラウザ右上のメニューを開く'}</div></div>
            <div class="nakanoInstallStep"><span class="nakanoInstallNo">2</span><div>「ホーム画面に追加」${isIOS?'を選ぶ':'または「アプリをインストール」を選ぶ'}</div></div>
            <div class="nakanoInstallStep"><span class="nakanoInstallNo">3</span><div>「追加」をタップして完了</div></div>
          </div>
          <button type="button" class="nakanoInstallClose">閉じる</button>
        </div>`;
      document.body.appendChild(guide);
      guide.querySelector('.nakanoInstallClose')?.addEventListener('click',closeGuide);
      guide.addEventListener('click',e=>{if(e.target===guide)closeGuide()});
    }
    guide.classList.remove('hidden');
  }

  function openSafariForInstall(){
    const url=new URL(location.href);
    url.searchParams.set('install','1');
    const a=document.createElement('a');
    a.href=url.toString();
    a.target='_blank';
    a.rel='noopener external';
    a.style.display='none';
    document.body.appendChild(a);
    a.click();
    setTimeout(()=>a.remove(),300);
  }

  async function handleInstall(){
    if(isStandalone()){
      openSafariForInstall();
      return;
    }
    if(installPrompt){
      const p=installPrompt;
      installPrompt=null;
      try{
        await p.prompt();
        const choice=await p.userChoice;
        if(choice?.outcome==='accepted')removeInstallCard();
      }catch(err){
        console.warn('PWA install prompt failed',err);
        showGuide();
      }
      return;
    }
    showGuide();
  }

  function createInstallCard(){
    if(!isCustomerPage||installCard)return;
    const anchor=document.querySelector('.header')||document.querySelector('main');
    if(!anchor)return;
    addStyles();
    const standalone=isStandalone();
    const card=document.createElement('div');
    card.className='nakanoInstallCard';
    card.id='nakanoInstallCard';
    card.innerHTML=standalone
      ?`<div class="nakanoInstallCopy"><div class="nakanoInstallTitle">別のホーム画面にも追加できます</div><div class="nakanoInstallSub">Safariで開いて、追加したいホーム画面に登録できます</div></div><button type="button" class="nakanoInstallBtn">Safariで開いて追加</button>`
      :`<div class="nakanoInstallCopy"><div class="nakanoInstallTitle">次回からすぐ予約</div><div class="nakanoInstallSub">ホーム画面に追加すると、アプリのように1タップで開けます</div></div><button type="button" class="nakanoInstallBtn">ホーム画面に追加</button>`;
    card.querySelector('.nakanoInstallBtn')?.addEventListener('click',handleInstall);
    if(anchor.classList?.contains('header'))anchor.insertAdjacentElement('afterend',card);else anchor.prepend(card);
    installCard=card;
  }

  function maybeShowInstallGuideAfterSafariOpen(){
    if(!openedForInstall||isStandalone())return;
    try{
      const url=new URL(location.href);
      url.searchParams.delete('install');
      history.replaceState(null,'',url.pathname+url.search+url.hash);
    }catch{}
    setTimeout(showGuide,180);
  }

  window.addEventListener('beforeinstallprompt',event=>{
    event.preventDefault();
    installPrompt=event;
    createInstallCard();
  });

  window.addEventListener('appinstalled',()=>{
    installPrompt=null;
    if(!isStandalone())removeInstallCard();
    closeGuide();
  });

  window.addEventListener('DOMContentLoaded',()=>{
    createInstallCard();
    maybeShowInstallGuideAfterSafariOpen();
  },{once:true});
  if(document.readyState!=='loading'){
    createInstallCard();
    maybeShowInstallGuideAfterSafariOpen();
  }
})();
