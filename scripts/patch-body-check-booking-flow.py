from pathlib import Path

repo = Path('.')
index = repo / 'index.html'
check = repo / 'body-check.html'

idx = index.read_text(encoding='utf-8')
old = '''    button.click();
    url.searchParams.delete('menu');
    history.replaceState(null,'',url.pathname+(url.search||'')+(url.hash||''));
    setTimeout(()=>button.scrollIntoView({behavior:'smooth',block:'center'}),120);
    return true;'''
new = '''    button.click();
    const fromCheck=url.searchParams.get('fromcheck')==='1';
    url.searchParams.delete('menu');
    url.searchParams.delete('fromcheck');
    history.replaceState(null,'',url.pathname+(url.search||''));
    setTimeout(()=>{
      if(fromCheck){
        $('date').scrollIntoView({behavior:'smooth',block:'center'});
      }else{
        button.scrollIntoView({behavior:'smooth',block:'center'});
      }
    },160);
    return true;'''
if old not in idx:
    raise SystemExit('index target not found')
idx = idx.replace(old, new, 1)
index.write_text(idx, encoding='utf-8')

html = check.read_text(encoding='utf-8')
old_href = '''<a class="reserve" href="./?menu=${encodeURIComponent(m.id)}#menuCard">このメニューで予約する</a>'''
new_href = '''<a class="reserve" href="./?menu=${encodeURIComponent(m.id)}&fromcheck=1#date">このメニューで予約へ進む</a>'''
if old_href not in html:
    raise SystemExit('body-check target not found')
html = html.replace(old_href, new_href, 1)
check.write_text(html, encoding='utf-8')
