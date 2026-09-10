from pathlib import Path

p = Path('customers.html')
s = p.read_text(encoding='utf-8')

old_css = ".warningBox{padding:12px;border-radius:12px;background:#fff5ef;border:1px solid #ead3c4;font-size:13px;line-height:1.7}.deleteZone{margin-top:20px;padding-top:18px;border-top:1px solid #ebd8d5}@media(max-width:480px)"
new_css = ".warningBox{padding:12px;border-radius:12px;background:#fff5ef;border:1px solid #ead3c4;font-size:13px;line-height:1.7}.mergeCandidateList{margin:8px 0}.mergeCandidate{padding:11px 2px;border-bottom:1px solid #eee7df;cursor:pointer}.mergeCandidate:last-child{border-bottom:0}.mergeCandidateName{font-weight:700}.mergeCandidateMeta{font-size:12px;color:#77716a;margin-top:2px}.mergeCompare{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:8px;margin:12px 0}.mergeBox{padding:11px;border:1px solid #e5ddd4;border-radius:12px;background:#faf8f5}.mergeBoxTitle{font-size:10px;color:#857e77}.mergeBoxName{margin-top:4px;font-weight:700}.mergeBoxMeta{margin-top:3px;font-size:11px;color:#77716a;line-height:1.5}.deleteZone{margin-top:20px;padding-top:18px;border-top:1px solid #ebd8d5}@media(max-width:480px){.mergeCompare{grid-template-columns:1fr}"
if old_css not in s:
    raise SystemExit('CSS anchor not found')
s = s.replace(old_css, new_css, 1)

old_html = "</details><div class=\"deleteZone\"><h3>テスト顧客・不要データ削除</h3>"
new_html = """</details><details class=\"foldSection\" id=\"mergeCustomerSection\"><summary>お客様を統合</summary><div class=\"foldInner\"><div class=\"warningBox\" style=\"margin-top:12px\">重複して登録されたお客様を1人にまとめます。予約・会計・カルテ・身体図は残すお客様へ引き継ぎ、統合される側は非表示になります。</div><label>統合する相手を探す</label><input id=\"mergeSearch\" placeholder=\"名前・ふりがな・電話番号・顧客番号\"><div id=\"mergeCandidateList\" class=\"mergeCandidateList\"><span class=\"muted\">名前や電話番号を入力してください。</span></div><div id=\"mergeSelection\" class=\"hidden\"><div id=\"mergeCompare\" class=\"mergeCompare\"></div><label>どちらのお客様を残すか</label><select id=\"mergeKeepChoice\"></select><button class=\"danger\" id=\"mergeExecute\" type=\"button\">この2人を統合</button><button class=\"secondary\" id=\"mergeCancel\" type=\"button\">選び直す</button></div><div id=\"mergeMsg\" class=\"msg\"></div></div></details><div class=\"deleteZone\"><h3>テスト顧客・不要データ削除</h3>"""
if old_html not in s:
    raise SystemExit('HTML anchor not found')
s = s.replace(old_html, new_html, 1)

old_state = "let customers=[],selectedCustomer=null,currentBookings=[],currentKarte=[],editingKarte=null,currentKana='すべて';"
new_state = "let customers=[],selectedCustomer=null,currentBookings=[],currentKarte=[],editingKarte=null,mergeCandidate=null,currentKana='すべて';"
if old_state not in s:
    raise SystemExit('state anchor not found')
s = s.replace(old_state, new_state, 1)

old_anchor = "$('search').oninput=renderCustomers;\nasync function openCustomer(id)"
merge_js = r'''$('search').oninput=renderCustomers;
function resetMergePanel(){mergeCandidate=null;if($('mergeSearch'))$('mergeSearch').value='';if($('mergeCandidateList'))$('mergeCandidateList').innerHTML='<span class="muted">名前や電話番号を入力してください。</span>';if($('mergeSelection'))$('mergeSelection').classList.add('hidden');if($('mergeCompare'))$('mergeCompare').innerHTML='';if($('mergeKeepChoice'))$('mergeKeepChoice').innerHTML='';if($('mergeMsg'))$('mergeMsg').textContent=''}
function renderMergeCandidates(){if(!selectedCustomer)return;const q=$('mergeSearch').value.trim().toLowerCase(),qd=phoneDigits(q);if(!q){$('mergeCandidateList').innerHTML='<span class="muted">名前や電話番号を入力してください。</span>';return}const f=customers.filter(c=>String(c.id)!==String(selectedCustomer.id)).filter(c=>{const text=[c.customer_name,c.customer_name_kana,c.phone,c.phone_digits,c.customer_no,c.customer_no_display].filter(Boolean).join(' ').toLowerCase();return text.includes(q)||(qd&&phoneDigits(c.phone).includes(qd))}).slice(0,10);$('mergeCandidateList').innerHTML=f.length?f.map(c=>`<div class="mergeCandidate" data-id="${esc(c.id)}"><div class="mergeCandidateName">${esc(c.customer_name)}</div><div class="mergeCandidateMeta">${esc(displayCustomerNo(c))}${c.phone?` / ${esc(c.phone)}`:''}${c.customer_name_kana?` / ${esc(c.customer_name_kana)}`:''}</div></div>`).join(''):'<span class="muted">該当するお客様はいません。</span>';document.querySelectorAll('#mergeCandidateList .mergeCandidate').forEach(x=>x.onclick=()=>selectMergeCandidate(x.dataset.id))}
function selectMergeCandidate(id){mergeCandidate=customers.find(c=>String(c.id)===String(id))||null;if(!mergeCandidate)return;const a=selectedCustomer,b=mergeCandidate;$('mergeCompare').innerHTML=`<div class="mergeBox"><div class="mergeBoxTitle">現在開いているお客様</div><div class="mergeBoxName">${esc(a.customer_name)}</div><div class="mergeBoxMeta">${esc(displayCustomerNo(a))}<br>${esc(a.phone||'電話番号なし')}</div></div><div class="mergeBox"><div class="mergeBoxTitle">統合する相手</div><div class="mergeBoxName">${esc(b.customer_name)}</div><div class="mergeBoxMeta">${esc(displayCustomerNo(b))}<br>${esc(b.phone||'電話番号なし')}</div></div>`;$('mergeKeepChoice').innerHTML=`<option value="current">${esc(a.customer_name)}（${esc(displayCustomerNo(a)||'現在の顧客')}）を残す</option><option value="other">${esc(b.customer_name)}（${esc(displayCustomerNo(b)||'選択した顧客')}）を残す</option>`;$('mergeSelection').classList.remove('hidden');$('mergeCandidateList').innerHTML='<span class="muted">統合相手を選択しました。</span>';$('mergeMsg').textContent=''}
$('mergeSearch').oninput=renderMergeCandidates;$('mergeCancel').onclick=resetMergePanel;$('mergeExecute').onclick=async()=>{if(!selectedCustomer||!mergeCandidate)return;const keepCurrent=$('mergeKeepChoice').value==='current',keep=keepCurrent?selectedCustomer:mergeCandidate,merge=keepCurrent?mergeCandidate:selectedCustomer;const text=`残すお客様：${keep.customer_name} ${displayCustomerNo(keep)}\n統合するお客様：${merge.customer_name} ${displayCustomerNo(merge)}\n\n予約・会計・カルテ・身体図をまとめます。よろしいですか？`;if(!confirm(text))return;if(prompt('確認のため「統合」と入力してください。')!=='統合')return;$('mergeExecute').disabled=true;$('mergeMsg').textContent='統合しています…';const{data,error}=await supabase.rpc('nakano_admin_merge_customers',{p_keep_customer_id:keep.id,p_merge_customer_id:merge.id});$('mergeExecute').disabled=false;if(error){console.error(error);$('mergeMsg').textContent='統合できませんでした。内容を確認してください。';return}await loadCustomers();await openCustomer(keep.id);const d=data||{};$('customerMsg').textContent=`お客様を統合しました。予約 ${Number(d.bookings_moved)||0}件、施術記録 ${Number(d.karte_moved)||0}件、身体図 ${Number(d.body_charts_moved)||0}件をまとめました。`};
async function openCustomer(id)'''
if old_anchor not in s:
    raise SystemExit('JS anchor not found')
s = s.replace(old_anchor, merge_js, 1)

old_open = "async function openCustomer(id){selectedCustomer=customers.find(x=>String(x.id)===String(id));if(!selectedCustomer)return;$('customerCard').classList.remove('hidden');$('newCustomerCard').classList.add('hidden');$('karteEditor').classList.add('hidden');fillCustomerForm();"
new_open = "async function openCustomer(id){selectedCustomer=customers.find(x=>String(x.id)===String(id));if(!selectedCustomer)return;$('customerCard').classList.remove('hidden');$('newCustomerCard').classList.add('hidden');$('karteEditor').classList.add('hidden');resetMergePanel();fillCustomerForm();"
if old_open not in s:
    raise SystemExit('openCustomer anchor not found')
s = s.replace(old_open, new_open, 1)

p.write_text(s, encoding='utf-8')
print('customers.html patched')
