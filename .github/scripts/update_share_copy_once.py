from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="text:'整体なかののオンライン予約はこちら。メニューに迷ったら、お体チェックからおすすめも選べます。',"
new="text:'完全紹介制で、普段は一般の新規予約を受けていない整体なんだけど、知り合いなら紹介で案内してもらえるみたい。\\n「つらくなってから行く場所」というより、体のことを相談できる場所って感じ。\\nもし合いそうなら、ここから見てみて。',"
if old not in s:
    raise SystemExit('share text marker not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('updated share copy')
