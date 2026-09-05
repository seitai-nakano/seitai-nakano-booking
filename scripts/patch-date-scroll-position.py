from pathlib import Path

p=Path('index.html')
s=p.read_text()
old="""      if(fromCheck){
        $('date').scrollIntoView({behavior:'smooth',block:'center'});
      }else{
        button.scrollIntoView({behavior:'smooth',block:'center'});
      }
"""
new="""      if(fromCheck){
        const dateCard=$('date').closest('.card');
        const target=dateCard||$('date');
        const top=target.getBoundingClientRect().top+window.scrollY-12;
        window.scrollTo({top,behavior:'smooth'});
      }else{
        button.scrollIntoView({behavior:'smooth',block:'center'});
      }
"""
if old not in s:
    raise SystemExit('target snippet not found')
p.write_text(s.replace(old,new,1))
