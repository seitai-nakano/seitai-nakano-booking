from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='pwa-register.js?v=20260908-3'
new='pwa-register.js?v=20260909-1'
if old not in s:
    raise SystemExit('old PWA version not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('bumped pwa-register version')
