(()=>{const LOGO='./assets/nakano-logo.png?v=20260816-2';function hero(title,lead,compact=false){const d=document.createElement('div');d.className=`brandHero${compact?' compact':''}`;d.innerHTML=`<div class="brandHeroMain"><img class="brandLogo" src="${LOGO}" alt="整体なかの"><div class="brandCopy"><div class="brandKicker">SEITAI NAKANO</div><h1 class="brandTitle">${title}</h1><p class="brandLead">${lead}</p></div></div>`;return d}function addFooter(){const main=document.querySelector('main');if(!main||document.querySelector('.customerBrandFooter'))return;const f=document.createElement('div');f.className='customerBrandFooter';f.textContent='整体なかの';main.appendChild(f)}function indexBrand(){const h=document.querySelector('header.header');if(!h||h.dataset.branded)return;h.dataset.branded='1';const line=document.getElementById('lineStatus');const top=document.createElement('div');top.className='brandTopBar';top.innerHTML=`<img class="brandTopLogo" src="${LOGO}" alt=""><div class="brandTopText"><div class="brandTopName">整体なかの</div><div class="brandTopMode">ONLINE RESERVATION</div></div>`;const intro=document.createElement('div');intro.className='bookingIntro';intro.innerHTML='<div class="bookingIntroReferral">完全紹介制サロン</div><div class="bookingIntroEyebrow">ONLINE RESERVATION</div><h1 class="bookingIntroTitle">ご予約</h1><p class="bookingIntroLead">ご希望のメニューと日時をお選びください。</p>';h.prepend(intro);h.prepend(top);if(line)h.appendChild(line);const success=document.getElementById('successArea');if(success&&!success.querySelector('.brandMiniLogo')){const img=document.createElement('img');img.className='brandMiniLogo';img.src=LOGO;img.alt='整体なかの';success.prepend(img)}}function karteBrand(){const h=document.querySelector('main>header');if(!h||h.dataset.branded)return;h.dataset.branded='1';const b=hero('初回カルテ','ご来店前に、お身体の状態についてご入力ください。',true);h.replaceWith(b)}function cancelBrand(){const main=document.querySelector('main');if(!main||main.querySelector('.brandHero'))return;main.prepend(hero('予約キャンセル','内容をご確認のうえ、お手続きください。',true))}function runBookingSplash(){
  const splash=document.getElementById('bookingSplash');
  if(!splash)return;
  const p=new URLSearchParams(location.search);
  const skip=p.get('fromcheck')==='1'||p.has('manage');
  const finish=()=>{
    document.body.classList.remove('bookingSplashActive','bookingSplashReveal');
    splash.remove();
  };
  if(skip){
    finish();
    return;
  }
  window.scrollTo({top:0,left:0,behavior:'auto'});
  setTimeout(()=>splash.classList.add('textOut'),3550);
  setTimeout(()=>{
    document.body.classList.add('bookingSplashReveal');
    splash.classList.add('exit');
  },4200);
  setTimeout(finish,4700);
}
function run(){const t=document.title||'';if(t.includes('オンライン予約')){indexBrand();runBookingSplash()}else if(t.includes('初回カルテ'))karteBrand();else if(t.includes('予約キャンセル'))cancelBrand();addFooter()}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run);else run();})();