from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
s=s.replace('./pwa-register.js?v=20260908-2','./pwa-register.js?v=20260908-3')
p.write_text(s,encoding='utf-8')
print('bumped pwa-register version')
