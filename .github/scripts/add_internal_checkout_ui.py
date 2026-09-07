from pathlib import Path
import re

admin=Path('admin.html')
text=admin.read_text()
if './checkout.html' not in text:
    pat=r'(<a class="wide" href="\./analytics\.html">.*?</a>)'
    add='''\n\n<a class="wide" href="./checkout.html">\n<button class="secondary" type="button">\n店舗会計・店販\n</button>\n</a>'''
    text,n=re.subn(pat,lambda m:m.group(1)+add,text,count=1,flags=re.S)
    if n!=1:
        raise SystemExit('admin analytics link anchor not found')
    admin.write_text(text)

analytics=Path('analytics.html')
text=analytics.read_text()
tag='<script type="module" src="./accounting-analytics.js?v=20260908-1"></script>'
if tag not in text:
    if '</body>' not in text:
        raise SystemExit('analytics body anchor not found')
    text=text.replace('</body>',tag+'\n</body>',1)
    analytics.write_text(text)
