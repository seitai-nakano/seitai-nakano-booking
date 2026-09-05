from pathlib import Path

p=Path('index.html')
s=p.read_text()

css_anchor='</style>'
css='''
.menuGuide{margin:0 0 12px;border:1px solid #e7e0d7;border-radius:13px;background:#faf8f5;overflow:hidden}
.menuGuide>summary{list-style:none;cursor:pointer;padding:12px 14px;font-size:13px;font-weight:800;color:#4d4843;position:relative;padding-right:38px}
.menuGuide>summary::-webkit-details-marker{display:none}
.menuGuide>summary::after{content:'＋';position:absolute;right:14px;top:50%;transform:translateY(-50%);font-size:17px;color:#827a72}
.menuGuide[open]>summary::after{content:'−'}
.menuGuideBody{padding:0 14px 13px;border-top:1px solid #eee7df;font-size:12px;line-height:1.75;color:#625d57}
.menuGuideItem{padding:9px 0;border-bottom:1px solid #eee7df}
.menuGuideItem:last-child{border-bottom:0;padding-bottom:0}
.menuGuideItem strong{color:#3f3a35}
'''
if '.menuGuide{' not in s:
    if css_anchor not in s: raise SystemExit('style end not found')
    s=s.replace(css_anchor,css+css_anchor,1)

old='<section class="card"><h2><span class="step">1</span>メニューを選択</h2><div id="menus">'
new='''<section class="card"><h2><span class="step">1</span>メニューを選択</h2><details class="menuGuide"><summary>どのメニューを選べばいいかわからない方へ</summary><div class="menuGuideBody"><div class="menuGuideItem"><strong>気になるところを短時間で</strong><br>30分コースが目安です。</div><div class="menuGuideItem"><strong>定期的なケア・部分的な疲れ</strong><br>60分コースが目安です。</div><div class="menuGuideItem"><strong>初めての方・全身をしっかりみてほしい</strong><br>90分コースがおすすめです。</div><div class="menuGuideItem"><strong>全身をじっくり整えたい</strong><br>120分コースがおすすめです。</div><div class="menuGuideItem"><strong>頭・目の疲れも気になる</strong><br>ヘッド付きのコースをお選びください。</div></div></details><div id="menus">'''
if old not in s:
    raise SystemExit('menu section target not found')
s=s.replace(old,new,1)

p.write_text(s)
