from pathlib import Path

p=Path('index.html')
s=p.read_text()

old="""function phoneIsValid(v){const d=v.replace(/\\D/g,'');return d.length===10||d.length===11}\nfunction setLatestManage(t){"""
new="""function phoneIsValid(v){const d=v.replace(/\\D/g,'');return d.length===10||d.length===11}\nconst CUSTOMER_PROFILE_KEY='nakano_customer_profile_v1';\nlet customerInfoTouched=false;\n$('name').addEventListener('input',()=>{customerInfoTouched=true});\n$('tel').addEventListener('input',()=>{customerInfoTouched=true});\nfunction saveCustomerProfile(name,tel){\n  if(!name||!phoneIsValid(tel))return;\n  try{localStorage.setItem(CUSTOMER_PROFILE_KEY,JSON.stringify({name,tel}))}catch{}\n}\nfunction loadSavedCustomerProfile(){\n  if(customerInfoTouched)return false;\n  try{\n    const v=JSON.parse(localStorage.getItem(CUSTOMER_PROFILE_KEY)||'null');\n    if(!v?.name||!phoneIsValid(String(v.tel||'')))return false;\n    $('name').value=String(v.name);\n    $('tel').value=String(v.tel);\n    return true;\n  }catch{return false}\n}\nasync function fillCustomerProfileFromLine(userId){\n  if(!userId||customerInfoTouched)return false;\n  try{\n    const{data,error}=await supabase.rpc('nakano_customer_prefill_by_line',{p_line_user_id:userId});\n    if(error)throw error;\n    if(!data?.customer_name||!phoneIsValid(String(data.phone||'')))return false;\n    if(customerInfoTouched)return false;\n    $('name').value=String(data.customer_name);\n    $('tel').value=String(data.phone);\n    saveCustomerProfile(String(data.customer_name),String(data.phone));\n    return true;\n  }catch(e){console.warn('前回のお客様情報を読み込めませんでした',e);return false}\n}\nfunction setLatestManage(t){"""
if old not in s:
    raise SystemExit('profile helper anchor not found')
s=s.replace(old,new,1)

old="""const p=await liff.getProfile();lineUser={userId:p.userId,displayName:p.displayName||''};$('lineStatus').textContent='LINEで予約完了のお知らせを受け取れます。';return lineUser}catch(e){console.error(e);$('lineStatus').textContent='オンライン予約をご利用いただけます。';return null}}"""
new="""const p=await liff.getProfile();lineUser={userId:p.userId,displayName:p.displayName||''};$('lineStatus').textContent='LINEで予約完了のお知らせを受け取れます。';const filled=await fillCustomerProfileFromLine(lineUser.userId);if(!filled)loadSavedCustomerProfile();return lineUser}catch(e){console.error(e);$('lineStatus').textContent='オンライン予約をご利用いただけます。';loadSavedCustomerProfile();return null}}"""
if old not in s:
    raise SystemExit('initLine anchor not found')
s=s.replace(old,new,1)

old="""    $('successArea').dataset.bookingId=String(bookingId||'');\n    $('successDetail').innerHTML=summaryHtml(["""
new="""    saveCustomerProfile(name,tel);\n    $('successArea').dataset.bookingId=String(bookingId||'');\n    $('successDetail').innerHTML=summaryHtml(["""
if old not in s:
    raise SystemExit('booking success anchor not found')
s=s.replace(old,new,1)

old="""$('newBooking').onclick=()=>{selectedMenu=null;selectedTime=null;$('name').value='';$('tel').value='';$('memo').value='';$('date').value='';"""
new="""$('newBooking').onclick=()=>{selectedMenu=null;selectedTime=null;$('memo').value='';$('date').value='';"""
if old not in s:
    raise SystemExit('new booking reset anchor not found')
s=s.replace(old,new,1)

old="""<section class=\"card\"><h2><span class=\"step\">4</span>お客様情報</h2><label>お名前"""
new="""<section class=\"card\"><h2><span class=\"step\">4</span>お客様情報</h2><p class=\"muted\">2回目以降は、前回のお名前・電話番号を自動で表示します。</p><label>お名前"""
if old not in s:
    raise SystemExit('customer info ui anchor not found')
s=s.replace(old,new,1)

p.write_text(s)
